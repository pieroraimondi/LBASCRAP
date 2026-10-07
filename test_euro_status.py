from euroleague_tabellini import game_from_schedule as el
from eurocup_tabellini import game_from_schedule as ec

def g(played=False,status='',score=0):
    return {'gameCode':12,'round':1,'date':'2026-09-29T18:00:00', 'played':played,'gameStatus':status,
            'local':{'club':{'name':'HOME'},'score':score},'road':{'club':{'name':'AWAY'},'score':score}}
for parser in (el,ec):
    x=parser(g(False,'SCHEDULED',0),1,False); assert x['status']=='DA GIOCARE' and x['score']=='0 - 0'
    x=parser(g(False,'LIVE',12),1,False); assert x['status']=='IN CORSO' and x['score']=='12 - 12'
    x=parser(g(True,'CONFIRMED',77),1,False); assert x['status']=='TERMINATA' and x['score']=='77 - 77'
print('Euro status tests OK')
