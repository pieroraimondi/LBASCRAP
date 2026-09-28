#!/usr/bin/env python3
"""Esporta i tabellini giocatori di legabasket.it in CSV (Python 3, nessuna dipendenza)."""
import argparse
import csv
import json
import re
import sys
from html.parser import HTMLParser
from urllib.request import Request, urlopen


class NextData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.collect = False
        self.data = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == '__NEXT_DATA__':
            self.collect = True

    def handle_data(self, data):
        if self.collect:
            self.data.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.collect = False


FIELDS = ['GameID', 'Giornata', 'Data', 'Squadra', 'Avversaria', 'Casa_Trasferta',
          'Giocatore', 'Numero', 'Minuti', 'Punti', 'Valutazione', 'Assist',
          'Rimbalzi', 'Rimbalzi_offensivi', 'Rimbalzi_difensivi', 'Palle_perse',
          'Palle_recuperate', 'Falli_commessi', 'Falli_subiti',
          'T2_realizzati', 'T2_tentati', 'T3_realizzati', 'T3_tentati',
          'TL_realizzati', 'TL_tentati', 'Plus_minus']


def fetch_game(game):
    match = re.search(r'(?:/game/)?(\d{4,6})(?:/|$)', game.rstrip('/'))
    if not match:
        raise ValueError(f'ID/URL partita non valido: {game}')
    game_id = match.group(1)
    url = f'https://www.legabasket.it/game/{game_id}/statistiche'
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; LBA-CSV/1.0)'}), timeout=25) as response:
        html = response.read().decode('utf-8')
    parser = NextData()
    parser.feed(html)
    if not parser.data:
        raise ValueError(f'Dati strutturati assenti nella partita {game_id}')
    game_data = json.loads(''.join(parser.data))['props']['pageProps']['game']
    match_info = game_data['match']
    rows = []
    for side, own, other, location in [
        ('ht', 'h_team_name', 'v_team_name', 'Casa'),
        ('vt', 'v_team_name', 'h_team_name', 'Trasferta'),
    ]:
        for player in game_data['scores'][side]['rows']:
            seconds = player.get('sec')
            duration = int(player['min']) if player.get('min') is not None else (int(seconds)//60 if seconds is not None else '')
            row = dict(zip(FIELDS, [
                game_id, match_info.get('day_name'), match_info.get('match_datetime'),
                match_info.get(own), match_info.get(other), location,
                ' '.join(filter(None, [player.get('player_name'), player.get('player_surname')])),
                player.get('player_num'), duration, player.get('pun'), player.get('val_lega'),
                player.get('ass'), player.get('rimbalzi_t'), player.get('rimbalzi_o'),
                player.get('rimbalzi_d'), player.get('palle_p'), player.get('palle_r'),
                player.get('falli_c'), player.get('falli_sf'), player.get('t2_r'),
                player.get('t2_t'), player.get('t3_r'), player.get('t3_t'),
                player.get('tl_r'), player.get('tl_t'), player.get('plus_minus'),
            ]))
            rows.append({key: '' if value is None else value for key, value in row.items()})
    return {'match': match_info, 'players': rows}


def fetch(game):
    return fetch_game(game)['players']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('partite', nargs='+', help='URL o ID di una o più partite')
    ap.add_argument('-o', '--output', default='tabellini_lba.csv', help='CSV di destinazione')
    args = ap.parse_args()
    records = []
    failed = False
    for game in args.partite:
        try:
            rows = fetch(game)
            print(f'{game}: {len(rows)} giocatori' + (' (tabellino non ancora disponibile)' if not rows else ''), file=sys.stderr)
            records.extend(rows)
        except Exception as exc:
            print(f'{game}: errore: {exc}', file=sys.stderr)
            failed = True
    with open(args.output, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, delimiter=';')
        writer.writeheader()
        writer.writerows(records)
    print(f'Salvate {len(records)} righe in {args.output}', file=sys.stderr)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
