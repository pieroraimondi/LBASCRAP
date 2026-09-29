from fantasy import parse_page, best_match, player_index
from default_rosters import DEFAULT_ROSTERS

def names(comp,text,team):
    forms,_=parse_page(text,comp,{},DEFAULT_ROSTERS[comp])
    return [p['name'] for p in forms[team]]

pcf_lba='''sprizzaug\nview post Inviato il: 23/9/2026, 12:35\nPM - Darius Brown\nG/AP - Wendell Moore\nAP/AG - Trentyn Flowers\nAG/C - Aliou Diarra\nC - Chad Brown\nPM/G - Alessandro Manfredotti\nPM/G - Davide Casarin\nAP - Giovanni Veronesi\nAP/AG - Andrej Jakimovski\nAG/C - Jordan Bayehe\nPM/G - Marcus Carr\nC - Maximilian Ladurner\nMessaggio Privato'''
assert names('pcf_lba',pcf_lba,'Olimpija Ruero') == ['Darius Brown','Wendell Moore','Trentyn Flowers','Aliou Diarra','Chad Brown','Alessandro Manfredotti','Davide Casarin','Giovanni Veronesi','Andrej Jakimovski','Jordan Bayehe','Marcus Carr','Maximilian Ladurner']
assert 'Aaron Holiday' not in names('pcf_lba',pcf_lba,'Olimpija Ruero')

pcf_lnp='''sprizzaug\nview post Inviato il: 26/9/2026\nSCHINA\nDEMPS\nGASPARDO\nMINIOTAS\nSANTOS SILVA\nMONALDI\nACCORSI\nMOLLURA\nHADZIC\nDEL CHIARO\nCALBINI PM/G\nGUAIANA G/AP'''
assert names('pcf_lnp',pcf_lnp,'Olimpija Ruero') == ['SCHINA','DEMPS','GASPARDO','MINIOTAS','SANTOS SILVA','MONALDI','ACCORSI','MOLLURA','HADZIC','DEL CHIARO','CALBINI','GUAIANA']

fbl='''Alectro93\nview post Inviato il: 24/9/2026\nDRINK TEAM\nMODULO: 2-2-1\nG Glynn Watson\nG Hunter Hale\nA Denzel Valentine\nA Mezie Offurum\nC Dominik Olejniczak\nG Bruno Mascolo\nG Amedeo Della Valle\nA Giovanni Veronesi\nA Jack White\nC Paul Eboua\nG DeWayne Russell\nA Eimantas Bendzius\nA Federico Miaschi\nModificato da Alectro93'''
assert names('fbl_lba',fbl,'Drink Team') == ['Glynn Watson','Hunter Hale','Denzel Valentine','Mezie Offurum','Dominik Olejniczak','Bruno Mascolo','Amedeo Della Valle','Giovanni Veronesi','Jack White','Paul Eboua','DeWayne Russell','Eimantas Bendzius','Federico Miaschi']

idx=player_index([{'players':[{'Giocatore':'Valentine CHERY','Minuti':19,'Valutazione':14}]}])
assert best_match('Valentin Chery',idx)[1:] == (19,14)
print('OK: test regressione formazioni')

# Identity regression: same surname must never override a stronger full-name match.
from fantasy import best_match, norm, roster_match, score_fbl, player_index, FBL_ITA_NAMES
idx={norm('Charlie Moore'):('Charlie Moore',25,9), norm('Wendell Moore Jr'):('Wendell Moore Jr',0,0)}
assert best_match('Wendell Moore',idx)[0]=='Wendell Moore Jr'

# FBL invariant: the posted role/order is authoritative. Aliou Diarra was posted as C
# and must stay C; the roster's natural/multi-role metadata may never relocate him.
fbl='''Sprizzaug\nview post Inviato il: 24/9/2026, 11:36\nG MOORE JR\nA CHERY\nA PETERS\nC DIARRA\nC WRIGHT\nG ROSS\nG BROCKINGTON\nA STRAUTINS\nA SIMONOVIC\nC DIOP\nG ZAMPINI\nA LEVER\nC BROWN III\nMessaggio Privato'''
forms,_=parse_page(fbl,'fbl_lba',{},DEFAULT_ROSTERS['fbl_lba'])
assert [(p['name'],p['role']) for p in forms['Maccabi Ruero']][3] == ('DIARRA','C')

