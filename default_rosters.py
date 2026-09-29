"""Roster iniziali incorporati. Sono fallback: un roster incollato dall'utente sovrascrive la lega."""

def _parse(s):
    out={}
    team=None
    for raw in s.strip().splitlines():
        line=raw.strip()
        if not line: continue
        if line.startswith('## '):
            team=line[3:].strip(); out[team]=[]; continue
        role,name=line.split('|',1); out[team].append({'role':role.strip(),'name':name.strip()})
    return out

PCF_LBA=_parse(r'''
## I Mollo
PM/G|Darius Thompson
AP/AG|Jason Burnell
C|Ousmane Diop
G/AP|Stefano Tonut
C|Moses Wright
AP/AG|Jack White
AG/C|Leonardo Toté
PM/G|Nico Mannion
C|Amedeo Tessitori
AP/AG|RJ Melendez
PM/G|Leandro Bolmaro
G/AP|Devon Hall
G|Garrison Mathews
G|Jaylen Barford
PM/G|Ky Bowman
## Casorzo Lakers
G|Quincy Olivari
PM|Dewayne Russell
PM|Alessandro Cappelletti
PM|Michele Ruzzier
C|Nick McGlynn
G/AP|Denzel Valentine
AP/AG|Andrea Loro
AG|Jermaine Samuels
PM/G|Andrew Andrews
C|Mike Tobey
AP/AG|Derrick Alston JR
AP/AG|Francesco Ferrari
AP/AG|Kessler Edwards
AG/C|Alessandro Lever
G/AP|Riccardo Moraschini
## Pikkiatelli Bodio
AG/C|Leonardo Okeke
AG/C|Vernon Carey
AP/AG|Zac Seljaas
AG|Amar Alibegovic
G/AP|Charles Brown JR
PM/G|Lorenzo Bucarelli
PM|Matteo Librizzi
G|Amedeo Della Valle
AG/C|Kyle Wiltjer
PM/G|Federico Zampini
G/AP|Sean McDermott
PM/G|Erick Green
C|Kaleb Tarczewski
PM|Trent Frazier
AP/AG|Lajae Jones
## PCF 'Facu' Mastelle
AG/C|Guglielmo Caruso
G|Jahmi’us Ramsey
PM|Kenneth Smith
G|Giordano Bortolani
AP/AG|Matteo Cavallero
AG|Andrejs Grazulis
AG/C|John Brown
C|Gora Camara
PM/G|Garrett Nevels
AP|Davide Alviti
PM/G|Mike Iuzzolino
G/AP|Lorenzo Ambrosin
AP|Brandon Johnson
G/AP|Marko Guduric
## Zalgiris
PM/G|Semaj Christon
AP|Savion Flagg
AG/C|Alec Peters
AG/C|JT Thor
C|Derek Ogbeide
C|Jaime Echenique
PM/G|Bruno Mascolo
AG/C|Marko Simonovic
AP/AG|Alessandro Bertini
G/AP|RaeQuan Battle
PM|Andrea Calzavara
G/AP|Tomas Woldetensae
PM|Edoardo Di Meo
G/AP|Izaiah Brockington
PM/G|David Duke
## Domonator
PM|Marco Spissu
AG/C|Paul Eboua
AP|Louis Olinde
PM/G|Daniel Hackett
G/AP|Liam Udom
AG|Isaiah Miles
PM|Corey Davis
G/AP|JP Macura
C|Skylar Spencer
C|Nate Renfro
AP/AG|Sasha Grant
G/AP|Langston Galloway
G/AP|Leonardo Faggian
## Basket Padova
G/AP|Andrea Pecchia
AG/C|Valentin Chery
PM/G|William McDowell-White
AP/AG|Stefan Nikolic
AG|Isaiah Roby
C|Enoch Boakye
C|Federico Poser
PM/G|Xavier Moon
PM/G|Tommaso Baldasso
PM|Zan Sisko
G|Octavio Maretto
AG|Andrea Mezzanotte
AP|Paul Watson
AG|Hunter Tyson
## Olimpija Ruero
C|Chad Brown
AP|Giovanni Veronesi
PM|Aaron Holiday
AP/AG|Chimezie Offurum
AP/AG|Trentyn Flowers
C|Selom Mawugbe
AG/C|Jordan Bayehe
PM|Darius Brown
AG/C|Aliou Diarra
PM/G|Davide Casarin
G/AP|Wendell Moore
AP/AG|Andrej Jakimovski
PM/G|Marcus Carr
PM/G|Alessandro Manfredotti
C|Maximilian Ladurner
## Dinamo Lucura
C|Miro Bilan
PM|RJ Cole
PM|Charlie Moore
G|Dante Maddox
G/AP|Federico Miaschi
PM/G|Rasheed Bello
AP/AG|Bo Klintman
AG/C|Matteo Chillo
G/AP|Markel Brown
AP/AG|Lodovico Deangeli
PM/G|Diego Flaccadori
G/AP|Abramo Canka
AG|Brekkott Chapman
PM/G|Davide Moretti
## Springfields Isotopes
PM|Matteo Parravicini
G/AP|Mirza Alibegovic
AP/AG|Giampaolo Ricci
G/AP|Rob Edwards
C|Giovanni Emejuru
G/AP|Cheikh Niang
PM/G|Hunter Hale
PM|Glynn Watson Jr
G|C.J. Massinburg
AG/C|Devin Booker
AG|Eimantas Bendzius
AG/C|Kevin Kokila
AG|Luca Severini
PM/G|Federico Bonacini
C|Christopher Ike Anigbogu
## Birrareal
G/AP|John Petrucelli
AG/C|Ze’Rik Onyema
G|Gerald Ayayi
PM/G|Aljami Durham
AP/AG|Isaiah Bigelow
PM|Colbey Ross
AP/AG|Joseph Mobio
C|Ismael Kamagate
PM/G|Leonardo Candi
AP/AG|Nikola Akele
G/AP|Riccardo Visconti
AP/AG|Carl Wheatle
PM|Toto Forray
AP|Iris Ikangi
## Rasta Panthers
PM|Jeff Dowtin
PM/G|Lorenzo Uglietti
PM/G|Riccardo Rossato
G/AP|Arturs Strautins
G/AP|Karim Jallow
AG|Justin Gorham
C|Dominik Olejniczak
PM/G|Prentiss Hubb
C|Francesco Candussi
AP/AG|Jordan Parks
AG/C|Mouhamet Diouf
AP|Matt Ryan
AP/AG|Assane Sankare
C|Antonio Iannuzzi
''')

