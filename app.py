"""Web server per le giornate LBA e LNP A2 e l'esportazione Excel."""
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

from a2_tabellini import date_iso, read_boxscore
from excel_export import make_xlsx
from lba_tabellini import fetch_game
from euroleague_tabellini import games_for_round, game_from_schedule
from eurocup_tabellini import games_for_round as eurocup_games_for_round, game_from_schedule as eurocup_game_from_schedule

ROOT = Path(__file__).parent
HTML = (ROOT / 'index.html').read_bytes()
CALENDAR = json.loads((ROOT / 'calendar.json').read_text())
A2_CALENDAR = json.loads((ROOT / 'a2_calendar.json').read_text())
CACHE = {}
LOCK = threading.Lock()


def match_status(match):
    code = str(match.get('game_status', ''))
    return {'0': 'DA GIOCARE', '1': 'IN CORSO', '2': 'TERMINATA'}.get(code, 'STATO NON NOTO')


def fetch_match(game_id):
    url = f'https://www.legabasket.it/api/championships/get-championships-matches-by-id?id={game_id}'
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=25) as response:
        return json.load(response)['match']


def score_data(match):
    status = match_status(match)
    if status not in ('IN CORSO', 'TERMINATA'):
        return '', []
    score = f"{match.get('home_final_score', 0)} - {match.get('visitor_final_score', 0)}"
    periods = []
    current = int(match.get('quarter') or 0)
    if status == 'TERMINATA':
        current = 4
    for n in range(1, min(current, 4) + 1):
        periods.append({'name': f'{n}°Q', 'home': match.get(f'q{n}_hs', 0),
                        'away': match.get(f'q{n}_vs', 0)})
    if match.get('ot_hs') or match.get('ot_vs'):
        periods.append({'name': 'OT', 'home': match.get('ot_hs', 0), 'away': match.get('ot_vs', 0)})
    if status == 'IN CORSO' and periods:
        home = sum(int(p['home'] or 0) for p in periods)
        away = sum(int(p['away'] or 0) for p in periods)
        if home or away:
            score = f'{home} - {away}'
    return score, periods


def load_game(item):
    result = dict(item)
    try:
        match = fetch_match(item['id'])
        status = match_status(match)
        score, periods = score_data(match)
        players = fetch_game(str(item['id']))['players'] if status in ('IN CORSO', 'TERMINATA') else []
        result.update(status=status, datetime=match.get('match_datetime') or '',
                      score=score, periods=periods, quarter=match.get('quarter') or '',
                      players=players, error='')
    except Exception as exc:
        result.update(status='DATI NON DISPONIBILI', datetime='', score='', periods=[], quarter='', players=[], error=str(exc))
    return result


def get_lba_day(day):
    with LOCK:
        cached = CACHE.get(('lba', day))
        if cached and time.monotonic() - cached[0] < (10 if any(g['status'] == 'IN CORSO' for g in cached[1]['games']) else 60):
            return cached[1]
    with ThreadPoolExecutor(max_workers=8) as pool:
        games = list(pool.map(load_game, CALENDAR[day]))
    result = {'day': int(day), 'games': games}
    with LOCK:
        CACHE[('lba', day)] = (time.monotonic(), result)
    return result


def get_lba_scores(day):
    def refresh(item):
        match = fetch_match(item['id'])
        score, periods = score_data(match)
        return {'id': item['id'], 'status': match_status(match), 'score': score,
                'periods': periods, 'quarter': match.get('quarter') or '',
                'datetime': match.get('match_datetime') or ''}
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(refresh, CALENDAR[day]))


def a2_status(code):
    code = str(code or '').lower()
    if code == 'finished':
        return 'TERMINATA'
    if code == 'ready':
        return 'DA GIOCARE'
    if code in ('live', 'started', 'playing', 'in_progress', 'ongoing', 'running'):
        return 'IN CORSO'
    return 'STATO NON NOTO'


def a2_schedule(day):
    url = f'https://lnpstat.domino.it/getstatisticsfiles?task=schedule&year=x2627&league=ita2&round={day}'
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=25) as response:
        rows = json.load(response)
    by_id = {r['gameid']: r for r in rows}
    expected = A2_CALENDAR[day]
    if len(rows) != len(expected) or set(by_id) != set(expected):
        raise ValueError('Il calendario A2 non corrisponde ai link forniti.')
    return [by_id[game_id] for game_id in expected]


def a2_game(row, day, with_players=True):
    status = a2_status(row.get('game_status'))
    game = {'id': row['gameid'], 'home': row.get('teamname_home') or 'Casa',
            'away': row.get('teamname_away') or 'Ospite', 'status': status,
            'datetime': date_iso(row.get('date'), row.get('time')),
            'score': '', 'periods': [], 'quarter': '', 'players': [], 'error': ''}
    if status in ('IN CORSO', 'TERMINATA'):
        if row.get('score_home') is not None and row.get('score_away') is not None:
            game['score'] = f"{row['score_home']} - {row['score_away']}"
        if with_players or status == 'IN CORSO':
            try:
                box = read_boxscore(game['id'], game['home'], game['away'], int(day), game['datetime'], allow_empty=status == 'IN CORSO')
                game['periods'] = box['periods']
                game['quarter'] = len(box['periods'])
                game['players'] = box['players'] if with_players else []
                if not game['score']:
                    game['score'] = box['score']
            except Exception as exc:
                if with_players:
                    game['error'] = str(exc)
    return game