# End-to-end identity safety: if Wendell is absent from the boxscore, Charlie Moore
# must NEVER be borrowed from another team. An old poisoned learned alias is ignored
# because Charlie is not in Olimpija's current roster.
from fantasy import calculate_page
page='''sprizzaug\nview post Inviato il: 23/9/2026\nPM - Darius Brown\nG/AP - Wendell Moore\nAP/AG - Trentyn Flowers\nAG/C - Aliou Diarra\nC - Chad Brown\nPM/G - Alessandro Manfredotti\nPM/G - Davide Casarin\nAP - Giovanni Veronesi\nAP/AG - Andrej Jakimovski\nAG/C - Jordan Bayehe\nPM/G - Marcus Carr\nC - Maximilian Ladurner\nMessaggio Privato'''
games=[{'players':[{'Giocatore':'Charlie Edward Moore','Minuti':25,'Valutazione':9},
                   {'Giocatore':'Darius Brown','Minuti':27,'Valutazione':11},
                   {'Giocatore':'Trentyn Flowers','Minuti':5,'Valutazione':3},
                   {'Giocatore':'Aliou Diarra','Minuti':15,'Valutazione':6},
                   {'Giocatore':'Chad Brown','Minuti':18,'Valutazione':9}]}]
r=calculate_page(page,'pcf_lba',games,{'olimpija ruero|||wendell moore':'Charlie Edward Moore'})
d=r['teams']['Olimpija Ruero']['details']
assert d[1]['name'] != 'Charlie Edward Moore', d[1]
assert d[1]['name']=='Wendell Moore' and d[1]['minutes']==0 and d[1]['fantasy']==0, d[1]

# End-to-end FBL role invariant: roster says Aliou Diarra is C and posted C stays C.
fbl_page='''Sprizzaug\nview post Inviato il: 24/9/2026, 11:36\nG MOORE JR\nA CHERY\nA PETERS\nC DIARRA\nC WRIGHT\nG ROSS\nG BROCKINGTON\nA STRAUTINS\nA SIMONOVIC\nC DIOP\nG ZAMPINI\nA LEVER\nC BROWN III\nMessaggio Privato'''
r=calculate_page(fbl_page,'fbl_lba',[{'players':[{'Giocatore':'Aliou Diarra','Minuti':15,'Valutazione':6}]}],{})
parsed=r['parsed_formations']['Maccabi Ruero']
assert parsed[3]['role']=='C' and parsed[3]['canonical']=='Aliou Diarra', parsed[3]
diarra_details=[x for x in r['teams']['Maccabi Ruero']['details'] if norm(x.get('name',''))==norm('Aliou Diarra')]
assert diarra_details and diarra_details[0]['slot_role']=='C' and diarra_details[0]['role']=='C', diarra_details
print('OK: identity DNP + learned alias guard + FBL posted-role invariants')


# Poisoned learned aliases must never remap one roster player to another identity.
r=DEFAULT_ROSTERS['fbl_lba']['Maccabi Ruero']
poison={norm('CHERY'):'Aliou Diarra', norm('DIARRA'):'Valentin Chery'}
assert roster_match('CHERY','A',r,poison,'Maccabi Ruero')[0]=='Valentin Chery'
assert roster_match('DIARRA','C',r,poison,'Maccabi Ruero')[0]=='Aliou Diarra'

# Exact FBL detail regression for Maccabi G1 (not only the total).
S2={norm(n):(n,m,v) for n,m,v in [
('Wendell Moore',0,0),('Valentin Chery',19,14),('Alec Peters',0,0),('Aliou Diarra',15,6),('Moses Wright',22,16),
('Colbey Ross',27,24),('Izaiah Brockington',0,0),('Arturs Strautins',26,7),('Marko Simonovic',25,21),('Ousmane Diop',13,3),
('Federico Zampini',36,19),('Alessandro Lever',23,5),('John Brown',22,15)]}
ps=[{'role':r,'name':n,'explicit_single_fbl_role':(i>=10),'status':('ITA' if norm(n) in FBL_ITA_NAMES else 'STR')} for i,(r,n) in enumerate([('G','Wendell Moore'),('A','Valentin Chery'),('A','Alec Peters'),('C','Aliou Diarra'),('C','Moses Wright'),('G','Colbey Ross'),('G','Izaiah Brockington'),('A','Arturs Strautins'),('A','Marko Simonovic'),('C','Ousmane Diop'),('G','Federico Zampini'),('A','Alessandro Lever'),('C','John Brown')])]
score,det=score_fbl(ps,S2,'Maccabi Ruero')
assert score==100
assert [(x['name'],x['fantasy']) for x in det] == [('Colbey Ross',24),('Federico Zampini',6),('Valentin Chery',14),('Arturs Strautins',7),('Alessandro Lever',3),('Aliou Diarra',6),('Marko Simonovic',21),('Moses Wright',16),('Ousmane Diop',3)]

