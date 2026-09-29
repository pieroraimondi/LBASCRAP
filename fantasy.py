"""Parser/calcolatore leggero per i tre fantabasket collegati ai tabellini."""
import re, unicodedata, math
from default_rosters import DEFAULT_ROSTERS
from difflib import SequenceMatcher

ROLES=('PM','G','AP','AG','C')
ROLE_RE=re.compile(r'(?<![A-Z])(?:PM/G|G/AP|AP/AG|AG/C|PM|AP|AG|G|A|C)(?![A-Z])',re.I)

def norm(s):
    # Uniforma prima apostrofi tipografici e trattini Unicode: se li eliminassimo
    # durante la conversione ASCII, Dell’Agnello diventerebbe "dellagnello" mentre
    # Dell'Agnello diventerebbe "dell agnello", creando due identita diverse.
    s=str(s).translate(str.maketrans({'’':"'",'‘':"'",'`':"'",'´':"'",'‐':'-','‑':'-','–':'-','—':'-'}))
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def role_parts(role): return role.upper().split('/') if role else []

def trunc(x): return math.floor(x)  # arrotondamento sempre per difetto, anche per valori negativi

def player_index(games, learned_aliases=None):
    out={}
    for g in games:
        for p in g.get('players',[]):
            out[norm(p.get('Giocatore',''))]=(p.get('Giocatore',''), int(p.get('Minuti') or 0), int(p.get('Valutazione') or 0))
    # Il dizionario appreso dal browser punta sempre a un nome realmente presente
    # nei tabellini correnti: se il giocatore non esiste piu', l'alias non viene usato.
    for raw,canonical in (learned_aliases or {}).items():
        ck=norm(canonical)
        if ck in out:
            out[norm(raw)]=out[ck]
    return out

def best_match(name, idx):
    """Resolve a *canonical* player identity against the current boxscore.

    Safety invariant: a player missing from the boxscore is a DNP (0/0), never
    another player with a similar surname. Fuzzy matching is allowed only when
    first-name and surname evidence are both compatible; surname-only matching
    is reserved for genuinely one-token inputs.
    """
    requested=name
    n=norm(name)
    alias=PLAYER_ALIASES.get(n) if 'PLAYER_ALIASES' in globals() else None
    if alias:
        n=norm(alias); requested=alias
    if n in idx: return idx[n]
    if not n: return (name,0,0)

    nt=n.split()
    suffixes={'jr','sr','ii','iii','iv','v'}
    core=[t for t in nt if t not in suffixes]

    # Full identity, allowing only suffix/punctuation differences.
    exactish=[]
    for k,v in idx.items():
        kt=k.split(); kcore=[t for t in kt if t not in suffixes]
        if core==kcore or (len(core)>=2 and (n.startswith(k+' ') or k.startswith(n+' '))):
            exactish.append(v)
    uniq={norm(v[0]):v for v in exactish}
    if len(uniq)==1: return next(iter(uniq.values()))

    # A one-token forum abbreviation may use a unique surname. Full names may NOT:
    # this is precisely what used to turn Wendell Moore into Charlie Moore.
    if len(core)==1:
        token=core[0]
        hits=[]
        for k,v in idx.items():
            kc=[t for t in k.split() if t not in suffixes]
            if kc and (kc[-1]==token or kc[0]==token): hits.append(v)
        uniq={norm(v[0]):v for v in hits}
        if len(uniq)==1:return next(iter(uniq.values()))

    # Conservative typo tolerance for full identities: first and last token must
    # independently agree. A shared surname alone can never select a player.
    if len(core)>=2:
        ranked=[]
        for k,v in idx.items():
            kc=[t for t in k.split() if t not in suffixes]
            if len(kc)<2: continue
            first=SequenceMatcher(None,core[0],kc[0]).ratio()
            last=SequenceMatcher(None,core[-1],kc[-1]).ratio()
            whole=SequenceMatcher(None,' '.join(core),' '.join(kc)).ratio()
            # Middle names/initials may appear only in the official feed
            # (e.g. Charlie Moore -> Charlie Edward Moore). Exact first+last is
            # therefore a strong identity even when whole-string similarity drops.
            if (first>=.98 and last>=.98) or (first>=.72 and last>=.82 and whole>=.84):
                identity=max(whole, .96 if first>=.98 and last>=.98 else whole)
                ranked.append((identity,first,last,v))
        ranked.sort(key=lambda x:(-x[0],-x[1],-x[2],norm(x[3][0])))
        if ranked and (len(ranked)==1 or ranked[0][0]-ranked[1][0]>=.05):
            return ranked[0][3]

    # Canonical player not present in this day's stats => DNP/non-convocato.
    return (requested,0,0)

