from fantasy import parse_formation, score_formation, DEFAULT_ROSTERS

# Regression: forum metadata must never occupy a formation slot.
raw='''Promozione\nGruppo: Utente\nMessaggi: 8\nPunteggio: 0\nProvenienza: Napoli\nStato:\nI Mollo\nPM Avery Woodson\nG Michele Vitali\nAP Tevin Mack\nAG Jeff Brooks\nC Romello White\nPM Eugenio Rota\nG Alvise Sarto\nAP Niccolo De Vico\nAG Simone Zanotti\nC Vittorio Bartoli\n11 Lorenzo Caroti PM\n12 Matteo Piccoli G/AP\nModificato da Hot Sauce 7'''
ps=parse_formation(raw, roster_players=DEFAULT_ROSTERS['pcf_lnp']['I Mollo'], competition='pcf_lnp')
assert [p['name'] for p in ps] == ['Avery Woodson','Michele Vitali','Tevin Mack','Jeff Brooks','Romello White','Eugenio Rota','Alvise Sarto','Niccolo De Vico','Simone Zanotti','Vittorio Bartoli','Lorenzo Caroti','Matteo Piccoli']

# Regression PCF: 11°/12° can use the sum of residual minutes of compatible roles.
players=[
 {'name':'Stefano Gentile','role':'PM/G'}, {'name':'Caleb Walker','role':'G/AP'}, {'name':'Mattia Udom','role':'AP/AG'}, {'name':'Matt Tiby','role':'AG/C'}, {'name':'Jacorey Williams','role':'C'},
 {'name':'Stefano Saccoccia','role':'PM'}, {'name':'Luca Conti','role':'G/AP'}, {'name':'Aristide Mouaha','role':'G/AP'}, {'name':'Andrea Lo Biondo','role':'AG/C'}, {'name':'Mattia Acunzo','role':'AG/C'},
 {'name':'Michele Munari','role':'PM/G'}, {'name':'Michele Serpilli','role':'AP/AG'}]
vals=[(7,19),(1,28),(4,18),(0,0),(11,21),(2,21),(7,30),(8,26),(1,19),(3,17),(2,15),(12,14)]
stats={}
from fantasy import norm
for p,(v,m) in zip(players,vals): stats[norm(p['name'])]=(p['name'],m,v)
score,details=score_formation(players,stats)
assert score==49, (score,details)
assert details[-1]['name']=='Michele Serpilli' and details[-1]['fantasy']==12
print('PCF structural regression OK')