# PCF LNP apostrophe/case regression: Dell'Agnello must hook to 13 in 26.
idx=player_index([{'players':[{'Giocatore':"Giacomo Dell'agnello",'Minuti':26,'Valutazione':13}]}])
assert best_match('Giacomo Dell’Agnello',idx)[1:] == (26,13)
print('OK: poisoned aliases + exact FBL detail + DellAgnello')

# End-to-end FBL with poisoned browser dictionary: detail must remain official.
raw="""Sprizzaug
view post Inviato il: 24/9/2026, 11:36
G MOORE JR
A CHERY
A PETERS
C DIARRA
C WRIGHT
G ROSS
G BROCKINGTON
A STRAUTINS
A SIMONOVIC
C DIOP
G ZAMPINI
A LEVER
C BROWN III
Messaggio Privato"""
rows=[('Wendell Moore',0,0),('Valentin Chery',19,14),('Alec Peters',0,0),('Aliou Diarra',15,6),('Moses Wright',22,16),('Colbey Ross',27,24),('Izaiah Brockington',0,0),('Arturs Strautins',26,7),('Marko Simonovic',25,21),('Ousmane Diop',13,3),('Federico Zampini',36,19),('Alessandro Lever',23,5),('John Brown',22,15)]
games=[{'players':[{'Giocatore':n,'Minuti':m,'Valutazione':v} for n,m,v in rows]}]
calc=calculate_page(raw,'fbl_lba',games,poison)
d=calc['teams']['Maccabi Ruero']['details']
assert calc['teams']['Maccabi Ruero']['score']==100
assert [x['name'] for x in d]==['Colbey Ross','Federico Zampini','Valentin Chery','Arturs Strautins','Alessandro Lever','Aliou Diarra','Marko Simonovic','Moses Wright','Ousmane Diop']
print('OK: end-to-end poisoned dictionary FBL')

# FBL hard invariant: even a completely poisoned learned dictionary must NEVER rewrite
# the posted formation. Identity comes from current post + current team roster only.
from test_fbl_benchmark import RAW as FBL_RAW, S as FBL_STATS, EXPECT as FBL_EXPECT
poison={
    'glynn watson':'Jack White','hunter hale':'Jack White','denzel valentine':'Jack White',
    'mezie offurum':'DeWayne Russell','dominik olejniczak':'Jack White',
    'bruno mascolo':'Jack White','amedeo della valle':'Jack White','giovanni veronesi':'Jack White',
    'jack white':'DeWayne Russell','paul eboua':'Jack White','dewayne russell':'Jack White',
    'moore jr':'Aliou Diarra','chery':'Aliou Diarra','diarra':'Alessandro Lever','ross':'Ousmane Diop'
}
GAMES_POISON=[{'players':[{'Giocatore':v[0],'Minuti':v[1],'Valutazione':v[2]} for v in FBL_STATS.values()]}]
calc_poison=calculate_page(FBL_RAW,'fbl_lba',GAMES_POISON,poison)
for team,base in FBL_EXPECT.items():
    assert calc_poison['teams'][team]['score']==base,(team,calc_poison['teams'][team]['score'],base)
# source/canonical order must remain the posted Drink Team 13, not repeated aliases
posted=[p['canonical'] for p in calc_poison['parsed_formations']['Drink Team']]
assert posted[:10]==['Glynn Watson','Hunter Hale','Denzel Valentine','Mezie Offurum','Dominik Olejniczak','Bruno Mascolo','Amedeo Della Valle','Giovanni Veronesi','Jack White','Paul Eboua'], posted
macc=[p['canonical'] for p in calc_poison['parsed_formations']['Maccabi Ruero']]
assert macc[:5]==['Wendell Moore','Valentin Chery','Alec Peters','Aliou Diarra','Moses Wright'],macc
print('OK: FBL learned aliases cannot rewrite posted formations')