def parse_line(line):
    line=re.sub(r'^\s*(?:\d{1,2}[.)]?\s*)','',line.strip())
    m=ROLE_RE.search(line.upper())
    if not m:return None
    role=m.group(0).upper()
    name=(line[:m.start()]+' '+line[m.end():]).strip(' -–:')
    # Nei post PCF il ruolo viene spesso scritto due volte (es.
    # "PM Cinciarini PM" oppure "G Green G"). Dopo aver individuato
    # il ruolo, elimina gli eventuali altri token-ruolo: altrimenti il nome
    # diventa "Cinciarini PM" e il matching col tabellino fallisce.
    name=ROLE_RE.sub(' ',name)
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
    """Motore PCF, replica letterale del foglio ``calcolatore``.

    Ordine formazione: 5 titolari (PM,G,AP,AG,C), 5 panchinari negli stessi
    slot, poi 11° e 12°. I primi dieci NON vengono riallocati in base al ruolo
    naturale: il loro slot e' determinato dalla posizione nella formazione.

    L'11°/12° usa invece il ruolo dichiarato e la matrice di compatibilita'
    dell'Excel. Un doppio ruolo dispone della SOMMA dei minuti residui dei due
    slot compatibili. Dopo l'11°, i suoi minuti reali vengono sottratti (con
    minimo zero) da ciascuno slot compatibile, esattamente come nelle formule
    H26:H34 del foglio. Il 12° usa i residui cosi' ottenuti.
    """
    enriched=[]
    for i,p in enumerate(players[:12]):
        real,mins,val=best_match(p['name'],stats)
        enriched.append({**p,'real_name':real,'minutes':max(0,mins),'valuation':val,'order':i})

    total=0; details=[]

    # Excel J5:J9: titolari, cap individuale a 40', con FLOOR.
    for i,slot in enumerate(ROLES):
        if i>=len(enriched): continue
        p=enriched[i]; mins=p['minutes']; val=p['valuation']
        raw = (val/mins*40) if mins>40 and mins else val
        pts=trunc(raw)
        total+=pts
        details.append({'slot':slot,'kind':'titolare','name':p['real_name'],'role':p['role'],
                        'minutes':mins,'valuation':val,'used_minutes':min(40,mins),'fantasy':pts})

    # Excel J11:J15: panchina. Il residuo usa 40 - minuti REALI del titolare
    # (non MIN(40,...)); e' intenzionale per aderire al foglio alla lettera.
    for i,slot in enumerate(ROLES):
        j=i+5
        if j>=len(enriched): continue
        p=enriched[j]; mins=p['minutes']; val=p['valuation']
        starter_mins=enriched[i]['minutes'] if i<len(enriched) else 0
        available=40-starter_mins
        if mins==0:
            raw=0
        elif mins>available:
            raw=val/mins*available
        else:
            raw=val
        pts=trunc(raw)
        total+=pts
        details.append({'slot':slot,'kind':'panchina','name':p['real_name'],'role':p['role'],
                        'minutes':mins,'valuation':val,'used_minutes':max(0,min(mins,available)),'fantasy':pts})

    # Excel G26:G30: residui dopo i primi dieci, qui invece con MIN(40,...).
    rem={}
    for i,slot in enumerate(ROLES):
        sm=enriched[i]['minutes'] if i<len(enriched) else 0
        bm=enriched[i+5]['minutes'] if i+5<len(enriched) else 0
        rem[slot]=max(0,40-(min(40,sm)+min(40,bm)))

    def compatible_slots(role):
        # Matrice B26:D30 / E26:E34 dell'Excel.
        parts=role_parts(role)
        return [slot for slot in ROLES if slot in parts]

    # 11° e 12°: disponibilita' = somma residui dei ruoli compatibili.
    # Dopo ogni giocatore, i suoi minuti vengono sottratti da OGNI residuo
    # compatibile (non distribuiti/ottimizzati): e' la logica esatta del foglio.
    for j,label in ((10,'11°'),(11,'12°')):
        if j>=len(enriched): continue
        p=enriched[j]; mins=p['minutes']; val=p['valuation']
        slots=compatible_slots(p['role'])
        available=sum(rem[s] for s in slots)
        raw=(val/mins*available) if mins>available and mins else val
        pts=trunc(raw)
        total+=pts
        details.append({'slot':'/'.join(slots) if slots else p['role'],'kind':label,
                        'name':p['real_name'],'role':p['role'],'minutes':mins,'valuation':val,
                        'used_minutes':min(mins,available),'fantasy':pts,'available_minutes':available})
        for slot in slots:
            rem[slot]=max(0,rem[slot]-mins)

    return total,details

