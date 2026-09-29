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
