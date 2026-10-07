"""Lettura del boxscore LNP Serie A2 2026/27, senza dipendenze esterne."""
import re
from datetime import datetime
from html import unescape
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from lba_tabellini import FIELDS

BASE = 'https://www.legapallacanestro.com/wp/match/{}/ita2/x2627'
TAG = re.compile(r'<[^>]+>')


def clean(value):
    return unescape(TAG.sub('', value)).strip()


def number(value):
    value = clean(value)
    return int(value) if re.fullmatch(r'-?\d+', value) else ''


def date_iso(date, hour):
    if not date:
        return ''
    try:
        return datetime.strptime(date + ' ' + (hour or '00:00'), '%d/%m/%Y %H:%M').replace(
            tzinfo=ZoneInfo('Europe/Rome')).isoformat()
    except ValueError:
        return ''


def read_boxscore(game_id, home, away, day, date, allow_empty=False):
    url = BASE.format(game_id)
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}), timeout=25) as response:
        html = response.read().decode('utf-8')
    if 'id="match-main"' not in html:
        raise ValueError('Tabellino non ancora disponibile')

    score_nodes = re.findall(r'<span class="score[^\"]*">(.*?)</span>', html, re.S)
    score = ' - '.join(clean(x) for x in score_nodes[:2]) if len(score_nodes) >= 2 else ''
    section = re.search(r'<div class="match-result-periods">(.*?)</div>', html, re.S)
    pairs = []
    if section:
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', section.group(1), re.S):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
            if len(cells) == 2:
                pair = (number(cells[0]), number(cells[1]))
                if all(isinstance(value, int) for value in pair):
                    pairs.append(pair)
    # Il sito etichetta le colonne dei quarti in ordine inverso in alcune pagine.
    # I totali ufficiali permettono di verificare l'orientamento senza affidarsi alle intestazioni.
    if score and pairs:
        totals = [number(x) for x in score_nodes[:2]]
        if all(isinstance(x, int) for x in totals) and sum(x[0] for x in pairs) == totals[1] and sum(x[1] for x in pairs) == totals[0]:
            pairs = [(a, h) for h, a in pairs]
    periods = [{'name': f'{i}°Q' if i <= 4 else 'OT', 'home': h, 'away': a}
               for i, (h, a) in enumerate(pairs, 1)]

    wrappers = re.findall(r'<div class="table-wrapper-evo">(.*?)</div>', html, re.S)
    if allow_empty and not wrappers:
        return {'score': score, 'periods': periods, 'players': []}
    if len(wrappers) != 2:
        raise ValueError('Boxscore non ancora disponibile o incompleto')
    players = []
    for side, team, opponent, wrapper in zip(('Casa', 'Trasferta'), (home, away), (away, home), wrappers):
        halves = re.split(r'<td colspan="23" class="table-right">', wrapper, maxsplit=1)
        if len(halves) != 2:
            raise ValueError('Struttura del boxscore non riconosciuta')
        identities = []
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', halves[0], re.S):
            jersey = re.search(r'<td class="jersey">(.*?)</td>', row, re.S)
            player = re.search(r'<a href="/giocatore/[^\"]+">(.*?)</a>', row, re.S)
            if jersey and player:
                identities.append((number(jersey.group(1)), clean(player.group(1))))
        stats = []
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', halves[1], re.S):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
            if len(cells) == 23:
                stats.append([number(cell) for cell in cells])
        # Le righe statistiche dei giocatori precedono le righe aggregate/footer.
        # LNP può aggiungere o togliere righe di riepilogo (totali, staff, ecc.):
        # non devono invalidare un boxscore altrimenti completo.
        if len(stats) < len(identities):
            raise ValueError('Numero giocatori/statistiche incoerente')
        player_stats = stats[:len(identities)]
        for (jersey, name), values in zip(identities, player_stats):
            p = dict.fromkeys(FIELDS, '')
            p.update(GameID=game_id, Giornata=day, Data=date, Squadra=team,
                     Avversaria=opponent, Casa_Trasferta=side, Giocatore=name,
                     Numero=jersey, Punti=values[0], Minuti=values[1],
                     Falli_commessi=values[2], Falli_subiti=values[3],
                     T2_realizzati=values[4], T2_tentati=values[5],
                     T3_realizzati=values[7], T3_tentati=values[8],
                     TL_realizzati=values[10], TL_tentati=values[11],
                     Rimbalzi_offensivi=values[13], Rimbalzi_difensivi=values[14],
                     Rimbalzi=values[15], Palle_perse=values[18],
                     Palle_recuperate=values[19], Assist=values[20],
                     Valutazione=values[21])
            players.append(p)
    return {'score': score, 'periods': periods, 'players': players}
