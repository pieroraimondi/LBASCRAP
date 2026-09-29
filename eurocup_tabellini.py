"""EuroCup 2026/27 schedule and boxscore reader using the public v2 feed."""
import json
import time
import math
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from lba_tabellini import FIELDS

BASE = 'https://api-live.euroleague.net/v2/competitions/U/seasons/U2026'
MIRROR = 'https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/U/seasons/U2026'
LEGACY_BOXSCORE = 'https://live.euroleague.net/api/Boxscore?gamecode={game_code}&seasoncode=U2026'


def _json(url, retries=3):
    last = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; LBASCRAP/1.0)','Accept':'application/json','Cache-Control':'no-cache'})
            with urlopen(req, timeout=30) as r:
                return json.load(r)
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            last = exc
            if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                break
            if attempt + 1 < retries:
                time.sleep(1.0 * (2 ** attempt))
    raise last


def _first(d, *keys, default=''):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return default


def _club_name(side):
    if not isinstance(side, dict): return ''
    club = side.get('club') or side.get('team') or side
    if isinstance(club, dict):
        return str(_first(club, 'name','clubName','clubPermanentName','shortName','abbreviatedName','code', default=''))
    return str(club or '')


def _side_name(game, key):
    side = game.get(key) or {}
    return _club_name(side)


def _score(game, key):
    side = game.get(key) or {}
    return _first(side, 'score','points','totalScore', default='')


def _round(game):
    value = _first(game, 'round','roundNumber','roundCode', default='')
    if isinstance(value, dict): value = _first(value,'number','round','code',default='')
    try: return int(value)
    except Exception: return None


def _datetime(game):
    value = _first(game,'date','startDate','gameDate','dateTime','startTime',default='')
    return str(value or '')


def schedule():
    errors=[]
    for base in (BASE, MIRROR):
        try:
            payload=_json(base+'/games')
            rows=payload.get('data',payload) if isinstance(payload,dict) else payload
            if isinstance(rows,list): return rows
            errors.append(f'{base}: formato calendario inatteso')
        except Exception as exc: errors.append(f'{base}: {exc}')
    raise RuntimeError('EuroCup calendario non disponibile. '+' | '.join(errors))


def games_for_round(day):
    day=int(day)
    rows=[g for g in schedule() if _round(g)==day]
    rows.sort(key=lambda g:int(_first(g,'gameCode',default=0) or 0))
    if not rows: raise ValueError(f'Nessuna partita EuroCup trovata per la giornata {day}.')
    return rows


def _minutes(v):
    """Normalise EuroCup timePlayed to whole minutes.

    v2 game stats exposes timePlayed as seconds (float); the legacy live
    Boxscore exposes Minutes as MM:SS.  The rest of LBASCRAP works with
    completed whole minutes, so both shapes are normalised here.
    """
    if v in (None, ''): return ''
    if isinstance(v, (int, float)):
        # v2: seconds, e.g. 1088.0 == 18:08.  Small numeric values are
        # accepted as already-minute values for defensive compatibility.
        return int(math.ceil(v / 60.0)) if v > 60 else int(math.ceil(v))
    s = str(v).strip()
    if not s or s.upper() == 'DNP': return 0
    if ':' in s:
        try:
            mm, ss = s.split(':', 1)
            return int(mm) + (1 if float(ss) > 0 else 0)
        except ValueError: return ''
    try:
        n = float(s)
        return int(math.ceil(n / 60.0)) if n > 60 else int(math.ceil(n))
    except ValueError: return ''


def _player_name(p):
    """Read identity from both v2 and legacy player records."""
    # v2 shape: {player: {person: {...}, dorsal: ...}, stats: {...}}
    player = p.get('player') if isinstance(p, dict) else None
    if isinstance(player, dict):
        person = player.get('person') or player
        if isinstance(person, dict):
            full = _first(person, 'name', 'fullName', 'displayName', default='')
            if full: return str(full).strip()
            first = _first(person, 'firstName', 'first_name', default='')
            last = _first(person, 'lastName', 'surname', 'last_name', default='')
            if first or last: return f'{first} {last}'.strip()
    person = p.get('person') if isinstance(p, dict) else None
    if isinstance(person, dict):
        full = _first(person, 'name', 'fullName', 'displayName', default='')
        if full: return str(full).strip()
        first = _first(person, 'firstName', default='')
        last = _first(person, 'lastName', 'surname', default='')
        if first or last: return f'{first} {last}'.strip()
    name = str(_first(p, 'Player', 'PLAYER', 'playerName', 'name', 'fullName', default='')).strip()
    # legacy feed commonly uses "SURNAME, NAME".
    if ',' in name:
        last, first = [x.strip() for x in name.split(',', 1)]
        if first and last: name = f'{first} {last}'
    return name