def score_fbl(players, stats, team=None):
    """Motore FBL.

    Posizioni 1-5 titolari, 6-10 riserve abbinate, 11-13 tribuna in ordine.
    La tribuna puo' essere usata SOLO se nella formazione di giornata il singolo
    tribunaro ha un ruolo FBL esplicito e singolo (G, A oppure C): i doppi ruoli
    del roster non valgono in tribuna e non vengono mai dedotti automaticamente.

    Un tribunaro compatibile entra soltanto per un DNP dei primi dieci e soltanto
    se la sostituzione mantiene almeno 3 ITA nei dieci giocatori effettivi. Se lo
    status ITA/STR necessario a verificare il vincolo non e' disponibile nel roster,
    la sostituzione di tribuna viene prudentemente rifiutata: il vincolo non puo'
    essere dato per rispettato per supposizione.
    """
    enriched=[]
    for i,p in enumerate(players[:13]):
        real,mins,val=best_match(p['name'],stats)
        enriched.append({**p,'real_name':real,'minutes':max(0,mins),'valuation':val,'order':i})

    total=0; details=[]; used_tribuna=set()
    # Gli indici attivi iniziali sono i 10 schierati. Una sostituzione di tribuna
    # rimuove il DNP e aggiunge il tribunaro; la riserva promossa resta gia' nei 10.
    active=set(range(min(10,len(enriched))))

    def status_known(indices):
        return all(enriched[k].get('status') in ('ITA','STR') for k in indices)

    def italian_count(indices):
        return sum(enriched[k].get('status')=='ITA' for k in indices)

    def take_tribuna(target_fbl_role, dnp_index):
        # target_fbl_role e' lo slot FBL da coprire: G/A/C. L'ordine 11->12->13
        # e' tassativo; un candidato non utilizzabile viene saltato e si prova il successivo.
        target=(target_fbl_role or '').upper()
        for k in range(10,len(enriched)):
            if k in used_tribuna: continue
            p=enriched[k]
            # In tribuna conta SOLO il ruolo singolo scritto nella formazione.
            if not p.get('explicit_single_fbl_role') or p.get('role') not in ('G','A','C'):
                continue
            if p.get('role') != target:
                continue
            trial=(active-{dnp_index})|{k}
            # Il vincolo e' verificato positivamente: servono almeno 3 status ITA noti.
            # Gli status mancanti non vengono mai contati come italiani per supposizione.
            if italian_count(trial) < 3:
                continue
            used_tribuna.add(k)
            active.discard(dnp_index); active.add(k)
            return p
        return None

    # Gli slot FBL sono determinati dalla formazione postata, non dal ruolo naturale.
    # Il ruolo del titolare deve quindi essere G/A/C; per eventuali input legacy AP/AG/C
    # normalizziamo solo gli slot 1-10, mai la tribuna.
    def fbl_slot_role(p):
        r=(p.get('role') or '').upper()
        if r=='G' or r=='PM' or r=='PM/G': return 'G'
        if r in ('A','AP','AG','G/AP','AP/AG'): return 'A'
        if r in ('C','AG/C'): return 'C'
        return r

    for i in range(min(5,len(enriched))):
        starter=enriched[i]
        bench=enriched[i+5] if i+5<len(enriched) else None
        slot_role=fbl_slot_role(starter)
        if starter['minutes']==0 and bench is not None:
            first=bench
            second=take_tribuna(slot_role, i)
            kinds=('riserva promossa','tribuna')
        else:
            first=starter
            if bench is not None and bench['minutes']==0:
                second=take_tribuna(slot_role, i+5)
                kinds=('titolare','tribuna')
            else:
                second=bench
                kinds=('titolare','riserva')
        rem=40
        for p,kind in ((first,kinds[0]),(second,kinds[1])):
            if p is None or rem<=0: continue
            mins=p['minutes']; take=min(rem,mins)
            if take<=0: pts=0
            elif mins<=rem: pts=p['valuation']
            else: pts=trunc(p['valuation']*rem/mins)
            total+=pts; rem-=take
            details.append({'slot':i+1,'slot_role':slot_role,'kind':kind,'name':p['real_name'],'role':p['role'],
                            'status':p.get('status',''),'minutes':mins,'valuation':p['valuation'],
                            'used_minutes':take,'fantasy':pts})
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

def infer_line(line, learned_aliases=None):
    parsed=parse_line(line)
    if parsed:return parsed
    clean=re.sub(r'^\s*(?:\d{1,2}[.)]?\s*)','',line.strip())
    n=norm(clean)
    # Anche le formazioni senza ruoli espliciti possono contenere abbreviazioni
    # o refusi (Coornoh, J Johnson...). Se esiste un alias canonico, usalo per
    # ricavare il ruolo dal roster-hint senza perdere la posizione nel quintetto.
    alias=(learned_aliases or {}).get(clean) or (learned_aliases or {}).get(n) or (PLAYER_ALIASES.get(n) if 'PLAYER_ALIASES' in globals() else None)
    if alias and norm(alias) in ROLE_HINTS:
        return {'name':clean,'role':ROLE_HINTS[norm(alias)]}
    best=None
    for key,role in ROLE_HINTS.items():
        if key and (key in n or n in key) and len(n)>=4:
            if best is None or len(key)>len(best[0]): best=(key,role)
    if best:
        # usa il testo originale come nome, ripulito da annotazioni comuni
        name=re.sub(r'\s+(?:ITA|STR)\b.*$','',clean,flags=re.I).strip()
        return {'name':name,'role':best[1]}
    return None

def _similarity(a,b):
    a,b=norm(a),norm(b)
    if not a or not b:return 0.0
    if a==b:return 1.0
    at,bt=a.split(),b.split()
    score=SequenceMatcher(None,a,b).ratio()
    if at[-1]==bt[-1]: score=max(score,.88)
    elif at[-1] in bt or bt[-1] in at: score=max(score,.72)
    if set(at)&set(bt): score=max(score, len(set(at)&set(bt))/max(len(set(at)),len(set(bt))))
    return score

