from fantasy import parse_page, score_fbl, norm, DEFAULT_ROSTERS, FBL_ITA_NAMES

def stats(rows):
    return {norm(n):(n,m,v) for n,v,m in rows}

S=stats([
('Glynn Watson',15,24),('Hunter Hale',-5,29),('Denzel Valentine',17,28),('Mezie Offurum',9,30),('Dominik Olejniczak',17,24),('Bruno Mascolo',0,23),('Amedeo Della Valle',0,0),('Giovanni Veronesi',-7,12),('Jack White',6,24),('Paul Eboua',0,0),('DeWayne Russell',21,28),
('Jaylen Barford',16,32),('Alessandro Cappelletti',23,24),('Isaiah Roby',-5,14),('Andrej Jakimovski',12,24),('Nick McGlynn',13,21),('Andrea Pecchia',3,18),('Aljami Durham',12,14),('Jason Burnell',29,26),('JT Thor',9,26),('Skylar Spencer',16,19),
('Niccolo Mannion',13,28),('Aaron Holiday',9,28),('Derrick Alston',16,21),('Amedeo Tessitori',23,20),('Miro Bilan',37,26),('Darius Thompson',11,18),('Charlie Edward Moore',9,25),('Kessler Edwards',17,23),('Justin Gorham',17,31),("Ze'Rik Onyema",17,25),
('Dante Maddox',27,25),('Gerald Ayayi',24,31),('Charles Brown',14,25),('JP Macura',37,31),('Chad Brown',9,18),('Langston Galloway',9,30),('Riccardo Moraschini',10,19),('Jordan Parks',10,23),('Mirza Alibegovic',20,30),('Jordan Bayehe',11,29),
('Quincy Olivari',22,29),('Semaj Christon',11,23),('Savion Flagg',4,28),('Trentyn Flowers',3,5),('Enoch Boakye',12,20),('Matteo Librizzi',8,18),('Andrea Calzavara',6,17),('Raequan Battle',19,29),('Davide Alviti',21,24),('Gora Camara',3,11),
('Wendell Moore',0,0),('Valentin Chery',14,19),('Alec Peters',0,0),('Aliou Diarra',6,15),('Moses Wright',16,22),('Colbey Ross',24,27),('Izaiah Brockington',0,0),('Arturs Strautins',7,26),('Marko Simonovic',21,25),('Ousmane Diop',3,13),('Federico Zampini',19,36),('Alessandro Lever',5,23),('John Brown',15,22),
('Darius Brown',11,27),('Prentiss Hubb',18,26),('Zac Seljaas',-1,19),('Ismael Kamagate',6,11),('Jaime Echenique',6,15),('Riccardo Rossato',11,26),('Giordano Bortolani',11,18),('John Petrucelli',12,23),('Isaiah Bigelow',14,21),('Derek Ogbeide',5,11),
('Jeff Dowtin',25,29),('Rob Edwards',-1,18),('Trent Frazier',6,22),('Marko Guduric',0,0),('Mouhamet Rassoul Diouf',12,20),('Marco Spissu',5,17),('Andrew Andrews',0,0),('Amar Alibegovic',7,19),('Devon Hall',7,26),('Kyle Wiltjer',13,27),('Markel Brown',16,22),('Carl Wheatle',-5,21),('Giovanni Emejuru',1,11)
])

FORMS={
'Drink Team': [('G','Glynn Watson'),('G','Hunter Hale'),('A','Denzel Valentine'),('A','Mezie Offurum'),('C','Dominik Olejniczak'),('G','Bruno Mascolo'),('G','Amedeo Della Valle'),('A','Giovanni Veronesi'),('A','Jack White'),('C','Paul Eboua'),('G','DeWayne Russell'),('A','Eimantas Bendzius'),('A','Federico Miaschi')],
'Rasta Panthers':[('G','Barford'),('G','Cappelletti'),('A','Roby'),('A','Jakimovski'),('C','McGlynn'),('G','Pecchia'),('G','Durham'),('A','Olinde'),('A','Thor'),('C','Spencer'),('G','Bucarelli'),('C','Mawugbe'),('A','Burnell')],
'CSKA Basket':[('G','Mannion'),('G','Holiday'),('A','Alston'),('C','Tessitori'),('C','Bilan'),('G','Darius Thompson'),('G','Moon'),('A','Edwards'),('A','Gorham'),('C','Onyema'),('G','Moore'),('A','Samuels'),('C',"Tote'")],
'Monza a Spicchi':[('G','Maddox'),('G','Ayayi'),('A','Brown Charles'),('A','Macura'),('C','Brown Chad'),('G','Galloway'),('G','Moraschini'),('A','Parks'),('A','Alibegovic M.'),('C','Bayehe'),('G','Baldasso'),('A','Miles'),('C','Caruso')],
'PBK Dinamo Ronco':[('G','Ramsey'),('G','Christon'),('A','Flagg'),('A','Flowers'),('C','Boakye'),('G','Olivari'),('G','Calzavara'),('A','Battle'),('A','Alviti'),('C','Camara'),('G','Librizzi'),('A','Klintman'),('C','Tarczewski')],
'Maccabi Ruero':[('G','Moore Jr'),('A','Chery'),('A','Peters'),('C','Diarra'),('C','Wright'),('G','Ross'),('G','Brockington'),('A','Strautins'),('A','Simonovic'),('C','Diop'),('G','Zampini'),('A','Lever'),('C','Brown III')],
'Casorzo Lakers':[('G','D Brown'),('G','Hubb'),('A','Seljas'),('C','Kamagate'),('C','Echenique'),('G','Rossato'),('G','Bortolani'),('A','Petruccelli'),('A','Bigelow'),('C','Ogbeide'),('G','Massinburg'),('A','Nikolic'),('C','Tobey')],
'Furleee':[('G','Dowtin'),('G','Edwards Rob'),('G','Frazier'),('A','Guduric'),('C','Diouf'),('G','Spissu'),('G','Andrews'),('A','Alibegovic'),('A','Hall'),('C','Wiltjer'),('G','Markel B'),('A','Wheatle'),('C','Emejuru')]
}
EXPECT={'Drink Team':56,'Rasta Panthers':122,'CSKA Basket':142,'Monza a Spicchi':139,'PBK Dinamo Ronco':93,'Maccabi Ruero':100,'Casorzo Lakers':82,'Furleee':79}
for team,rows in FORMS.items():
    ps=[{'role':r,'name':n,'explicit_single_fbl_role': True, 'status': ('ITA' if norm(n) in FBL_ITA_NAMES else 'STR')} for r,n in rows]
    got,det=score_fbl(ps,S,team)
    assert got==EXPECT[team], (team,got,EXPECT[team],[(x['name'],x['fantasy']) for x in det])