def _player_row(p, game_code, day, date, team, opp, location):
    stats=p.get('stats') if isinstance(p.get('stats'),dict) else p
    def val(*keys): return _first(stats,*keys,default='')
    row={k:'' for k in FIELDS}
    row.update({
        'GameID':str(game_code),'Giornata':day,'Data':date,'Squadra':team,'Avversaria':opp,'Casa_Trasferta':location,
        'Giocatore':_player_name(p),'Numero':_first((p.get('player') or {}) if isinstance(p,dict) else {},'dorsal','jerseyNumber','shirtNumber','number',default=_first(p,'Dorsal','DORSAL','jerseyNumber','shirtNumber','number',default='')),
        'Minuti':_minutes(val('timePlayed','minutes','Minutes','MINUTES','min')),'Punti':val('points','Points','POINTS','pts'),'Valutazione':val('valuation','Valuation','VALUATION','pir','indexRating'),
        'Assist':val('assists','ast'),'Rimbalzi':val('totalRebounds','rebounds','reb'),'Rimbalzi_offensivi':val('offensiveRebounds','oreb'),
        'Rimbalzi_difensivi':val('defensiveRebounds','dreb'),'Palle_perse':val('turnovers','to'),'Palle_recuperate':val('steals','stl'),
        'Falli_commessi':val('foulsCommitted','personalFouls','pf'),'Falli_subiti':val('foulsReceived','foulsDrawn'),
        'T2_realizzati':val('twoPointersMade','twoPointsMade','fg2Made'),'T2_tentati':val('twoPointersAttempted','twoPointsAttempted','fg2Attempted'),
        'T3_realizzati':val('threePointersMade','threePointsMade','fg3Made'),'T3_tentati':val('threePointersAttempted','threePointsAttempted','fg3Attempted'),
        'TL_realizzati':val('freeThrowsMade','ftMade'),'TL_tentati':val('freeThrowsAttempted','ftAttempted'),'Plus_minus':val('plusMinus','plusminus')})
    return row


def _stats(game_code):
    errors=[]
    for base in (BASE,MIRROR):
        try: return _json(f'{base}/games/{game_code}/stats')
        except Exception as exc: errors.append(f'{base}: {exc}')
    raise RuntimeError('boxscore non disponibile. '+' | '.join(errors))



def _legacy_stats(game_code):
    return _json(LEGACY_BOXSCORE.format(game_code=game_code))


def _legacy_rows(payload, game_code, day, date, home, away):
    """Parse live.euroleague.net Boxscore: Stats[0/1].PlayersStats."""
    stats = payload.get('Stats') if isinstance(payload, dict) else None
    if not isinstance(stats, list): return []
    rows=[]
    for i, side in enumerate(stats[:2]):
        if not isinstance(side, dict): continue
        team = str(_first(side, 'Team', 'TEAM', default='')).strip() or (home if i == 0 else away)
        opp = away if i == 0 else home
        loc = 'Casa' if i == 0 else 'Trasferta'
        players = side.get('PlayersStats') or side.get('playersStats') or []
        if not isinstance(players, list): continue
        for p in players:
            if not isinstance(p, dict): continue
            name=_player_name(p)
            if name:
                rows.append(_player_row(p,game_code,int(day),date,team,opp,loc))
    return rows

def game_from_schedule(g, day, with_players=True):
    code=_first(g,'gameCode',default='')
    home=_side_name(g,'local') or 'Casa'; away=_side_name(g,'road') or 'Ospite'; date=_datetime(g)
    hs=_score(g,'local'); as_=_score(g,'road')
    played = hs not in ('',None) and as_ not in ('',None)
    status='TERMINATA' if played else 'DA GIOCARE'
    result={'id':str(code),'home':home,'away':away,'status':status,'datetime':date,'score':f'{hs} - {as_}' if played else '', 'periods':[],'quarter':'','players':[],'error':''}
    if not with_players or not played: return result
    try:
        payload=_stats(code)
        rows=[]
        for key,team,opp,loc in [('local',home,away,'Casa'),('road',away,home,'Trasferta')]:
            side=payload.get(key) or {}
            players=side.get('players') or []
            for p in players:
                name=_player_name(p)
                if name: rows.append(_player_row(p,code,int(day),date,team,opp,loc))
        # Defensive fallback: the legacy live feed has a different but very
        # stable Stats[].PlayersStats shape.  Use it only when v2 returned no
        # usable player identities, not merely on a single malformed player.
        if not rows:
            try:
                rows = _legacy_rows(_legacy_stats(code), code, day, date, home, away)
            except Exception as legacy_exc:
                result['error'] = f'v2 senza giocatori; fallback live fallito: {legacy_exc}'
        result['players']=rows
        if played and not rows and not result['error']:
            result['error']='Boxscore EuroCup vuoto (v2 e fallback live).'
    except Exception as exc:
        # If the v2 request itself fails, still try the official legacy feed.
        try:
            rows = _legacy_rows(_legacy_stats(code), code, day, date, home, away)
            result['players'] = rows
            if not rows: result['error'] = f'v2: {exc}; fallback live vuoto.'
        except Exception as legacy_exc:
            result['error']=f'v2: {exc}; fallback live: {legacy_exc}'
    return result