def parse_roster_page(text, competition):
    """Legge un copia-incolla della pagina roster. Restituisce roster per squadra.
    Accetta sia il formato PCF numerato sia il formato FBL ruolo+cognome+crediti.
    """
    lines=text.replace('\r','').split('\n'); starts=[]
    for i,line in enumerate(lines):
        t=detect_team_line(line.strip(' *\\'),competition)
        if t: starts.append((i,t))
    rosters={}
    for pos,(i,team) in enumerate(starts):
        end=starts[pos+1][0] if pos+1<len(starts) else len(lines)
        players=[]
        for raw in lines[i+1:end]:
            line=raw.strip().strip('\\').strip()
            if not line or line.startswith('---') or re.search(r'roster\s+\d+/',line,re.I): continue
            # PCF: 026 Darius Thompson PM/G ITA MILANO 25
            m=re.match(r'^\s*\d{1,3}\s+(.+?)\s+(PM/G|G/AP|AP/AG|AG/C|PM|AP|AG|G|C)\s+(ITA|STR)\b',line,re.I)
            if m:
                players.append({'name':m.group(1).strip(),'role':m.group(2).upper(),'status':m.group(3).upper()}); continue
            # FBL roster: G SMITH 1 / GA BARFORD 5 / AC THOR 43
            m=re.match(r'^\s*(PM/G|G/AP|AP/AG|AG/C|GA|AC|PM|AP|AG|G|A|C)\s+(.+?)(?:\s+\d+(?:\s*\(.*?\))?)?\s*$',line,re.I)
            if m and len(m.group(2))<55:
                role=m.group(1).upper(); role={'GA':'G/AP','AC':'AG/C','A':'AP/AG' if competition!='fbl_lba' else 'A'}.get(role,role)
                name=m.group(2).strip()
                name=re.sub(r'\s+\d+(?:\s*\(.*?\))?$','',name).strip()
                status=''
                sm=re.search(r'\b(ITA|STR)\b',name,re.I)
                if sm:
                    status=sm.group(1).upper(); name=(name[:sm.start()]+' '+name[sm.end():]).strip()
                    name=re.sub(r'\s+\d+(?:\s*\(.*?\))?$','',name).strip()
                if len(name)>1: players.append({'name':name,'role':role,'status':status})
        # dedup
        seen=set(); clean=[]
        for x in players:
            k=norm(x['name'])
            if k and k not in seen: seen.add(k); clean.append(x)
        if clean: rosters[canonical_team(team,competition)]=clean
    return rosters

def roster_match(raw, role, roster_players, learned_aliases=None, team=None):
    """Match permissivo ma confinato al roster della squadra.
    Ritorna (nome, confidence, candidati). Un candidato unico ragionevole viene accettato.
    """
    aliases=learned_aliases or {}
    scoped = f"{norm(team)}|||{norm(raw)}" if team else None
    alias=(aliases.get(scoped) if scoped else None) or aliases.get(raw) or aliases.get(norm(raw))
    # Un alias appreso non e' autoritativo per sempre: deve ancora appartenere
    # al roster ATTUALE della squadra. Questo impedisce a una vecchia convalida
    # errata (es. Wendell Moore -> Charlie Moore) di contaminare giornate future.
    if alias:
        # Un alias appreso puo' essere riutilizzato solo se e' ancora coerente con
        # l'identita' testuale corrente. Questo blocca vecchie convalide avvelenate
        # (es. CHERY -> DIARRA) pur conservando abbreviazioni legittime come
        # MOORE JR -> Wendell Moore o cognome -> nome completo.
        raw_tokens=norm(raw).split(); alias_tokens=norm(alias).split()
        lexical_ok=False
        if raw_tokens and alias_tokens:
            overlap=set(raw_tokens) & set(alias_tokens)
            lexical_ok=bool(overlap) or _similarity(raw,alias)>=.72
            if len(raw_tokens)==1:
                lexical_ok=raw_tokens[0] in alias_tokens or _similarity(raw,alias)>=.82
        in_roster=(not roster_players or any(norm(alias)==norm(p.get('name','')) for p in roster_players))
        if in_roster and lexical_ok:
            return alias,1.0,[alias]
    if not roster_players:return raw,0.0,[]
    wanted=set(role_parts(role))
    ranked=[]
    for p in roster_players:
        prole=p.get('role',''); compat=not wanted or bool(wanted & set(role_parts(prole))) or role in ('A','G','C')
        sc=_similarity(raw,p['name']) + (.07 if compat else -.10)
        ranked.append((sc,p['name'],prole))
    ranked.sort(reverse=True)
    candidates=[x[1] for x in ranked[:3] if x[0]>=.30]
    if not ranked:return raw,0.0,[]
    best=ranked[0]; second=ranked[1][0] if len(ranked)>1 else 0
    # dentro un roster di 15 giocatori possiamo essere molto piu permissivi
    if best[0]>=.48 and (best[0]-second>=.04 or best[0]>=.78): return best[1],best[0],candidates
    return raw,best[0],candidates