PCF_LNP=_parse(r'''
## Casorzo Lakers
G/AP|Jaron Johnson
PM|Tommaso Vecchiola
C|Giovanni Vildera
PM/G|David Cournooh
AG/C|Lorenzo Galmarini
PM/G|Simone Valsecchi
C|Matteo Gherardini
AG/C|Riccardo Salvioni
C|Leonardo Bettiol
AP/AG|Riccardo Chinellato
PM|Federico Massone
G/AP|Simone Pepe
AG|Terry Allen
PM/G|Lucio Redivo
AG/C|Alessandro Ferrari
## Chi Burdel
AG/C|Giacomo Dell’Agnello
AP/AG|Ethan Esposito
PM|Matteo Fantinelli
PM|Alessandro Zanelli
AP/AG|Hasan Varence
AP/AG|Alessandro Gentile
PM/G|Matteo Imbrò
AG/C|Nicolò Nobili
G/AP|Luca Cesana
C|Alessandro Morgillo
G|Isaiah Brickner
PM|Gianluca Della Rosa
AG/C|Mihajlo Jerkovic
G/AP|Martino Mastellari
C|Anthony Morse
## Zalgiris
PM/G|Mattia Palumbo
PM|Domenico D’Argenzio
G/AP|Alessandro Sperduto
AG/C|Stacy Davis
AG/C|Samuele Moretti
AG|Tio Tiagande Willis
PM|Nicola Berdini
AP/AG|Andrija Josovic
C|Francesco Pellegrino
G/AP|Marquis Barnett
PM|Matteo Bogliardi
G|Jazz Johnson
C|Luca Possamai
PM|Andrea De Nicolao
PM/G|Mattia Ceccato
## I Mollo
G/AP|Alvise Sarto
AP/AG|Niccolo De Vico
AG/C|Simone Zanotti
PM|Eugenio Rota
C|Romello White
AG|Jeff Brooks
PM|Lorenzo Caroti
PM/G|Matteo Montano
PM/G|Avery Woodson
G/AP|Matteo Piccoli
AG/C|Vittorio Bartoli
G/AP|Michele Vitali
AP/AG|Tevin Mack
C|Andrea Zerini
## Si Ok E Poi?
AG/C|Andrea Lo Biondo
G/AP|Luca Conti
PM/G|Michele Munari
AG/C|Matt Tiby
PM/G|Stefano Gentile
PM|Stefano Saccoccia
AG/C|Mattia Acunzo
G/AP|Aristide Mouaha
G/AP|Caleb Walker
AP/AG|Mattia Udom
PM|Filippo Gallo
AP/AG|Michele Serpilli
C|Jacorey Williams
## Team Cento
PM|Andrea Cinciarini
AP/AG|Cosimo Costi
C|Matteo Berti
G/AP|Alberto Conti
AG|Davide Pascolo
PM|Lorenzo Penna
G/AP|Zach Harvey
PM/G|Matteo Corgnati
G/AP|Francesco Reggiani
PM/G|Alfredo Boglio
C|Ursulo D'Almeida
AG/C|Paulius Sorokas
G|Devonte Green
AG/C|Falilou Mbacke
C|Edoardo Tiberti
## Olimpija Ruero
AP/AG|Marco Mollura
G/AP|Luca Campogrande
C|Marcus Santos-Silva
AP/AG|Raphael Gaspardo
AG|Valerio Mazzola
PM/G|Lorenzo Calbini
AG/C|Regimantas Miniotas
PM/G|Matteo Accorsi
G/AP|Cody Demps
C|Angelo Del Chiaro
AP/AG|Todor Radonjic
PM/G|Diego Monaldi
G/AP|Vincenzo Guaiana
PM|Matteo Schina
AG/C|Damir Hadzic
## Liverpaul
AG/C|Alexander Cicchetti
G/AP|Umberto Stazzonelli
PM/G|Jayvon Graves
AG|Ion Lupusor
G/AP|Gabriele Stefanini
PM/G|Lorenzo Saccaggi
PM/G|Giovanni Tomassini
C|Bryce Nze
G/AP|KeShawn Curry
AP/AG|Nazzareno Italiano
AP/AG|Giacomo Leardini
PM|Saverio Bartoli
C|Davide Bruttini
## Rasta Panthers
PM/G|Blake Francis
AG/C|Gabriele Miani
AP|Seneca Knight
AG/C|Simone Barbante
C|Tommaso Guariglia
AP/AG|Luca Tozzi
PM|Costantino Bechi
PM/G|Matteo Tambone
AG/C|Dustin Hogue
AG/C|Simone Aromando
G/AP|Joonas Riismaa
G/AP|Riccardo Bolpin
PM|Stefano Trucchetti
C|Lorenzo Benvenuti
G/AP|Fabio Mian
## Butter Beater
PM/G|Federico Mussini
AG/C|Massimiliano Moretti
PM/G|Davide Denegri
G/AP|Pierpaolo Marini
C|Deshawn Stephens
PM/G|Alessandro Grande
G/AP|Tyreek Scott-Grayson
AG/C|Giacomo Zanetti
AP/AG|Simon Anumba
AP/AG|Niccolo Filoni
C|Alessandro Simioni
G/AP|Lucas Fresno
PM/G|Ivan Mobio
AG/C|Deshawn Freeman
''')

