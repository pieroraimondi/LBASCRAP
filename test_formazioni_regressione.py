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
from fantasy import best_match, norm
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