def parse_formation(text, learned_aliases=None, roster_players=None, competition='pcf_lba'):
    """Legge *solo* i giocatori effettivamente scritti nel post, nell'ordine scritto.

    Regola fondamentale: il roster NON genera mai una formazione. Viene usato soltanto
    per riconoscere una riga che esiste davvero nel post (es. ``Sisko`` -> Zan Sisko).
    Una riga non presente nel post non può quindi comparire tra titolari/panchina.
    """
    players=[]
    max_players = 13 if competition=='fbl_lba' else 12
    started=False

    # Marker che chiudono realmente il contenuto del post. Dopo uno di questi non
    # cerchiamo più giocatori: firme, palmares e post successivi non possono entrare.
    hard_stop=tuple(norm(x) for x in (
        'modificato da','messaggio privato','multiquote','view post','inviato il',
        'forza basket','www','youtube','myspace','sign by','palmares',
        'campione serie','terzo posto','promozione in serie','fanta world cup'
    ))
    # Righe di servizio che possono stare in mezzo alla formazione ma non sono giocatori.
    # I confronti avvengono sulla stessa normalizzazione usata per la riga: in questo
    # modo "Punteggio: 0", "Stato:" e "Provenienza: Sardegna" non possono mai
    # essere scambiati per giocatori e spostare tutti gli slot della formazione.
    soft_skip=tuple(norm(x) for x in (
        'titolari','riserve','panchina','tribuna','esclusi','modulo',
        'gruppo','messaggi','punteggio','provenienza','stato','avatar',
        'advanced member','member','admin pcf forum','lega a1','lega a2','dnb','dnc',
        'promozione','eurochallenge','olympic','c regionale','fantabasket'
    ))

    for raw in text.splitlines():
        line=raw.strip().strip('\\').strip()
        if not line: continue
        nl=norm(line)
        # Il nome della squadra ripetuto nel post è solo un'intestazione, mai un giocatore.
        if detect_team_line(line.strip(' *'), competition):
            continue
        if started and any(z in nl for z in hard_stop):
            break
        if any(nl==z or nl.startswith(z) for z in soft_skip):
            continue
        # Prima prova la sintassi esplicita del post: ruolo + nome / nome + ruolo.
        x=parse_line(line)
        if x:
            # Evita che frasi narrative contenenti una singola A/G/C vengano scambiate
            # per giocatori. Una riga giocatore deve anche corrispondere al roster se
            # il roster della squadra è disponibile.
            if roster_players:
                canonical,conf,_=roster_match(x['name'],x.get('role',''),roster_players,learned_aliases)
                if conf < .40:
                    if started: continue
                    else: continue
            x['explicit_single_fbl_role']=bool(competition=='fbl_lba' and x.get('role') in ('G','A','C') and ROLE_RE.search(line.upper()))
            players.append(x); started=True
        else:
            # Formati PCF senza ruolo (es. "Watson Jr", "Hale", ...): accettiamo
            # esclusivamente una riga che identifica un giocatore DEL roster corrente.
            if not roster_players or len(line)>55: continue
            clean=re.sub(r'^\s*(?:\d{1,2}[.)]?\s*)','',line).strip()
            canonical,conf,_=roster_match(clean,'',roster_players,learned_aliases)
            if conf>=.48:
                rp=next((p for p in roster_players if norm(p['name'])==norm(canonical)),None)
                if rp:
                    players.append({'name':clean,'role':rp.get('role',''),'explicit_single_fbl_role':False}); started=True
        if len(players)>=max_players:
            break
    return players

