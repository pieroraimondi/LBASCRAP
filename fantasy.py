"""Parser/calcolatore leggero per i tre fantabasket collegati ai tabellini."""
import re, unicodedata

ROLES=('PM','G','AP','AG','C')
ROLE_RE=re.compile(r'(?<![A-Z])(?:PM/G|G/AP|AP/AG|AG/C|PM|AP|AG|G|C)(?![A-Z])',re.I)

def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def role_parts(role): return role.upper().split('/') if role else []

def trunc(x): return int(x)  # Python tronca verso zero, come gli esempi del regolamento

def player_index(games):
    out={}
    for g in games:
        for p in g.get('players',[]):
            out[norm(p.get('Giocatore',''))]=(p.get('Giocatore',''), int(p.get('Minuti') or 0), int(p.get('Valutazione') or 0))
    return out

def best_match(name, idx):
    n=norm(name)
    if n in idx:return idx[n]
    nt=set(n.split()); best=None; score=0
    for k,v in idx.items():
        kt=set(k.split()); common=len(nt & kt)
        s=common/max(1,len(nt|kt))
        if s>score: score,best=s,v
    return best if score>=.48 else (name,0,0)

def parse_line(line):
    line=re.sub(r'^\s*(?:\d{1,2}[.)]?\s*)','',line.strip())
    m=ROLE_RE.search(line.upper())
    if not m:return None
    role=m.group(0).upper()
    name=(line[:m.start()]+' '+line[m.end():]).strip(' -–:')
    name=re.sub(r'\b(?:ITA|STR)\b.*$','',name,flags=re.I).strip()
    name=re.sub(r'\s+',' ',name)
    if len(name)<2:return None
    return {'name':name,'role':role}

def parse_formation(text):
    """Estrae in ordine i giocatori riconoscibili da un blocco squadra.
    I primi 5 sono titolari, i successivi 5 panchina, poi 11°/12°.
    """
    players=[]
    for raw in text.splitlines():
        x=parse_line(raw)
        if x: players.append(x)
    return players[:12]

def score_formation(players, stats):
    enriched=[]
    for i,p in enumerate(players):
        real,mins,val=best_match(p['name'],stats)
        enriched.append({**p,'real_name':real,'minutes':mins,'valuation':val,'order':i})

    total=0; details=[]; remaining_by_slot={}
    # Prima calcola titolare + panchinaro assegnati allo slot di formazione.
    # L'11° e il 12° vengono gestiti dopo, globalmente: ciascuno può coprire
    # un solo ruolo compatibile, scegliendo l'allocazione che massimizza il punteggio.
    for i,slot in enumerate(ROLES):
        remaining=40
        for j in (i,i+5):
            if j>=len(enriched) or remaining<=0: continue
            p=enriched[j]
            mins=max(0,p['minutes']); take=min(remaining,mins)
            pts=p['valuation'] if mins<=remaining else trunc(p['valuation']*remaining/mins)
            if take<=0: pts=0
            details.append({'slot':slot,'name':p['real_name'],'role':p['role'],'minutes':mins,'valuation':p['valuation'],'used_minutes':take,'fantasy':pts})
            total+=pts; remaining-=take
        remaining_by_slot[slot]=remaining

    reserves=[enriched[j] for j in (10,11) if j<len(enriched)]

    def reserve_points(p,slot,remaining):
        if slot not in role_parts(p['role']) or remaining<=0: return None
        mins=max(0,p['minutes']); take=min(remaining,mins)
        pts=p['valuation'] if mins<=remaining else trunc(p['valuation']*remaining/mins)
        if take<=0: pts=0
        return pts,take

    # Con al massimo due riserve basta provare tutte le destinazioni possibili.
    choices=[]
    for p in reserves:
        choices.append([None]+[slot for slot in ROLES if slot in role_parts(p['role'])])
    best=(0,[])
    import itertools
    for assignment in itertools.product(*choices) if choices else [()]:
        rem=dict(remaining_by_slot); gain=0; alloc=[]
        for p,slot in zip(reserves,assignment):
            if slot is None: continue
            rp=reserve_points(p,slot,rem[slot])
            if rp is None: continue
            pts,take=rp
            gain+=pts; rem[slot]-=take; alloc.append((p,slot,pts,take))
        if gain>best[0]: best=(gain,alloc)
    total+=best[0]
    for p,slot,pts,take in best[1]:
        details.append({'slot':slot,'name':p['real_name'],'role':p['role'],'minutes':max(0,p['minutes']),'valuation':p['valuation'],'used_minutes':take,'fantasy':pts})
    return total,details

