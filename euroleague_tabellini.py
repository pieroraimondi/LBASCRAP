"""EuroLeague 2026/27 schedule and boxscore reader using the public v2 feed."""
import json
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from lba_tabellini import FIELDS

BASE = 'https://api-live.euroleague.net/v2/competitions/E/seasons/E2026'
MIRROR = 'https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2026'


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
    raise RuntimeError('EuroLeague calendario non disponibile. '+' | '.join(errors))


def games_for_round(day):
    day=int(day)
    rows=[g for g in schedule() if _round(g)==day]
    rows.sort(key=lambda g:int(_first(g,'gameCode',default=0) or 0))
    if not rows: raise ValueError(f'Nessuna partita EuroLeague trovata per la giornata {day}.')
    return rows


def _minutes(v):
    if v in (None,''): return ''
    if isinstance(v,(int,float)): return int(v)
    s=str(v).strip()
    if ':' in s:
        try: return int(s.split(':',1)[0])
        except ValueError: return ''
    try: return int(float(s))
    except ValueError: return ''


def _player_name(p):
    person=p.get('person') or p.get('player') or {}
    if isinstance(person,dict):
        full=_first(person,'name','fullName','displayName',default='')
        if full: return str(full)
        first=_first(person,'firstName','name',default=''); last=_first(person,'lastName','surname',default='')
        if first or last: return f'{first} {last}'.strip()
    return str(_first(p,'playerName','name','fullName',default=''))


def _player_row(p, game_code, day, date, team, opp, location):
    stats=p.get('stats') if isinstance(p.get('stats'),dict) else p
    def val(*keys): return _first(stats,*keys,default='')
    row={k:'' for k in FIELDS}
    row.update({
        'GameID':str(game_code),'Giornata':day,'Data':date,'Squadra':team,'Avversaria':opp,'Casa_Trasferta':location,
        'Giocatore':_player_name(p),'Numero':_first(p,'jerseyNumber','shirtNumber','number',default=''),
        'Minuti':_minutes(val('minutes','timePlayed','min')),'Punti':val('points','pts'),'Valutazione':val('pir','valuation','indexRating'),
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
        result['players']=rows
        if played and not rows: result['error']='Boxscore EuroLeague vuoto.'
    except Exception as exc: result['error']=str(exc)
    return result