# Alias frequenti nei post FBL: servono a disambiguare cognomi/abbreviazioni.
PLAYER_ALIASES={
    norm(k):v for k,v in {
    'D Brown':'Darius Brown','Hubb':'Prentiss Hubb','Seljas':'Zac Seljaas','Kamagate':'Ismael Kamagate',
    'Echenique':'Jaime Echenique','Rossato':'Riccardo Rossato','Bortolani':'Giordano Bortolani',
    'Petruccelli':'John Petrucelli','Bigelow':'Isaiah Bigelow','Ogbeide':'Derek Ogbeide','Massinburg':'C.J. Massinburg',
    'Nikolic':'Stefan Nikolic','Tobey':'Mike Tobey','Moore Jr':'Wendell Moore','Chery':'Valentin Chery',
    'Peters':'Alec Peters','Diarra':'Aliou Diarra','Wright':'Moses Wright','Ross':'Colbey Ross',
    'Brockington':'Izaiah Brockington','Strautins':'Arturs Strautins','Simonovic':'Marko Simonovic',
    'Diop':'Ousmane Diop','Zampini':'Federico Zampini','Lever':'Alessandro Lever','Brown III':'John Brown',
    'Glynn Watson':'Glynn Watson','Hunter Hale':'Hunter Hale','Denzel Valentine':'Denzel Valentine',
    'Mezie Offurum':'Mezie Offurum','Dominik Olejniczak':'Dominik Olejniczak','Amedeo Della Valle':'Amedeo Della Valle',
    'Jack White':'Jack White','Paul Eboua':'Paul Eboua','DeWayne Russell':'DeWayne Russell','Eimantas Bendzius':'Eimantas Bendzius',
    'Barford':'Jaylen Barford','Cappelletti':'Alessandro Cappelletti','Roby':'Isaiah Roby','Jakimovski':'Andrej Jakimovski',
    'McGlynn':'Nick McGlynn','Pecchia':'Andrea Pecchia','Durham':'Aljami Durham','Olinde':'Louis Olinde',
    'Thor':'JT Thor','Spencer':'Skylar Spencer','Bucarelli':'Lorenzo Bucarelli','Mawugbe':'Selom Mawugbe','Burnell':'Jason Burnell',
    'Maddox':'Dante Maddox','Ayayi':'Gerald Ayayi','Brown Charles':'Charles Brown','Macura':'JP Macura','Brown Chad':'Chad Brown',
    'Galloway':'Langston Galloway','Moraschini':'Riccardo Moraschini','Parks':'Jordan Parks','Alibegovic M.':'Mirza Alibegovic',
    'Bayehe':'Jordan Bayehe','Baldasso':'Tommaso Baldasso','Miles':'Isaiah Miles','Caruso':'Guglielmo Caruso',
    'Mannion':'Niccolo Mannion','Holiday':'Aaron Holiday','Alston':'Derrick Alston','Tessitori':'Amedeo Tessitori','Bilan':'Miro Bilan',
    'Darius Thompson':'Darius Thompson','Moon':'Xavier Moon','Edwards':'Kessler Edwards','Gorham':'Justin Gorham','Onyema':"Ze'Rik Onyema",
    'Moore':'Charlie Edward Moore','Samuels':'Jermaine Samuels',"Tote'":'Leonardo Tote',
    'Dowtin':'Jeff Dowtin','Edwards Rob':'Rob Edwards','Frazier':'Trent Frazier','Guduric':'Marko Guduric','Diouf':'Mouhamet Rassoul Diouf',
    'Spissu':'Marco Spissu','Andrews':'Andrew Andrews','Alibegovic':'Amar Alibegovic','Hall':'Devon Hall','Wiltjer':'Kyle Wiltjer',
    'Markel B':'Markel Brown','Wheatle':'Carl Wheatle','Emejuru':'Giovanni Emejuru',
    'Ramsey':"Jahmi'us Ramsey",'Christon':'Semaj Christon','Flagg':'Savion Flagg','Flowers':'Trentyn Flowers','Boakye':'Enoch Boakye',
    'Olivari':'Quincy Olivari','Calzavara':'Andrea Calzavara','Battle':'Raequan Battle','Alviti':'Davide Alviti','Camara':'Gora Camara',
    'Librizzi':'Matteo Librizzi','Klintman':'Bo Klintman','Tarczewski':'Kaleb Tarczewski',
    # abbreviazioni/refusi ricorrenti PCF LNP
    'Coornoh':'David Cournooh','Cournooh':'David Cournooh','J Johnson':'Jaron Johnson',
    'A Ferrari':'Alessandro Ferrari','Gentile Ale':'Alessandro Gentile',
    "Mimmo D'Argenzio":"Domenico D'Argenzio",'D Argenzio':"Domenico D'Argenzio",
    'Santos Silva':'Marcus Santos Silva','Riisma':'Joonas Riismaa',
    'Joonas Riisma':'Joonas Riismaa'}.items()
}

# Status FBL incorporati per il roster corrente. Sono metadati di roster, non
# eccezioni di calcolo: un roster incollato con ITA/STR li sovrascrive. Servono
# anche quando l'utente usa il roster fallback incorporato.
FBL_ITA_NAMES={norm(x) for x in '''
Alessandro Cappelletti
Lorenzo Bucarelli
Andrea Pecchia
Francesco Ferrari
Tommaso Baldasso
Riccardo Moraschini
Riccardo Visconti
Guglielmo Caruso
Amedeo Della Valle
Bruno Mascolo
Federico Miaschi
Giovanni Veronesi
Paul Eboua
Federico Zampini
Arturs Strautins
Alessandro Lever
Andrea Calzavara
Matteo Librizzi
Alessandro Bertini
Davide Alviti
Gora Camara
Nico Mannion
Amedeo Tessitori
Leonardo Tote
Riccardo Rossato
Giordano Bortolani
Davide Moretti
Stefan Nikolic
Marco Spissu
Amar Alibegovic
Karim Jallow
Giovanni Emejuru
'''.strip().splitlines()}