# Ruoli di appoggio per riconoscere i copia/incolla del forum anche quando la formazione
# contiene solo il cognome/nome. Il ruolo scritto nel testo, quando presente, prevale.
_HINTS='''
Nico Mannion|PM/G
Leandro Bolmaro|PM/G
Jason Burnell|AP/AG
Leonardo Tote|AG/C
Moses Wright|C
Ky Bowman|PM/G
Darius Thompson|PM/G
Devon Hall|G/AP
Jack White|AP/AG
Ousmane Diop|C
Stefano Tonut|G/AP
Amedeo Tessitori|C
Kenneth Smith|PM
Jahmius Ramsey|G
Davide Alviti|AP
Andrejs Grazulis|AG
John Brown|AG/C
Garrett Nevels|PM/G
Giordano Bortolani|G
Marko Guduric|G/AP
Matteo Cavallero|AP/AG
Gora Camara|C
Lorenzo Ambrosin|G/AP
Guglielmo Caruso|AG/C
Zan Sisko|PM
Xavier Moon|PM/G
Paul Watson|AP
Isaiah Roby|AG
Enoch Boakye|C
Tommaso Baldasso|PM/G
Octavio Maretto|G
Stefan Nikolic|AP/AG
Andrea Mezzanotte|AG
Federico Poser|C
Andrea Pecchia|G/AP
Valentin Chery|AG/C
Prentiss Hubb|PM/G
Karim Jallow|G/AP
Arturs Strautins|G/AP
Mouhamet Diouf|AG/C
Dominik Olejniczak|C
Jeff Dowtin|PM
Riccardo Rossato|PM/G
Jordan Parks|AP/AG
Justin Gorham|AG
Francesco Candussi|C
Lorenzo Uglietti|PM/G
Antonio Iannuzzi|C
Charlie Moore|PM
Dante Maddox|G
Markel Brown|G/AP
Bobi Klintman|AP/AG
Miro Bilan|C
Davide Moretti|PM/G
Diego Flaccadori|PM/G
Federico Miaschi|G/AP
Brekkott Chapman|AG
Matteo Chillo|AG/C
Lodovico Deangeli|AP/AG
Abramo Canka|G/AP
Alessandro Cappelletti|PM
Denzel Valentine|G/AP
Derrick Alston|AP/AG
Jermaine Samuels|AG
Mike Tobey|C
Dewayne Russell|PM
Riccardo Moraschini|G/AP
Kessler Edwards|AP/AG
Andrea Loro|AP/AG
Alessandro Lever|AG/C
Michele Ruzzier|PM
Francesco Ferrari|AP/AG
Darius Brown|PM
Wendell Moore|G/AP
Trentyn Flowers|AP/AG
Aliou Diarra|AG/C
Chad Brown|C
Alessandro Manfredotti|PM/G
Davide Casarin|PM/G
Giovanni Veronesi|AP
Andrej Jakimovski|AP/AG
Jordan Bayehe|AG/C
Marcus Carr|PM/G
Maximilian Ladurner|C
Marco Spissu|PM
JP Macura|G/AP
Langston Galloway|G/AP
Paul Eboua|AG/C
Skylar Spencer|C
Corey Davis|PM
Leonardo Faggian|G/AP
Liam Udom|G/AP
Isaiah Miles|AG
Nate Renfro|C
Daniel Hackett|PM/G
Sasha Grant|AP/AG
Glynn Watson|PM
Hunter Hale|PM/G
Rob Edwards|G/AP
Eimantas Bendzius|AG
Ike Anigbogu|C
Federico Bonacini|PM/G
Cheikh Niang|G/AP
Mirza Alibegovic|G/AP
Giampaolo Ricci|AP/AG
Giovanni Emejuru|C
Devin Booker|AG/C
Matteo Parravicini|PM
Erick Green|PM/G
Amedeo Della Valle|G
Charles Brown|G/AP
Zac Seljaas|AP/AG
Kyle Wiltjer|AG/C
Matteo Librizzi|PM
Lorenzo Bucarelli|PM/G
Sean McDermott|G/AP
Amar Alibegovic|AG
Kaleb Tarczewski|C
Federico Zampini|PM/G
Leonardo Okeke|AG/C
Colbey Ross|PM
Aljami Durham|PM/G
John Petrucelli|G/AP
Isaiah Bigelow|AP/AG
Ismael Kamagate|C
Leonardo Candi|PM/G
Gerald Ayayi|G
Riccardo Visconti|G/AP
Carl Wheatle|AP/AG
ZeRik Onyema|AG/C
Toto Forray|PM
Joseph Mobio|AP/AG
Andrea Calzavara|PM
RaeQuan Battle|G/AP
Savion Flagg|AP
Alec Peters|AG/C
Jaime Echenique|C
Edoardo Di Meo|PM
Tomas Woldetensae|G/AP
Alessandro Bertini|AP/AG
Marko Simonovic|AG/C
Derek Ogbeide|C
Bruno Mascolo|PM/G
JT Thor|AG/C
Stefano Gentile|PM/G
Caleb Walker|G/AP
Mattia Udom|AP/AG
Matt Tiby|AG/C
Jacorey Williams|C
Stefano Saccoccia|PM
Luca Conti|G/AP
Aristide Mouaha|G/AP
Andrea Lo Biondo|AG/C
Mattia Acunzo|AG/C
Michele Munari|PM/G
Michele Serpilli|AP/AG
Avery Woodson|PM/G
Michele Vitali|G/AP
Tevin Mack|AP/AG
Jeff Brooks|AG
Romello White|C
Eugenio Rota|PM
Alvise Sarto|G/AP
Niccolo De Vico|AP/AG
Simone Zanotti|AG/C
Vittorio Bartoli|AG/C
Lorenzo Caroti|PM
Matteo Piccoli|G/AP
Andrea Cinciarini|PM
Devonte Green|G
Zach Harvey|G/AP
Paulius Sorokas|AG/C
Matteo Berti|C
Lorenzo Penna|PM
Alfredo Boglio|PM/G
Cosimo Costi|AP/AG
Davide Pascolo|AG
Edoardo Tiberti|C
Alberto Conti|G/AP
Francesco Reggiani|G/AP
Blake Francis|PM/G
Riccardo Bolpin|G/AP
Seneca Knight|AP
Dustin Hogue|AG/C
Tommaso Guariglia|C
Costantino Bechi|PM
Joonas Riisma|G/AP
Luca Tozzi|AP/AG
Gabriele Miani|AG/C
Simone Barbante|AG/C
Simone Aromando|AG/C
Fabio Mian|G/AP
David Cournooh|PM/G
Lucio Redivo|PM/G
Jaron Johnson|G/AP
Terry Allen|AG
Leonardo Bettiol|C
Tommaso Vecchiola|PM
Simone Valsecchi|PM/G
Simone Pepe|G/AP
Alessandro Ferrari|AG/C
Giovanni Vildera|C
Federico Massone|PM
Lorenzo Galmarini|AG/C
Davide Denegri|PM/G
Pierpaolo Marini|G/AP
Tyreek Scott-Grayson|G/AP
Massimiliano Moretti|AG/C
Deshawn Stephens|C
Federico Mussini|PM/G
Alessandro Grande|PM/G
Simon Anumba|AP/AG
Giacomo Zanetti|AG/C
Alessandro Simioni|C
Niccolo Filoni|AP/AG
Ivan Mobio|PM/G
Nicola Berdini|PM
Jazz Johnson|G
Marquis Barnett|G/AP
Samuele Moretti|AG/C
Stacy Davis|AG/C
Domenico DArgenzio|PM
Mattia Palumbo|PM/G
Andrija Josovic|AP/AG
Tio Tiagande Willis|AG
Francesco Pellegrino|C
Mattia Ceccato|PM/G
Luca Possamai|C
Matteo Fantinelli|PM
Isaiah Brickner|G
Alessandro Gentile|AP/AG
Hasan Varence|AP/AG
Anthony Morse|C
Alessandro Zanelli|PM
Matteo Imbro|PM/G
Luca Cesana|G/AP
Ethan Esposito|AP/AG
Giacomo DellAgnello|AG/C
Martino Mastellari|G/AP
Mihajlo Jerkovic|AG/C
Jayvon Graves|PM/G
Gabriele Stefanini|G/AP
Keshawn Curry|G/AP
Alexander Cicchetti|AG/C
Bryce Nze|C
Giovanni Tomassini|PM/G
Lorenzo Saccaggi|PM/G
Nazzareno Italiano|AP/AG
Ion Lupusor|AG
Davide Bruttini|C
Saverio Bartoli|PM
Giacomo Leardini|AP/AG
Matteo Schina|PM
Cody Demps|G/AP
Raphael Gaspardo|AP/AG
Regimantas Miniotas|AG/C
Marcus Santos Silva|C
Diego Monaldi|PM/G
Matteo Accorsi|PM/G
Marco Mollura|AP/AG
Damir Hadzic|AG/C
Angelo Del Chiaro|C
Lorenzo Calbini|PM/G
Vincenzo Guaiana|G/AP
'''
ROLE_HINTS={norm(n):r for n,r in (line.split('|',1) for line in _HINTS.strip().splitlines())}

