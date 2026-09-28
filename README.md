# Tabellini LBA e LNP A2 2026/27

Seleziona LBA Serie A oppure LNP Serie A2 e una delle 30 giornate. Visualizza le otto gare LBA o le dieci gare A2 con stato, data e ora, punteggio live e parziali per quarto, poi scarica il file `.xlsx` con i fogli **Statistiche** e **Partite**. I minuti sono numeri interi.

## Aggiornamento del repository LBASCRAP

Carica nella radice del repository tutti i file di questa cartella. `a2_calendar.json` e `a2_tabellini.py` sono nuovi; gli altri aggiornano i file presenti. Prima del commit, verifica che GitHub li mostri come modificati e non come duplicati in una sottocartella. Dopo il commit su `main`, Render ridistribuisce il servizio collegato.

Il calendario deriva da `Calendario LBA_2627.xlsx` fornito dall'utente (30 giornate, otto ID partita ciascuna). Data, ora, stato e punteggi vengono letti dall’API Legabasket (flag 0 = da giocare, 1 = in corso, 2 = terminata). Durante il live il punteggio si aggiorna automaticamente ogni 20 secondi. I tabellini vengono letti dalla pagina della gara. Per le gare **DA GIOCARE**, le statistiche dei giocatori restano vuote, anche se il sito sorgente mostra righe provvisorie.

I 300 link A2 derivano dal file `link_A2_x2627_giornate_1-30.txt` fornito dall'utente. Date, squadre, punteggio e stato A2 vengono letti dal calendario ufficiale LNP (`game_status`: `ready` = da giocare; `finished` = terminata; gli stati live riconosciuti = in corso). I boxscore vengono letti dalla pagina ufficiale della partita quando disponibili. Le giornate vengono rilette dopo al massimo 60 secondi (10 secondi con partite in corso), per recepire eventuali correzioni; l'aggiornamento live dei punteggi avviene ogni 20 secondi. I campi non presenti nel boxscore A2, per esempio `Plus_minus`, restano vuoti.

Per una prova locale: `python app.py`, poi apri `http://localhost:10000`. Non sono richieste librerie esterne.