TEAM_OWNERS={
'pcf_lba':{
'hot sauce 7':'I Mollo','armando87':"PCF 'Facu' Mastelle",'ronartest':'Basket Padova','gabrio curzio caimi':'Rasta Panthers','sza':'Dinamo Lucura','marco zatti':'Casorzo Lakers','sprizzaug':'Olimpija Ruero','domonator8':'Domonator','roby gullo':'Springfields Isotopes','alex100':'Pikkiatelli Bodio','chi8':'Birrareal','arvydas':'Zalgiris'},
'pcf_lnp':{
'paga92':'Si Ok E Poi?','hot sauce 7':'I Mollo','alberto musto':'Team Cento','gabrio curzio caimi':'Rasta Panthers','marco zatti':'Casorzo Lakers','bunt72':'Butter Beater','arvydas':'Zalgiris','filo gallo95':'Chi Burdel','paoloc861':'Liverpaul','sprizzaug':'Olimpija Ruero'},
'fbl_lba':{'pazzoide198':'Casorzo Lakers','sprizzaug':'Maccabi Ruero','alectro93':'Drink Team','gabrio curzio caimi':'Rasta Panthers','bruno21':'Monza a Spicchi','alphonso ford':'CSKA Basket','filo gallo95':'Furleee','libertas fo':'PBK Dinamo Ronco'}
}

TEAM_NAMES={
'pcf_lba':['I Mollo','Casorzo Lakers','Pikkiatelli Bodio',"PCF 'Facu' Mastelle",'Zalgiris','Domonator','Basket Padova','Olimpija Ruero','Dinamo Lucura','Springfields Isotopes','Springfield','Birrareal','Rasta Panthers'],
'pcf_lnp':['Casorzo Lakers','Chi Burdel','Zalgiris','I Mollo','Si Ok E Poi?','Teamcento','Team Cento','Olimpija Ruero','Liverpaul','Rasta Panthers','Butter Beater'],
'fbl_lba':['Drink Team','Rasta Panthers','CSKA Basket','Monza a Spicchi','PBK Dinamo Ronco','Maccabi Ruero','Casorzo Lakers','Furleee']}

def canonical_team(team, competition):
    # Uniforma gli alias usati nel forum (es. TEAMCENTO / Team Cento).
    n=norm(team)
    aliases={'teamcento':'Team Cento','springfield':'Springfields Isotopes'}
    return aliases.get(n, team)

def detect_team_line(line, competition):
    n=norm(line)
    # Alcuni post non riportano il nome della squadra: il copia-incolla contiene
    # però l'username dell'autore. Lo usiamo come secondo identificatore stabile.
    owner=TEAM_OWNERS.get(competition,{}).get(n)
    if owner: return canonical_team(owner,competition)
    for team in TEAM_NAMES.get(competition,[]):
        # Una riga di calendario/risultato (es. "Olimpija Ruero – Chi Burdel")
        # NON e' l'inizio di un post-formazione. In precedenza il test `tn in n`
        # faceva partire il blocco dal calendario e contaminava/riordinava la
        # formazione con giocatori dei post successivi. Accettiamo quindi solo
        # l'intestazione squadra esatta (gli username sono gia' gestiti sopra).
        if n==norm(team):
            return canonical_team(team,competition)
    return None

def parse_page(text, competition, learned_aliases=None, rosters=None):
    """Estrae le formazioni dai POST, non dal semplice susseguirsi di nomi squadra.

    Priorità assoluta agli username-autore noti: un blocco parte dalla riga autore e
    termina al successivo autore. Il nome squadra eventualmente ripetuto dentro il
    post è solo un'intestazione e non apre un nuovo blocco. Solo per squadre non
    trovate via autore usiamo come fallback una riga contenente ESATTAMENTE il nome
    squadra. Questo impedisce contaminazioni tra PCF LBA/LNP e tra calendario/post.
    """
    lines=text.replace('\r','').split('\n')
    owners=TEAM_OWNERS.get(competition,{})

    # 1) Blocchi autore -> autore: è la struttura reale del forum.
    author_starts=[]
    for i,line in enumerate(lines):
        owner=owners.get(norm(line.strip(' *')))
        if owner:
            author_starts.append((i,canonical_team(owner,competition)))

    forms={}
    for pos,(i,team) in enumerate(author_starts):
        end=author_starts[pos+1][0] if pos+1<len(author_starts) else len(lines)
        block='\n'.join(lines[i+1:end])
        players=parse_formation(block, learned_aliases, (rosters or {}).get(team,[]), competition)
        if len(players)>=5:
            forms[team]=players

    # 2) Fallback per copia/incolla senza username: solo intestazione squadra ESATTA.
    # Non sovrascrive mai una formazione già letta dal relativo autore.
    team_starts=[]
    for i,line in enumerate(lines):
        n=norm(line.strip(' *'))
        for team in TEAM_NAMES.get(competition,[]):
            if n==norm(team):
                ct=canonical_team(team,competition)
                if ct not in forms:
                    team_starts.append((i,ct))
                break
    for pos,(i,team) in enumerate(team_starts):
        # termina al prossimo autore noto o alla prossima intestazione squadra fallback
        stops=[j for j,_ in team_starts if j>i]
        stops += [j for j,_ in author_starts if j>i]
        end=min(stops) if stops else len(lines)
        players=parse_formation('\n'.join(lines[i+1:end]), learned_aliases, (rosters or {}).get(team,[]), competition)
        if len(players)>=5 and team not in forms:
            forms[team]=players

    # Accoppiamenti: il calendario è indipendente dai blocchi formazione.
    matchups=[]
    matchup_lines=lines
    if competition=='fbl_lba':
        for cut,line in enumerate(lines):
            if norm(line)=='supercoppa':
                matchup_lines=lines[:cut]; break
    for line in matchup_lines:
        if '–' not in line and ' - ' not in line: continue
        found=[]; nl=norm(line)
        for team in TEAM_NAMES.get(competition,[]):
            if norm(team) in nl: found.append(canonical_team(team,competition))
        found=list(dict.fromkeys(found))
        found=sorted(found, key=lambda t:min([nl.find(norm(x)) for x in TEAM_NAMES.get(competition,[]) if canonical_team(x,competition)==t and norm(x) in nl] or [9999]))
        if len(found)>=2 and found[0]!=found[1]:
            pair=(found[0],found[1])
            if pair not in matchups: matchups.append(pair)
    return forms,matchups