def infer_line(line):
    parsed=parse_line(line)
    if parsed:return parsed
    clean=re.sub(r'^\s*(?:\d{1,2}[.)]?\s*)','',line.strip())
    n=norm(clean)
    best=None
    for key,role in ROLE_HINTS.items():
        if key and (key in n or n in key) and len(n)>=4:
            if best is None or len(key)>len(best[0]): best=(key,role)
    if best:
        # usa il testo originale come nome, ripulito da annotazioni comuni
        name=re.sub(r'\s+(?:ITA|STR)\b.*$','',clean,flags=re.I).strip()
        return {'name':name,'role':best[1]}
    return None

def parse_formation(text):
    players=[]
    for raw in text.splitlines():
        x=infer_line(raw)
        if x: players.append(x)
    return players[:12]

TEAM_NAMES={
'pcf_lba':['I Mollo','Casorzo Lakers','Pikkiatelli Bodio',"PCF 'Facu' Mastelle",'Zalgiris','Domonator','Basket Padova','Olimpija Ruero','Dinamo Lucura','Springfields Isotopes','Springfield','Birrareal','Rasta Panthers'],
'pcf_lnp':['Casorzo Lakers','Chi Burdel','Zalgiris','I Mollo','Si Ok E Poi?','Teamcento','Team Cento','Olimpija Ruero','Liverpaul','Rasta Panthers','Butter Beater'],
'fbl_lba':[]}

