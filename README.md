# LBASCRAP — solo risultati e tabellini 2026/27

Versione alleggerita derivata da `LBASCRAP_EUROCUP_TEST_V4_STATUS.zip`.

Include esclusivamente consultazione e scarico dei risultati/tabellini per:

- LBA Serie A
- LNP Serie A2
- EuroLeague 2026/27
- EuroCup 2026/27

Sono stati rimossi completamente il motore Fantabasket, PCF/FBL, roster, alias, formazioni e relativi test/API.

La pagina permette di scegliere campionato e giornata, visualizzare stato/data/ora/punteggio/tabellino e scaricare il file Excel. Restano invariate le logiche di scraping della V4, compresa la gestione stato EuroLeague/EuroCup e la normalizzazione dei minuti.

Per una prova locale: `python app.py`, poi apri `http://localhost:10000`.

## V5
- Parser LNP A2 reso tollerante alle righe aggregate/footer aggiuntive introdotte nei tabellini: associa ai giocatori le rispettive righe statistiche e ignora i riepiloghi successivi.
- Nessuna modifica ai parser LBA, EuroLeague ed EuroCup o alla logica di stato/esportazione.

## V7 - elenco risultati + tabellini a richiesta
- La giornata mostra subito tutte le partite con data/ora, stato e punteggio.
- Le gare non ancora giocate mostrano `0 - 0`.
- Il tabellino non viene scaricato all'apertura della giornata: cliccando su un punteggio diverso da `0 - 0` viene caricato e aperto; un secondo clic lo richiude.
- EuroLeague/EuroCup: `played` determina la gara conclusa; gli stati live espliciti determinano `IN CORSO`; la presenza del punteggio non viene usata per dichiarare una gara conclusa.
- L'export Excel continua a caricare i boxscore completi al momento dell'esportazione.
- Conservata la conversione minuti V6: ogni frazione positiva di minuto viene arrotondata per eccesso (es. 00:47 -> 1).
