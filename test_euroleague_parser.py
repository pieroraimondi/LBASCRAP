from euroleague_tabellini import _player_name, _player_row, _legacy_rows, _minutes

v2 = {
 'player': {'person': {'firstName':'Chris','lastName':'Jones'}, 'dorsal': 3},
 'stats': {'timePlayed':1124.0,'points':12.0,'valuation':25.0}
}
r=_player_row(v2,1,1,'2026-09-24','Crvena Zvezda','Zalgiris','Casa')
assert r['Giocatore']=='Chris Jones', r
assert r['Minuti']==19, r
assert r['Punti']==12.0 and r['Valutazione']==25.0, r

legacy={'Stats':[
 {'Team':'Crvena Zvezda','PlayersStats':[{'Player':'JONES, CHRIS','Minutes':'18:44','Points':12,'Valuation':25}]},
 {'Team':'Zalgiris','PlayersStats':[{'Player':'VALANCIUNAS, JONAS','Minutes':'21:36','Points':18,'Valuation':24}]}
]}
rows=_legacy_rows(legacy,1,1,'2026-09-24','Crvena Zvezda','Zalgiris')
assert len(rows)==2, rows
assert rows[0]['Giocatore']=='CHRIS JONES' and rows[0]['Minuti']==19 and rows[0]['Valutazione']==25, rows[0]
assert rows[1]['Giocatore']=='JONAS VALANCIUNAS' and rows[1]['Minuti']==22 and rows[1]['Valutazione']==24, rows[1]
print('EUROLEAGUE PARSER OK')

# Regression: v2 timePlayed is always seconds, even below one minute.
for seconds, expected in [(0,0),(1,1),(47,1),(59,1),(60,1),(61,2),(1088,19),(1200,20),(1201,21)]:
    assert _minutes(seconds) == expected, (seconds, _minutes(seconds), expected)