def get_a2_day(day):
    with LOCK:
        cached = CACHE.get(('a2', day))
        if cached and time.monotonic() - cached[0] < (10 if any(g['status'] == 'IN CORSO' for g in cached[1]['games']) else 60):
            return cached[1]
    rows = a2_schedule(day)
    with ThreadPoolExecutor(max_workers=10) as pool:
        games = list(pool.map(lambda row: a2_game(row, day), rows))
    result = {'day': int(day), 'games': games}
    with LOCK:
        CACHE[('a2', day)] = (time.monotonic(), result)
    return result


def get_a2_scores(day):
    rows = a2_schedule(day)
    with ThreadPoolExecutor(max_workers=4) as pool:
        games = list(pool.map(lambda row: a2_game(row, day, with_players=False), rows))
    return [{key: g[key] for key in ('id', 'status', 'score', 'periods', 'quarter', 'datetime')}
            for g in games]


def get_euro_day(day):
    with LOCK:
        cached = CACHE.get(('euro', day))
        if cached and time.monotonic() - cached[0] < 60:
            return cached[1]
    schedule_rows = games_for_round(day)
    # Intenzionalmente sequenziale: il feed EuroLeague applica rate limiting.
    games = [game_from_schedule(row, day, with_players=True) for row in schedule_rows]
    result = {'day': int(day), 'games': games}
    with LOCK:
        CACHE[('euro', day)] = (time.monotonic(), result)
    return result


def get_euro_scores(day):
    return [{key: g[key] for key in ('id','status','score','periods','quarter','datetime')}
            for g in [game_from_schedule(row, day, with_players=False) for row in games_for_round(day)]]


def get_eurocup_day(day):
    with LOCK:
        cached = CACHE.get(('eurocup', day))
        if cached and time.monotonic() - cached[0] < 60:
            return cached[1]
    schedule_rows = eurocup_games_for_round(day)
    games = [eurocup_game_from_schedule(row, day, with_players=True) for row in schedule_rows]
    result = {'day': int(day), 'games': games}
    with LOCK:
        CACHE[('eurocup', day)] = (time.monotonic(), result)
    return result


def get_eurocup_scores(day):
    return [{key: g[key] for key in ('id','status','score','periods','quarter','datetime')}
            for g in [eurocup_game_from_schedule(row, day, with_players=False) for row in eurocup_games_for_round(day)]]


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type, attachment=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if attachment:
            self.send_header('Content-Disposition', f'attachment; filename="{attachment}"')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def json_response(self, status, data):
        self.respond(status, json.dumps(data, ensure_ascii=False).encode(), 'application/json; charset=utf-8')

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path in ('/', '/index.html'):
            return self.respond(200, HTML, 'text/html; charset=utf-8')
        if url.path == '/health':
            return self.json_response(200, {'ok': True})
        if url.path == '/api/calendar':
            return self.json_response(200, CALENDAR)
        if url.path in ('/api/day', '/api/excel', '/api/scores'):
            params = parse_qs(url.query)
            day = params.get('day', [''])[0]
            league = params.get('league', ['lba'])[0]
            if league not in ('lba', 'a2', 'euro', 'eurocup') or not re.fullmatch(r'\d{1,2}', day):
                return self.json_response(400, {'error': 'Giornata non valida.'})
            if league == 'lba' and day not in CALENDAR or league == 'a2' and day not in A2_CALENDAR or league == 'euro' and not (1 <= int(day) <= 38) or league == 'eurocup' and not (1 <= int(day) <= 18):
                return self.json_response(400, {'error': 'Giornata non valida.'})
            if url.path == '/api/scores':
                try:
                    score_fun = {'lba': get_lba_scores, 'a2': get_a2_scores, 'euro': get_euro_scores, 'eurocup': get_eurocup_scores}[league]
                    return self.json_response(200, {'games': score_fun(day)})
                except Exception as exc:
                    return self.json_response(502, {'error': str(exc)})
            try:
                day_fun = {'lba': get_lba_day, 'a2': get_a2_day, 'euro': get_euro_day, 'eurocup': get_eurocup_day}[league]
                result = day_fun(day)
            except Exception as exc:
                return self.json_response(502, {'error': str(exc)})
            if url.path == '/api/day':
                return self.json_response(200, result)
            if any(g['error'] for g in result['games']):
                return self.json_response(502, {'error': 'Alcune partite non sono state lette: riprova prima di esportare.'})
            content = make_xlsx(int(day), result['games'])
            name = {'lba':'LBA','a2':'LNP_A2','euro':'EUROLEAGUE','eurocup':'EUROCUP'}[league]
            return self.respond(200, content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', f'{name}_2026-27_giornata_{int(day):02d}.xlsx')
        self.json_response(404, {'error': 'Pagina non trovata.'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '10000'))
    print(f'Server LBA / LNP A2 / EuroLeague / EuroCup in ascolto sulla porta {port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
