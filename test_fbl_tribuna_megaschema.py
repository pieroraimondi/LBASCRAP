from fantasy import score_fbl, norm

def p(n,r,s='STR',explicit=False): return {'name':n,'role':r,'status':s,'explicit_single_fbl_role':explicit}
def stats(players, overrides=None):
    d={norm(x['name']):(x['name'],20,10) for x in players}
    for n,m,v in (overrides or []): d[norm(n)]=(n,m,v)
    return d

def kinds(det): return [(x['kind'],x['name'],x['fantasy']) for x in det]

# base: 5 moduli, >=3 ITA nei dieci
base=[p('S1','G','ITA'),p('S2','A','ITA'),p('S3','A','ITA'),p('S4','A'),p('S5','C'),
      p('B1','G'),p('B2','G'),p('B3','A'),p('B4','A'),p('B5','C')]

# 1 T presente/P assente -> T11 entra panchina
pl=base+[p('T11','G','ITA',True)]
sc,dt=score_fbl(pl,stats(pl,[('B1',0,0)])); assert ('tribuna','T11',10) in kinds(dt),kinds(dt)
# 2 T assente/P presente -> P promosso, T11 panchina
sc,dt=score_fbl(pl,stats(pl,[('S1',0,0)])); assert ('riserva promossa','B1',10) in kinds(dt) and ('tribuna','T11',10) in kinds(dt),kinds(dt)
# 3 doppia assenza + due G -> primo quintetto, secondo panchina
pl2=base+[p('T11','G','ITA',True),p('T12','G','STR',True)]
sc,dt=score_fbl(pl2,stats(pl2,[('S1',0,0),('B1',0,0),('T11',20,21),('T12',20,12)]))
assert ('tribuna titolare','T11',21) in kinds(dt) and ('tribuna','T12',12) in kinds(dt),kinds(dt)
# 4 titolare A, panchina G: doppia assenza usa due G (ruolo guida=panchina)
sc,dt=score_fbl(pl2,stats(pl2,[('S2',0,0),('B2',0,0)])); kk=kinds(dt)
assert ('tribuna titolare','T11',10) in kk and ('tribuna','T12',10) in kk,kk
# 5 doppio ruolo/non esplicito non utilizzabile
pl3=base+[p('X','G/AP','ITA',False)]
sc,dt=score_fbl(pl3,stats(pl3,[('S1',0,0),('B1',0,0)])); assert not any('tribuna' in x[0] for x in kinds(dt)),kinds(dt)
# 6 ordine moduli: un solo G va al modulo 1, non al 2
pl4=base+[p('ONE','G','ITA',True)]
sc,dt=score_fbl(pl4,stats(pl4,[('B1',0,0),('B2',0,0)]));
trib=[x for x in dt if 'tribuna' in x['kind']]; assert len(trib)==1 and trib[0]['slot']==1,trib
# 7 ordine tribuna: 11 prima di 12
pl5=base+[p('ELEVEN','G','ITA',True),p('TWELVE','G','ITA',True)]
sc,dt=score_fbl(pl5,stats(pl5,[('B1',0,0)])); trib=[x for x in dt if 'tribuna' in x['kind']]; assert trib[0]['name']=='ELEVEN',trib
# 8 vincolo ITA globale: se S1 ITA assente, T11 STR non basta; T12 ITA deve essere scelto
b=[dict(x) for x in base]; b[1]['status']='STR' # ITA solo S1,S3 tra starter +? ensure third B5
b[9]['status']='ITA' # ITA S1,S3,B5 = 3
pl6=b+[p('T11','G','STR',True),p('T12','G','ITA',True)]
sc,dt=score_fbl(pl6,stats(pl6,[('S1',0,0)])); trib=[x for x in dt if 'tribuna' in x['kind']]; assert trib and trib[0]['name']=='T12',trib
print('FBL megaschema tribuna: OK')