print('FBL benchmark 8/8 OK')

RAW='''pazzoide198
view post Inviato il: 24/9/2026, 11:10
G D Brown
G Hubb
A Seljas
C Kamagate
C Echenique
G Rossato
G Bortolani
A Petruccelli
A Bigelow
C Ogbeide
G Massinburg
A Nikolic
C Tobey
MP Email multiquote
Sprizzaug
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
MP Email multiquote
Alectro93
view post Inviato il: 24/9/2026, 12:23
DRINK TEAM
MODULO: 2-2-1
G Glynn Watson
G Hunter Hale
A Denzel Valentine
A Mezie Offurum
C Dominik Olejniczak
G Bruno Mascolo
G Amedeo Della Valle
A Giovanni Veronesi
A Jack White
C Paul Eboua
G DeWayne Russell
A Eimantas Bendzius
A Federico Miaschi
Modificato da Alectro93
Gabrio Curzio Caimi
view post Inviato il: 25/9/2026, 12:48
RASTA PANTHERS
G BARFORD
G CAPPELLETTI
A ROBY
A JAKIMOVSKI
C MCGLYNN
G PECCHIA
G DURHAM
A OLINDE
A THOR
C SPENCER
Tribuna
G BUCARELLI
C MAWUGBE
A BURNELL
Esclusi
A FERRARI
G SMITH
Modificato da Gabrio Curzio Caimi
bruno21
view post Inviato il: 25/9/2026, 16:17
MONZA A SPICCHI
G MADDOX
G AYAYI
A BROWN Charles
A MACURA
C BROWN Chad
G GALLOWAY
G MORASCHINI
A PARKS
A ALIBEGOVIC M.
C BAYEHE
G BALDASSO
A MILES
C CARUSO
MP Email multiquote
alphonso ford
view post Inviato il: 26/9/2026, 01:44
CSKA BASKET
TITOLARI:
G MANNION
G HOLIDAY
A ALSTON
C TESSITORI
C BILAN
RISERVE:
G DARIUS THOMPSON
G MOON
A EDWARDS
A GORHAM
C ONYEMA
TRIBUNA:
G MOORE
A SAMUELS
C TOTÈ
Modificato da alphonso ford
Filo-Gallo95
view post Inviato il: 26/9/2026, 10:52
Furleee
G Dowtin
G Edwards
G Frazier
A Guduric
C Diouf
G Spissu
G Andrews
A Alibegovic
A Hall
C Wiltjer
G Markel B
A Wheatle
C Emejuru
MP Email multiquote
Libertas_FO
view post Inviato il: 26/9/2026, 14:29
PBK DINAMO RONCO
G Ramsey
G Christon
A Flagg
A Flowers
C Boakye
G Olivari
G Calzavara
A Battle
A Alviti
C Camara
G Librizzi
A Klintman
C Tarczewski'''
parsed,_=parse_page(RAW,'fbl_lba',{},DEFAULT_ROSTERS['fbl_lba'])
expected_names={t:[n for _,n in rows] for t,rows in FORMS.items()}
# Compare normalized/source aliases: exact order/count is the invariant.
for team, exp in expected_names.items():
    got=[p['name'] for p in parsed[team]]
    assert len(got)==13,(team,len(got),got)
    # first post uses Edwards ambiguous; source text must still stay Edwards, never another roster player
    assert [norm(x) for x in got]==[norm(x) for x in exp] or team=='Furleee', (team,got,exp)
assert [norm(x['name']) for x in parsed['Furleee']]==[norm(x) for x in ['Dowtin','Edwards','Frazier','Guduric','Diouf','Spissu','Andrews','Alibegovic','Hall','Wiltjer','Markel B','Wheatle','Emejuru']]
print('FBL parser 8/8 formations OK')
from fantasy import calculate_page
GAMES=[{'players':[{'Giocatore':v[0],'Minuti':v[1],'Valutazione':v[2]} for v in S.values()]}]
calc=calculate_page(RAW,'fbl_lba',GAMES)
for team,base in EXPECT.items():
    assert calc['teams'][team]['score']==base,(team,calc['teams'][team]['score'],base)
print('FBL end-to-end parser+roster+stats+score 8/8 OK')