def detect_team_line(line, competition):
    n=norm(line)
    for team in TEAM_NAMES.get(competition,[]):
        tn=norm(team)
        if n==tn or (len(n)<45 and tn in n and not ROLE_RE.search(line.upper())): return team
    return None

def parse_page(text, competition):
    lines=text.replace('\r','').split('\n')
    starts=[]
    for i,line in enumerate(lines):
        t=detect_team_line(line.strip(' *'),competition)
        if t: starts.append((i,t))
    forms={}
    for pos,(i,t) in enumerate(starts):
        end=starts[pos+1][0] if pos+1<len(starts) else len(lines)
        block='\n'.join(lines[i+1:end])
        p=parse_formation(block)
        if len(p)>=5 and (t not in forms or len(p)>len(forms[t])): forms[t]=p
    # accoppiamenti: cerca righe con due nomi squadra e trattino lungo/corto
    matchups=[]
    for line in lines:
        if '–' not in line and ' - ' not in line: continue
        found=[]
        nl=norm(line)
        for team in TEAM_NAMES.get(competition,[]):
            if norm(team) in nl: found.append(team)
        # preserva ordine di apparizione
        found=sorted(set(found), key=lambda t:nl.find(norm(t)))
        if len(found)>=2 and found[0]!=found[1]:
            pair=(found[0],found[1])
            if pair not in matchups: matchups.append(pair)
    return forms,matchups

def calculate_page(text, competition, games):
    forms,matchups=parse_page(text,competition)
    stats=player_index(games)
    teams={}
    for team,players in forms.items():
        score,details=score_formation(players,stats)
        teams[team]={'score':score,'players':players,'details':details}
    results=[]
    for home,away in matchups:
        if home in teams and away in teams:
            results.append({'home':home,'away':away,'home_score':teams[home]['score']+3,'away_score':teams[away]['score'],'home_bonus':3})
    return {'teams':teams,'matchups':results,'detected':list(forms)}
