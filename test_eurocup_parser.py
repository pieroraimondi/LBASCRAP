from eurocup_tabellini import _player_row, _legacy_rows, BASE, LEGACY_BOXSCORE
assert '/competitions/U/seasons/U2026' in BASE
assert 'seasoncode=U2026' in LEGACY_BOXSCORE
v2={'player':{'person':{'firstName':'Test','lastName':'Player'}},'stats':{'timePlayed':1201.0,'points':7,'valuation':9}}
r=_player_row(v2,12,1,'2026-09-29','Neptunas','Trento','Casa')
assert r['Minuti']==21, r
legacy={'Stats':[{'Team':'Neptunas','PlayersStats':[{'Player':'PLAYER, TEST','Minutes':'20:00','Points':7,'Valuation':9}]},{'Team':'Trento','PlayersStats':[{'Player':'OTHER, TEST','Minutes':'20:01','Points':3,'Valuation':4}]}]}
rows=_legacy_rows(legacy,12,1,'2026-09-29','Neptunas','Trento')
assert rows[0]['Minuti']==20 and rows[1]['Minuti']==21, rows
print('EUROCUP PARSER OK')
