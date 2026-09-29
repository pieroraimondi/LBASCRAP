from fantasy import calculate_page
raw='''Maccabi Ruero
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
C BROWN III'''
rows=[('Wendell Moore',0,0),('Valentin Chery',19,14),('Alec Peters',0,0),('Aliou Diarra',15,6),('Moses Wright',22,16),('Colbey Ross',27,24),('Izaiah Brockington',0,0),('Arturs Strautins',26,7),('Marko Simonovic',25,21),('Ousmane Diop',13,3),('Federico Zampini',36,19),('Alessandro Lever',23,5),('John Brown',22,15)]
g=[{'players':[{'Giocatore':n,'Minuti':m,'Valutazione':v} for n,m,v in rows]}]
r=calculate_page(raw,'fbl_lba',g,{})['teams']['Maccabi Ruero']
assert r['score']==100, r
names=[(d['kind'],d['name'],d['fantasy']) for d in r['details']]
assert ('tribuna','Federico Zampini',6) in names, names
assert ('tribuna','Alessandro Lever',3) in names, names
assert sum(1 for d in r['details'] if d['kind']=='tribuna')==2, names
print('Maccabi tribuna final-ITA regression OK: 100')
