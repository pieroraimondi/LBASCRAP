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