FBL_LBA=_parse(r'''
## Rasta Panthers
PM/G|Kenneth Smith
PM/G|Aljami Durham
PM/G|Alessandro Cappelletti
PM/G|Lorenzo Bucarelli
G/AP|Jaylen Barford
G/AP|Andrea Pecchia
AP|Isaiah Roby
AP|Jason Burnell
AP|Louis Olinde
AP|Andrej Jakimovski
AP|Francesco Ferrari
AG/C|JT Thor
C|Nick McGlynn
C|Skylar Spencer
C|Selom Mawugbe
## Monza a Spicchi
G|Dante Maddox
G|Gerald Ayayi
G|Langston Galloway
G|Tommaso Baldasso
G/AP|Charles Brown
G/AP|JP Macura
G/AP|Riccardo Moraschini
G/AP|Mirza Alibegovic
G/AP|Riccardo Visconti
AP|Jordan Parks
AP|Isaiah Miles
C|Chad Brown
C|Ike Anigbogu
C|Jordan Bayehe
C|Guglielmo Caruso
## Drink Team
G|Hunter Hale
G|Glynn Watson
G|DeWayne Russell
G|Hassani Gravett
G|Amedeo Della Valle
G|Bruno Mascolo
G/AP|Denzel Valentine
AP|Jack White
AP|Mezie Offurum
AP|Eimantas Bendzius
AP|Federico Miaschi
AP|Giovanni Veronesi
C|Dominik Olejniczak
C|Paul Eboua
## Maccabi Ruero
G|Wendell Moore
G|Colbey Ross
G|Federico Zampini
G/AP|Izaiah Brockington
AP|Alec Peters
AP|Hunter Tyson
AP|Arturs Strautins
AG/C|Valentin Chery
AG/C|John Brown
AG/C|Marko Simonovic
AG/C|Alessandro Lever
C|Aliou Diarra
C|Moses Wright
C|Kevin Kokila
C|Ousmane Diop
## PBK Dinamo Ronco
G|Jahmi'us Ramsey
G|Quincy Olivari
G|Semaj Christon
G|Marcus Carr
G|Andrea Calzavara
G|Matteo Librizzi
G/AP|RaeQuan Battle
AP|Savion Flagg
AP|Trentyn Flowers
AP|Bo Klintman
AP|Alessandro Bertini
AP|Davide Alviti
C|Kaleb Tarczewski
C|Enoch Boakye
C|Gora Camara
## CSKA Basket
G|Charlie Moore
G|Aaron Holiday
G|Xavier Moon
G|RJ Cole
G|Nico Mannion
G|Darius Thompson
AP|Derrick Alston
AP|Jermaine Samuels
AP|Justin Gorham
AP|Kessler Edwards
AP|Andrea Loro
AG/C|Ze'Rik Onyema
C|Miro Bilan
C|Amedeo Tessitori
C|Leonardo Toté
## Casorzo Lakers
G|Darius Brown
G|Prentiss Hubb
G|C.J. Massinburg
G|Riccardo Rossato
G|Giordano Bortolani
G|Davide Moretti
G/AP|John Petrucelli
AP|Zac Seljaas
AP|Isaiah Bigelow
AP|Lajae Jones
AP|Stefan Nikolic
C|Jaime Echenique
C|Mike Tobey
C|Derek Ogbeide
C|Ismael Kamagate
## Furleee
G|Andrew Andrews
G|Jeff Dowtin
G|Rob Edwards
G|Markel Brown
G|Trent Frazier
G|Marco Spissu
G/AP|Devon Hall
G/AP|Marko Guduric
AP|RJ Melendez
AP|Karim Jallow
AP|Amar Alibegovic
AP|Carl Wheatle
AG/C|Kyle Wiltjer
C|Mouhamet Diouf
C|Giovanni Emejuru
''')

DEFAULT_ROSTERS={'pcf_lba':PCF_LBA,'pcf_lnp':PCF_LNP,'fbl_lba':FBL_LBA}