def calculate_page(text, competition, games, learned_aliases=None, roster_text=''):
    # I roster incorporati sono il fallback iniziale. Un roster incollato dall'utente
    # sostituisce/aggiorna solo le squadre presenti nel testo caricato.
    rosters={k:[dict(x) for x in v] for k,v in DEFAULT_ROSTERS.get(competition,{}).items()}
    uploaded=parse_roster_page(roster_text or '',competition)
    rosters.update(uploaded)
    # FBL: l'identita della formazione viene ricostruita SEMPRE dal testo corrente + roster corrente.
    # Il dizionario appreso non puo mai riscrivere una formazione (evita alias storici avvelenati).
    formation_aliases = {} if competition=='fbl_lba' else learned_aliases
    forms,matchups=parse_page(text,competition,formation_aliases,rosters)
    # Anche l'indice tabellini FBL non viene riscritto da alias storici: il matching
    # parte dai nomi canonici risolti sul roster corrente.
    stats_aliases = {} if competition=='fbl_lba' else learned_aliases
    stats=player_index(games, stats_aliases)
    teams={}; resolution=[]
    for team,players in forms.items():
        resolved=[]
        team_roster=rosters.get(team,[])
        for p in players:
            raw=p.get('name',''); canonical,conf,cands=roster_match(raw,p.get('role',''),team_roster,formation_aliases,team)
            q={**p,'source_name':raw,'name':canonical}
            rp=next((x for x in team_roster if norm(x.get('name',''))==norm(canonical)),None)
            q['status']=(rp or {}).get('status','').upper()
            if competition=='fbl_lba' and not q['status']:
                q['status']='ITA' if norm(canonical) in FBL_ITA_NAMES else 'STR'
            resolved.append(q)
            resolution.append({'team':team,'raw':raw,'canonical':canonical,'confidence':round(conf,3),'candidates':cands,'role':p.get('role','')})
        if competition=='fbl_lba': score,details=score_fbl(resolved,stats,team)
        else: score,details=score_formation(resolved,stats)
        teams[team]={'score':score,'players':resolved,'details':details}
    results=[]
    bonus=5 if competition=='fbl_lba' else 3
    for home,away in matchups:
        if home in teams and away in teams:
            results.append({'home':home,'away':away,'home_score':teams[home]['score']+bonus,'away_score':teams[away]['score'],'home_bonus':bonus})
    # Il browser memorizza solo associazioni che hanno effettivamente risolto un
    # nome del forum verso un nome ufficiale del tabellino. Gli irrisolti vengono
    # mostrati esplicitamente: non devono mai diventare zeri silenziosi.
    suggestions={}; unresolved=[]
    stat_names={norm(v[0]):v[0] for v in stats.values()}
    for r in resolution:
        raw=r['raw']; canonical=r['canonical']; team=r['team']
        # canonical roster name -> nome ufficiale tabellino
        official=best_match(canonical,stats)[0]
        stats_ok=norm(official) in stat_names
        # Se il nome è stato risolto con sicurezza CONTRO IL ROSTER della squadra,
        # è valido anche quando non compare nel tabellino (DNP/non convocato = 0').
        # Non ha senso chiedere di convalidare Nico Mannion o Garrison Mathews solo
        # perché quel giorno non sono presenti nell'elenco statistiche.
        roster_ok = r['confidence'] >= .48 and any(norm(canonical)==norm(p.get('name','')) for p in rosters.get(team,[]))
        ok = stats_ok or roster_ok
        if stats_ok and norm(raw)!=norm(official): suggestions[raw]=official
        elif roster_ok and norm(raw)!=norm(canonical): suggestions[raw]=canonical
        if not ok:
            unresolved.append({'team':team,'name':raw,'role':r['role'],'candidates':r['candidates']})
    valid=not unresolved and all(len(v.get('players',[]))>=10 for v in teams.values())
    return {'teams':teams,'matchups':results,'detected':list(forms),
            'parsed_formations':{t:[{'name':p.get('source_name',p.get('name','')),'canonical':p.get('name',''),'role':p.get('role','')} for p in v.get('players',[])] for t,v in teams.items()},
            'alias_suggestions':suggestions,'unresolved':unresolved,'rosters':{k:len(v) for k,v in rosters.items()},'roster_players':rosters,'valid':valid}
