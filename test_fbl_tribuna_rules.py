from fantasy import score_fbl, norm

def idx(rows):
    return {norm(n):(n,m,v) for n,m,v in rows}

def p(name,role,status,explicit=False):
    return {'name':name,'role':role,'status':status,'explicit_single_fbl_role':explicit}

# 5 starters + 5 bench. Starter G1 is DNP. Bench G1 is promoted; tribunal fills the vacancy.
base=[
 p('S1','G','STR'),p('S2','G','ITA'),p('S3','A','ITA'),p('S4','A','STR'),p('S5','C','ITA'),
 p('B1','G','STR'),p('B2','G','STR'),p('B3','A','STR'),p('B4','A','STR'),p('B5','C','STR'),
]
st=idx([(x['name'],20,10) for x in base] + [('S1',0,0),('T11',20,20),('T12',20,30),('T13',20,40)])
# 11 has wrong explicit role A, 12 is G and must be selected before 13.
players=base+[p('T11','A','STR',True),p('T12','G','STR',True),p('T13','G','STR',True)]
score,det=score_fbl(players,st)
trib=[d for d in det if d['kind']=='tribuna']
assert len(trib)==1 and trib[0]['name']=='T12',trib

# Double role in tribuna is NEVER usable, even if roster-compatible.
players=base+[p('T11','G/AP','ITA',False),p('T12','G','STR',True)]
score,det=score_fbl(players,st)
trib=[d for d in det if d['kind']=='tribuna']
assert len(trib)==1 and trib[0]['name']=='T12',trib

# Missing explicit role: unusable.
players=base+[p('T11','G','ITA',False)]
score,det=score_fbl(players,st)
assert not [d for d in det if d['kind']=='tribuna']

# ITA constraint: top 10 have exactly 3 ITA and the DNP is one of them.
# STR tribunal would leave 2 ITA => rejected; next ITA G is accepted.
base2=[dict(x) for x in base]
base2[0]['status']='ITA'; base2[1]['status']='STR' # ITA now S1,S3,S5 exactly 3
players=base2+[p('T11','G','STR',True),p('T12','G','ITA',True)]
score,det=score_fbl(players,st)
trib=[d for d in det if d['kind']=='tribuna']
assert len(trib)==1 and trib[0]['name']=='T12',trib
print('FBL tribuna rules OK')
