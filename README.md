# Tabellini LBA e LNP A2 2026/27

Seleziona LBA Serie A oppure LNP Serie A2 e una delle 30 giornate. Visualizza le otto gare LBA o le dieci gare A2 con stato, data e ora, punteggio live e parziali per quarto, poi scarica il file `.xlsx` con i fogli **Statistiche** e **Partite**. I minuti sono numeri interi.

## Aggiornamento del repository LBASCRAP

Carica nella radice del repository tutti i file di questa cartella. `a2_calendar.json` e `a2_tabellini.py` sono nuovi; gli altri aggiornano i file presenti. Prima del commit, verifica che GitHub li mostri come modificati e non come duplicati in una sottocartella. Dopo il commit su `main`, Render ridistribuisce il servizio collegato.

Il calendario deriva da `Calendario LBA_2627.xlsx` fornito dall'utente (30 giornate, otto ID partita ciascuna). Data, ora, stato e punteggi vengono letti dall’API Legabasket (flag 0 = da giocare, 1 = in corso, 2 = terminata). Durante il live il punteggio si aggiorna automaticamente ogni 20 secondi. I tabellini vengono letti dalla pagina della gara. Per le gare **DA GIOCARE**, le statistiche dei giocatori restano vuote, anche se il sito sorgente mostra righe provvisorie.

I 300 link A2 derivano dal file `link_A2_x2627_giornate_1-30.txt` fornito dall'utente. Date, squadre, punteggio e stato A2 vengono letti dal calendario ufficiale LNP (`game_status`: `ready` = da giocare; `finished` = terminata; gli stati live riconosciuti = in corso). I boxscore vengono letti dalla pagina ufficiale della partita quando disponibili. Le giornate vengono rilette dopo al massimo 60 secondi (10 secondi con partite in corso), per recepire eventuali correzioni; l'aggiornamento live dei punteggi avviene ogni 20 secondi. I campi non presenti nel boxscore A2, per esempio `Plus_minus`, restano vuoti.

Per una prova locale: `python app.py`, poi apri `http://localhost:10000`. Non sono richieste librerie esterne.


## Fantabasket

La pagina include ora tre aree di calcolo: **PCF LBA**, **PCF LNP** e **FBL LBA**. Il copia/incolla delle formazioni viene conservato nel `localStorage` del browser separatamente per ciascun fantabasket e resta disponibile finché viene sovrascritto o azzerato. Il calcolo usa i tabellini della giornata selezionata; per PCF applica il riempimento dei 40 minuti per ruolo e il +3 alla squadra di casa.

## Modulo Fantabasket
Il copia/incolla delle formazioni è memorizzato separatamente per competizione e giornata. Il parser PCF riconosce anche i post in cui il nome della squadra non è ripetuto, usando l'username dell'autore del forum (caso tipico di Casorzo Lakers e Olimpija Ruero in PCF LNP).

## Modulo Fantabasket

La pagina include tre calcolatori: **PCF LBA**, **PCF LNP** e **FBL LBA**. Il copia/incolla grezzo del thread viene conservato nel browser separatamente per competizione e giornata finché viene sovrascritto o azzerato.

- PCF LBA/LNP: +3 alla squadra di casa; motore 40 minuti per slot con 11°/12° sui residui compatibili.
- FBL LBA: +5 alla squadra di casa; 5 titolari + 5 riserve + fino a 3 tribuna. La tribuna interviene, in ordine e per ruolo compatibile, quando uno dei primi 10 ha 0 minuti.

Test di regressione G1 usati per il motore:
- PCF LBA: Basket Padova – Olimpija Ruero **75–57**.
- PCF LNP: Si Ok E Poi? – I Mollo **52–108**.
- FBL LBA: Drink Team – Rasta Panthers **61–122**; CSKA Basket – Monza a Spicchi **147–139**; PBK Dinamo Ronco – Maccabi Ruero **98–100**; Casorzo Lakers – Furleee **87–79**.

### Motore PCF — correzione calcolo
Il calcolo PCF replica ora letteralmente il foglio `calcolatore`: primi 5 titolari per slot PM/G/AP/AG/C, successivi 5 panchinari negli stessi slot; 11° e 12° usano i minuti residui in base al ruolo dichiarato. Per i doppi ruoli i minuti disponibili sono la somma dei residui dei due slot compatibili; dopo l'11° i suoi minuti reali vengono sottratti da ciascuno slot compatibile come nel foglio Excel. Non viene effettuata alcuna ottimizzazione automatica del ruolo.

## Dizionario nomi Fantabasket
Il modulo Fantabasket mantiene, separatamente per FBL LBA, PCF LBA e PCF LNP, un dizionario locale delle abbreviazioni riconosciute con certezza. Le associazioni apprese sono salvate nel browser e riutilizzate nelle giornate successive; il pulsante "Azzera dizionario nomi" le elimina. I match dubbi non vengono accettati automaticamente e sono segnalati come nomi non riconosciuti.

## Fantabasket: roster persistenti e dizionario dinamico
Per FBL LBA, PCF LBA e PCF LNP è disponibile una sezione Roster. Il copia-incolla del roster viene memorizzato nel browser separatamente per competizione e resta disponibile dopo i redeploy finché non viene sostituito o azzerato. Il parser usa prima il roster della squadra, poi ruolo/slot, alias appresi e infine il tabellino ufficiale. Le associazioni confermate vengono memorizzate nel dizionario della competizione.

Se un nome non è risolto con sufficiente certezza, il calcolo viene bloccato e vengono mostrati i candidati del roster: nessuna riga viene ignorata intenzionalmente per produrre un punteggio parziale. Confermando un candidato, l'alias viene salvato e il calcolo viene rieseguito.

## Validazione nomi e scelta dal roster
Quando un nome della formazione non viene risolto con certezza, la sezione Fantabasket mostra la proposta ricavata dal roster e consente di convalidarla. Se la proposta manca o non è corretta, **Scegli dal roster** apre il roster della squadra con ricerca per nome/ruolo. Ogni scelta manuale viene salvata come alias specifico per lega+squadra+nome scritto nel forum e riutilizzata nelle giornate successive. Gli alias manuali sono visibili e cancellabili dalla sezione **Alias memorizzati**. **Convalida tutti** salva in blocco solo le righe che hanno una proposta automatica.
