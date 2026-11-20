# PR1 · Puntualitat i incidències ferroviàries: Rodalies i els nuclis de Rodalia de Renfe

**Autor:** Juan Rogel Navarro · Màster universitari de Ciència de Dades, UOC · 14 de novembre de 2026

**Codi i dades:** [github.com/juanBcn/Visualitzacio_dades](https://github.com/juanBcn/Visualitzacio_dades)

**Visualització de dades · Pràctica, part I: selecció del conjunt de dades**

## 1. Presentació

El projecte analitza qui pateix els retards del tren a Catalunya, on i quan, i fins a quin punt la resposta depèn de qui mesura. Combina dues mirades sobre el mateix servei: les dades ciutadanes de [Puntual.cat](https://www.puntual.cat/dades/estadistica), que registren el retard de cada parada de Rodalies i FGC des del novembre de 2024, i els [informes mensuals de puntualitat de Renfe](https://grupo.renfe.com/es/es/gobierno-y-transparencia/puntualidad-en-los-servicios/cercanias), que publiquen els indicadors oficials dels 13 nuclis de Rodalia de l'Estat des del gener de 2025.

La taula principal té una fila per estació i mes: 6.142 registres i una trentena de variables, entre originals i derivades. S'enriqueix amb dades de línia, sentit, tipus de dia i franja horària, amb el catàleg obert de Renfe i amb indicadors municipals d'Idescat.

El resultat previst és una visualització narrativa i interactiva adreçada a les persones usuàries del tren i a la ciutadania de Catalunya.

## 2. Justificació de l'elecció

He triat aquest tema perquè trasllada al ferrocarril el problema amb què treballo cada dia: mesurar una disrupció del transport i decidir qui n'és responsable.

**Motiu professional.** Soc enginyer de programari en una consultora tecnològica i fa anys que treballo per a un client internacional del sector del transport. Hi he treballat a l'àrea de client, en reclamacions de passatgers i en gestió de disrupcions. Les reclamacions per retard o cancel·lació depenen de tres preguntes: quant de retard hi ha hagut, mesurat on (sortida, arribada, destí final) i atribuït a qui (operador o causa externa). Els informes de Renfe responen exactament aquestes preguntes per al tren: llindars de 5, 15, 30 i 60 minuts, mesura al destí final i minuts de retard separats entre causes pròpies i externes. Treballar-hi em permet aprofundir en un domini que conec, però amb dades obertes que no puc fer servir en l'entorn del meu client, on són confidencials.

**Motiu acadèmic.** El conjunt obliga a practicar les operacions que el màster demana: extracció des d'una API en JSON niat i des d'un informe Power BI, pas a format *tidy*, fusió de fonts amb claus diferents i agregació ponderada. No és un fitxer net descarregat d'un repositori.

**Motiu personal.** Soc usuari habitual de Renfe i conec de primera mà què suposa un retard o una supressió. També m'interessa la discussió pública sobre dades. En aquest cas, operador i usuaris publiquen xifres molt diferents del mateix servei, i una visualització rigorosa pot explicar per què totes dues poden ser certes alhora.

## 3. Rellevància i context

La puntualitat de Rodalies és un dels principals problemes de mobilitat a Catalunya i les dades arriben fins al mes passat.

### Actualitat

- A l'octubre de 2026 només el 33,8 % dels trens de Rodalies van arribar amb menys de cinc minuts de retard, i entre l'1 i el 12 de novembre la xifra va baixar al 25 %, amb set jornades de vaga, segons dades de Transporta'm recollides per [Metròpoli Abierta](https://metropoliabierta.cat/mobilitat/20261114/radiografia-caos-rodalies-set-trens-arribar-tard-loctubre-sagreuja-novembre/1003742812067_0.html) i [ElNacional.cat](https://elnacional.cat/ca/societat/rodalies-limit-set-cada-deu-trens-arriben-tard-puntualitat-enfonsa_1725581_102.html).
- El gener de 2026 un tren de la línia R4 va descarrilar entre Gelida i Martorell i hi va morir un maquinista. Entre gener i maig de 2026 Rodalies va transportar 39,9 milions de viatgers, davant dels 47,5 milions del mateix període de 2025, i les limitacions temporals de velocitat van passar de 95 a 191, segons [3CatInfo](https://www.3cat.cat/3catinfo/mig-any-des-de-laccident-de-gelida-menys-viatgers-al-tren-i-continuen-els-retards/noticia-amp/3420943/).
- Renfe publica els indicadors de Rodalia des de l'octubre de 2025. El 2025 el compliment horari de Rodalies de Barcelona va ser del 50 %, per sota de Sevilla (58,3 %), Madrid (68 %) i València (70 %), i el 37,4 % dels minuts de retard van ser atribuïbles a l'operadora, segons el [Diari de Tarragona](https://www.diaridetarragona.com/catalunya/250829/rodalies-barcelona-cumple-mitad-horarios-programados-2025.html).

### Col·lectius implicats

- **Persones usuàries captives**: treballadors, estudiants i residents de municipis sense alternativa de transport públic, per als quals un retard és temps de feina o de cures perdut.
- **Territoris perifèrics**: les línies regionals (Ebre, Lleida, Girona) tenen menys freqüència, de manera que cada tren cancel·lat pesa més.
- **Plataformes d'usuaris i periodisme de dades**, que han construït les seves pròpies fonts davant la manca de dades oficials detallades.
- **Administracions i operadors** (Generalitat, Renfe, Adif, FGC), en ple procés de traspàs de Rodalies.

### Component social i perspectiva de gènere

El retard no es reparteix per igual: depèn de la línia, de la distància a Barcelona i de l'hora. El projecte creua el retard de cada estació amb la població i la renda del seu municipi per veure si els territoris amb menys recursos reben pitjor servei.

Les dades de puntualitat no identifiquen persones, i per tant no permeten desagregar per sexe, edat o discapacitat. És una omissió rellevant, perquè les dones fan servir més el transport públic: segons l'Enquesta de mobilitat en dia feiner (EMEF) del 2022, el trien en el 18 % dels desplaçaments, davant de l'11 % dels homes. El projecte ho tractarà de manera explícita: farà servir la població municipal per sexe d'Idescat com a context i avisarà en la visualització que l'impacte per gènere no es pot mesurar amb aquestes fonts.

### Biaixos i omissions identificats

- **Qui mesura.** Renfe mesura la puntualitat al destí final de cada tren; Puntual.cat registra cada parada. Les plataformes d'usuaris sostenen que les xifres oficials no reflecteixen l'experiència real, com recull l'[ARA](https://en.ara.cat/society/why-does-renfe-say-that-the-trains-were-only-2-5-minutes-late-in-the-middle-of-the-rodalies-chaos_1_5705508.amp.html).
- **Dades ciutadanes incompletes.** Puntual.cat adverteix que les dades d'origen no sempre són completes i agrupa en una sola categoria les parades cancel·lades i les que no tenen dades.
- **Cobertura variable.** El nombre d'estacions amb dades varia entre 150 i 297 segons el mes, FGC només hi apareix des del gener de 2025 i el setembre de 2026 arriba fins al dia 22. Només 136 estacions tenen dades tots els mesos. Les comparacions temporals s'han de fer sobre el conjunt d'estacions presents en tots dos períodes.
- **Mitjanes que amaguen persones.** Un tren en hora punta porta molts més viatgers que un de migdia; el retard mitjà per tren infravalora el retard mitjà per viatger.
- **Comparació Renfe–FGC.** Les dues xarxes no són equivalents: Rodalies comparteix via amb mercaderies i llarga distància sobre infraestructura d'Adif, i FGC gestiona xarxa pròpia.
- **Dades revisables.** Renfe avisa que els valors de mesos anteriors poden canviar per reprocessos.

## 4. Conjunt de dades i complexitat

El conjunt supera els mínims de l'enunciat: la taula principal té 6.142 files i una trentena de variables, i combina dades numèriques, categòriques, temporals, geoespacials i jeràrquiques, obtingudes de fonts estructurades i semiestructurades.

### Fonts

| Font | Què aporta | Format i accés | Cobertura |
| --- | --- | --- | --- |
| [Puntual.cat](https://www.puntual.cat/dades/estadistica) (dades recollides per Transporta'm) | Retard i estat de cada parada, per estació, línia, sentit, tipus de dia i franja horària | JSON niat, via l'API pública que alimenta el web (`api.puntual.cat`) | Novembre 2024 – setembre 2026 (23 mesos); 261 estacions (188 de Rodalies i 73 d'FGC) i 29 línies al setembre de 2026 |
| [Informes de puntualitat de Renfe](https://grupo.renfe.com/es/es/gobierno-y-transparencia/puntualidad-en-los-servicios/cercanias) | Indicadors oficials per nucli i mes | Informe Power BI interactiu, sense descàrrega; el seu model de dades es consulta amb l'script descarrega_renfe.py, que en demana només totals per nucli | 13 nuclis, des del gener de 2025 |
| [Renfe Data](https://data.renfe.com/dataset) | Llistat d'estacions i horaris programats de Rodalies | CSV, XLSX i GTFS | Xarxa completa |
| [Idescat](https://www.idescat.cat/) | Població per sexe (2025) i renda familiar disponible per habitant (2023) del municipi de cada estació, assignat amb el geocodificador invers de l'ICGC | API en JSON, amb l'script descarrega_idescat.py | 273 de les 297 estacions són a Catalunya, en 181 municipis. Renda municipal per a 247 estacions, comarcal per a 20 i sense dada per a 6 |

### Taules del conjunt

| Taula | Unitat d'anàlisi | Registres aproximats | Variables |
| --- | --- | --- | --- |
| **Principal** | Estació × mes | 6.142 (entre 150 i 297 estacions per mes durant 23 mesos; 297 estacions diferents) | 32 a la taula generada (23 originals i 9 derivades); una desena més amb Renfe i Idescat |
| Línia | Línia × sentit × tipus de dia × mes | 5.131, de les quals 2.225 són combinacions de sentit i tipus de dia i la resta agregats ja calculats (valor «ANY») | 48 |
| Franja horària | Línia × tipus de dia × franja × mes | desenes de milers; s'agregarà per franges d'una hora | 4 |
| Oficial | Nucli × mes | 264 (12 nuclis d'ample ibèric × 22 mesos, l'últim incomplet) | 26 |

L'API també dóna una sèrie diària de retard mitjà per línia (15.160 files: 665 dies, del 10 de novembre de 2024 al 22 de setembre de 2026, per a 29 línies), que permet situar esdeveniments concrets en el temps. Una cinquena taula, estacions_municipi, té una fila per estació (297) i 14 variables amb el municipi, la població i la renda. Una sisena, bretxes_mes, té una fila per mes (21) amb les dues bretxes entre la mesura oficial i la ciutadana a Rodalia de Barcelona. El repositori conserva també les respostes originals de l'API de Puntual.cat (`puntualcat/raw/`) i de l'ICGC i l'Idescat (`puntualcat/raw_idescat/`), tal com es van rebre. Així es pot seguir tot el camí de transformació, del JSON niat de cada consulta a les taules planes: reanomenament de camps, normalització de dates, marca de les files agregades, assignació de cada estació al seu municipi i càlcul de les variables derivades.

He descarregat les dades el 14 de novembre de 2026 i n'he comprovat les xifres: 6.142 files, cap retard mitjà nul, 136 estacions amb dades tots els mesos i uns 17 milions de parades registrades. Com a comprovació de coherència, el retard mitjà ponderat de les estacions de Rodalies passa de 9,5 minuts el desembre de 2025 a 23,7 el febrer de 2026, després de l'accident de Gelida. La sèrie diària situa el salt el 20 de gener de 2026, quan el retard mitjà de Rodalies passa d'11 a 36 minuts d'un dia per l'altre.

### Tipus de dades

- **Quantitatives contínues**: retard mitjà en minuts, proporcions de parades per tram de retard, percentatges de puntualitat.
- **Quantitatives discretes**: nombre de parades registrades, arribades, sortides i cancel·lacions; circulacions i viatgers.
- **Categòriques nominals**: estació, línia, operador (Renfe o FGC), nucli, sentit, estat de la parada, origen de la incidència (Renfe o extern).
- **Categòriques ordinals**: trams de retard (fins a 1, 5, 10, 15, 20, 25, 30 minuts i més) i llindars oficials (5, 15, 30 i 60 minuts).
- **Temporals**: mes, tipus de dia (feiner o festiu) i franja horària.
- **Geoespacials**: coordenades de cada estació en format WKT.
- **Jeràrquiques**: operador → servei (Rodalies de Barcelona, regionals, nuclis de Girona, Tarragona i Lleida, FGC) → línia → estació; i comarca → municipi → estació.
- **De xarxa**: cada línia inclou la seqüència ordenada de les seves estacions, cosa que permet tractar la xarxa com un graf.

### Dades semiestructurades i preparació

La resposta de l'API és un JSON amb objectes niats: cada estació conté un diccionari d'estats (`smm_status`) i un altre de proporcions per tram de retard (`avg_scores`), i cada línia conté llistes de valors per sentit i tipus de dia. Cal aplanar-los, pivotar-los a format llarg i convertir la geometria WKT en longitud i latitud. L'informe de Renfe és un quadre de comandament, no una taula: els valors s'han d'extreure nucli a nucli i mes a mes.

Problemes de qualitat ja detectats: estacions sense dades en alguns mesos, estats `unknown` i `pending`, valors nuls en trams no servits i claus d'estació diferents entre fonts (codi Renfe, codi FGC, nom).

Amb les dades descarregades n'han aparegut més. A FGC les parades en estat pendent arriben al 52 % el març de 2025, cosa que invalida la puntualitat d'aquell mes. En dues files les parades cancel·lades superen les registrades. La taula de línies barreja files de detall amb agregats, que no es poden sumar. I les línies regionals inclouen estacions de fora de Catalunya, com València-Estació del Nord. A més, les dades ciutadanes infracompten les cancel·lacions: a Rodalies de Barcelona en registren al voltant del 0,1 % el 2025, mentre que Renfe hi declara entre el 2 % i el 7 % de parades suprimides cada mes. Les supressions s'han de prendre de la font oficial. El municipi de cada estació és el de l'element cartogràfic més proper a les seves coordenades, que en estacions properes a un límit municipal pot no ser el que els dona nom. De les 297 estacions, 24 són fora de Catalunya i no tenen dades municipals, i 6 més no tenen renda perquè Idescat no publica la del municipi i no s'ha pogut obtenir la de la comarca.

### Llicència i ús

Renfe Data i Idescat publiquen amb llicència oberta. Puntual.cat és d'accés obert i gratuït però no indica llicència de reutilització: vaig escriure al seu autor per demanar-li permís i el 20 de novembre de 2026 em va respondre donant el vistiplau a descarregar les dades de l'API, i oferint-me a més els fitxers parquet originals (un per línia, mes i tipus de dada). En cito la font a tot el document. L'informe de Renfe és públic però tampoc indica llicència; se'n guarden només indicadors agregats per nucli i mes. Les taules generades i les respostes originals de l'API són al repositori per facilitar l'avaluació; si algun dels titulars no ho autoritza, les retiraré. Cap de les fonts conté dades personals.

## 5. Originalitat i enriquiment

El conjunt no existeix com a tal: el construeixo combinant quatre fonts que fins ara s'han mostrat per separat, i hi afegeixo mètriques pròpies.

### Què hi ha fet

- **Puntual.cat** ofereix estadístiques mensuals per línia, un cronològic i un mapa, però només amb les seves dades i sense context socioeconòmic.
- **L'informe de Renfe** mostra un nucli i un mes cada vegada, sense comparació entre nuclis ni descàrrega.
- **La premsa** publica gràfics puntuals lligats a la notícia del dia, gairebé sempre d'un sol indicador.

No he trobat cap visualització que posi costat per costat la mesura oficial i la ciutadana, ni que relacioni el retard amb les característiques del territori. El tema tampoc coincideix amb els que l'enunciat demana evitar: «trànsit» hi fa referència a la circulació viària, i aquí s'analitza la qualitat d'un servei públic ferroviari.

### Enriquiment amb fonts externes

1. **Indicadors oficials de Renfe** units per mes al conjunt ciutadà, per comparar les dues mesures de Rodalies de Barcelona i situar-la entre els 13 nuclis.
2. **Catàleg d'estacions i horaris GTFS de Renfe Data**, per afegir a cada estació el municipi, el nombre de línies que hi paren i l'oferta programada.
3. **Població per sexe i renda familiar disponible d'Idescat**, units pel municipi de l'estació.
4. **Calendari d'esdeveniments** elaborat a mà a partir de premsa: accident de Gelida, vagues i talls per obres, com a dimensió categòrica de període.

### Mètriques noves

- **Puntualitat a 5 minuts per parada**: proporció de parades amb retard de fins a 5 minuts, calculada amb el mateix llindar que Renfe.
- **Taxa de retard greu**: proporció de parades amb més de 15 minuts de retard.
- **Taxa de cancel·lació**: parades cancel·lades sobre parades registrades.
- **Minuts perduts**: retard mitjà multiplicat pel nombre de parades servides, com a mesura de volum i no només d'intensitat.
- **Bretxa de mesura**: diferència, en punts percentuals, entre el compliment horari oficial i la puntualitat ciutadana per parada, i entre la puntualitat oficial i la ciutadana al destí final.
- **Acumulació de retard**: diferència entre el retard a final de trajecte i el retard mitjà del recorregut, per línia i sentit.
- **Distància a Barcelona-Sants** en quilòmetres i corona territorial derivada.
- **Canvi respecte al període anterior a l'accident de Gelida**, calculat per línia a partir de la sèrie diària.

## 6. Objectius

L'objectiu general és explicar com es distribueix el retard ferroviari a Catalunya entre territoris, hores i operadors, i per què les xifres oficials i les ciutadanes no coincideixen.

### Públic destinatari

- **Principal**: persones usuàries de Rodalies i ciutadania de Catalunya sense formació tècnica. Necessiten context sobre com es mesura la puntualitat i poder consultar la seva línia i estació.
- **Secundari**: periodistes de dades, plataformes d'usuaris i tècnics de mobilitat, que valoraran la possibilitat de filtrar, comparar i veure la metodologia.

### Objectius específics i hipòtesis

| Objectiu | Hipòtesi | Variables implicades | Perspectiva analítica |
| --- | --- | --- | --- |
| **O1. Bretxa entre operadors** | La diferència entre Rodalies i FGC es manté en tots els mesos, tipus de dia i franges, i per tant no s'explica per episodis puntuals. Al setembre de 2026 el retard mitjà per línia va de 0,7 a 1,4 minuts a FGC i de 3,1 a 15,7 a Rodalies. | Retard mitjà, distribució per trams × operador × línia × mes × tipus de dia × franja | Comparació de distribucions; petits múltiples per línia |
| **O2. Desigualtat territorial** | Les cancel·lacions augmenten amb la distància a Barcelona molt més que el retard (correlació de Spearman de 0,62 i 0,30 en una primera exploració de les estacions de Rodalies). Com que la perifèria té també menys població i menys renda, el servei no prestat recau sobre els municipis amb menys recursos, sense que la renda hi tingui un efecte propi un cop descomptada la distància. | Retard mitjà, taxa de retard greu, taxa de cancel·lació × distància a Sants × renda × població × línia | Geoespacial (mapa d'estacions) i correlació multivariable controlant per línia |
| **O3. Patró horari i propagació** | El retard no té dos pics d'hora punta sinó que s'acumula al llarg del dia i al llarg del recorregut, amb més intensitat en feiners i en un dels dos sentits. En una primera exploració, el retard a final de trajecte supera el retard mitjà en el 99 % de les combinacions de línia i mes de Rodalies. | Retard per franja × tipus de dia × línia; retard a final de trajecte menys retard mitjà × sentit | Temporal intradiària; mapa de calor línia × hora |
| **O4. Impacte de l'accident de Gelida** | L'accident del gener de 2026 provoca un xoc de dos mesos i una recuperació desigual: unes línies queden pitjor que abans i d'altres milloren. | Retard mitjà × dia × línia × període (abans o després); parades suprimides oficials × mes | Sèrie temporal amb esdeveniments anotats; abans i després sobre el mateix conjunt d'estacions |
| **O5. Biaix de mesura** | La bretxa entre la puntualitat oficial i la ciutadana depèn del llindar (5, 15 o 30 minuts) i del punt de mesura (destí final o cada parada), i creix en els mesos amb més cancel·lacions. | Puntualitat oficial per llindar, puntualitat ciutadana a final de trajecte i per parada, taxa de cancel·lació, minuts atribuïts a Renfe o a causes externes × mes | Comparació de mètriques sobre el mateix fet; context amb els 13 nuclis |

### Primera exploració de les hipòtesis

Una primera exploració de les dades descarregades confirma que el conjunt permet respondre els cinc objectius i ja n'avança el sentit. Els càlculs són mitjanes ponderades per parades servides, tret que s'indiqui el contrari.

| Objectiu | Què s'ha calculat | Resultat | Lectura |
| --- | --- | --- | --- |
| **O1** | Retard mitjà mensual per operador, gener 2025 – setembre 2026 | FGC entre 0,2 i 0,8 minuts; Rodalies entre 7,1 i 23,7 minuts. Parades amb fins a 5 minuts de retard a Rodalies: entre el 24,8 % i el 56,9 % | La bretxa es manté tots els mesos. La hipòtesi se sosté |
| **O2** | Correlació de Spearman entre la distància a Barcelona-Sants i el retard i la taxa de cancel·lació, en 224 estacions de Rodalies; les mateixes correlacions amb la renda i la població del municipi, en les 194 estacions de Rodalies que en tenen, i correlació parcial controlant la distància | Distància: 0,30 amb el retard i 0,62 amb les cancel·lacions. Retard mitjà per corona: 9,6 minuts fins a 15 km, 9,5 de 15 a 40 km, 10,8 de 40 a 80 km i 10,9 a més de 80 km. Renda: −0,11 amb el retard i −0,36 amb les cancel·lacions. Població: −0,27 i −0,45. Per quartils de renda, les cancel·lacions van de l'1,2 % al més baix al 0,6 % al més alt, i el retard de 9,9 a 9,5 minuts. La renda i la distància estan correlacionades (−0,61): controlant la distància, la correlació parcial de la renda és de −0,01 amb les cancel·lacions i de 0,05 amb el retard | La perifèria no arriba gaire més tard, però perd més trens, i és també la part amb menys renda i població. La renda no hi afegeix res un cop descomptada la distància: la desigualtat és territorial. La hipòtesi s'ha reformulat dues vegades. Les cancel·lacions per estació provenen de les dades ciutadanes, que les infracompten |
| **O3** | Retard a final de trajecte menys retard mitjà del recorregut, per línia i mes; retard en feiners i festius | La diferència és positiva en el 99 % dels casos de Rodalies, amb 5,9 minuts de mitjana, davant de 0,2 a FGC. Feiners 12,0 minuts i festius 9,0 (mitjana simple de línies i mesos) | El retard creix al llarg del recorregut. Falta l'anàlisi per franja horària |
| **O4** | Sèrie diària i mensual de Rodalies al voltant del gener de 2026; retard per línia abans i després del 20 de gener; parades suprimides segons Renfe | El retard passa d'11,1 minuts el 19 de gener a 36,0 el 20 de gener. Per mesos: 9,5 al desembre, 14,6 al gener, 23,7 al febrer i 10,2 al març. Per línies, l'R13 empitjora 12,9 minuts i l'R11 7,2, mentre que l'R3 i l'RG1 milloren 4,9 i 6,8. A Rodalia de Barcelona, Renfe declara un 17,9 % de parades suprimides al gener i un 14,3 % al febrer, i entre l'1,9 % i el 4,9 % des del març | Xoc de dos mesos i recuperació desigual entre línies. S'ha descartat la hipòtesi inicial que el retard es recuperava a canvi de més cancel·lacions: l'augment que mostraven les dades ciutadanes no apareix a la font oficial |
| **O5** | A Rodalia de Barcelona, gener 2025 – setembre 2026: (a) compliment horari oficial, amb llindar de 3 minuts per parada, davant de la puntualitat ciutadana per parada, amb llindar de 5 minuts; (b) puntualitat oficial al destí final davant de la ciutadana a l'última parada, totes dues amb llindar de 5 minuts | (a) De mitjana, 49,5 % oficial i 47,6 % ciutadà; menys de 6 punts de diferència en 19 dels 21 mesos, i uns 20 punts al gener i al febrer de 2026. (b) De mitjana, 93,9 % oficial i 35,3 % ciutadà; la diferència va de 47 a 80 punts i és màxima al febrer de 2026, amb un 91,1 % oficial i un 10,8 % ciutadà | Per parada, les dues fonts coincideixen en mesos normals. Al destí final divergeixen de manera sistemàtica: és la bretxa que denuncien les plataformes d'usuaris. Una diferència tan gran no s'explica pel llindar i apunta a definicions o cobertures diferents, que la visualització haurà de mostrar i explicar. Dona suport a la hipòtesi |

Aquesta exploració també ha servit per detectar els problemes de qualitat descrits a l'apartat 4, que condicionen les comparacions: els mesos d'FGC amb moltes parades pendents s'exclouran del càlcul de puntualitat.

### Procés seguit: validació de dades i refinament d'objectius

Els objectius d'aquest document no són els que vaig escriure el primer dia: s'han refinat en vuit iteracions entre les dades i les preguntes. He seguit el cicle que proposa la guia de l'assignatura (elecció de les dades, preguntes, avaluació), que coincideix amb les etapes inicials del procés de Ben Fry (adquirir, analitzar, filtrar, explorar) i amb el flux de treball de Moritz Stefaner, en què l'exploració de les dades torna enrere i modifica els objectius.

| Iteració | Què s'ha fet | Què s'ha après | Com ha canviat el projecte |
| --- | --- | --- | --- |
| 1. Tria i hipòtesis inicials | Lectura de premsa i de la descripció de les fonts; primera redacció dels cinc objectius | Hi ha dues fonts que mesuren el mateix servei i no coincideixen | El projecte passa de descriure retards a comparar mesures |
| 2. Descàrrega i perfilat | Descàrrega dels 23 mesos de Puntual.cat i comprovació de files, nuls i cobertura | La cobertura varia entre 150 i 297 estacions, la taula de línies barreja detall i agregats, i FGC té mesos amb moltes parades pendents | Regles de comparació sobre estacions comunes, columna `es_agregat` i exclusió dels mesos afectats |
| 3. Primera exploració | Càlcul de les mètriques derivades i primer contrast de cada hipòtesi | La distància a Barcelona s'associa més amb les cancel·lacions que amb el retard | Primera reformulació d'O2 |
| 4. Contrast amb la font oficial | Extracció dels indicadors de Renfe i validació contra el que mostra l'informe | Les dades ciutadanes infracompten les cancel·lacions | Correcció d'O4: es descarta que el retard es recuperi a canvi de més cancel·lacions. Les supressions es prenen de la font oficial |
| 5. Puntualitat oficial | Recompte de trens per minuts de retard al destí final | Cal excloure els serveis amb autobús per reproduir l'informe; la bretxa amb les dades ciutadanes és petita per parada i molt gran al destí final | O5 es desdobla en `bretxa_parada` i `bretxa_desti`. Es descarta el retard mitjà oficial perquè no s'ha pogut reproduir |
| 6. Revisió del diccionari | Comprovació que cada variable del diccionari existeix a les taules generades | Algunes variables descrites encara no eren a les dades | Columna Estat al diccionari, noms alineats amb els fitxers i ampliació dels scripts |
| 7. Enriquiment municipal | Assignació del municipi de cada estació i descàrrega de població i renda d'Idescat | La renda s'associa amb les cancel·lacions només perquè la perifèria té menys renda; controlant la distància, l'efecte desapareix | Segona reformulació d'O2: la desigualtat és territorial, no de renda |
| 8. Confirmació amb la font | Contacte amb l'autor de Puntual.cat per validar la interpretació de les dades i demanar-li permís de reutilització | Confirma que els valors d'`avg_scores` delimiten els trams de retard i dóna el vistiplau a l'ús de l'API; ofereix també els fitxers parquet originals | S'elimina la incertesa sobre la variable central del projecte i queda documentat el permís d'ús |

Cada xifra oficial s'ha validat contra una referència independent abans d'entrar al document: els valors que mostra l'informe de Renfe per a Astúries i Rodalia de Barcelona, i les xifres de viatgers i de quota de retard publicades a la premsa.

### Relació amb treballs anteriors

Les preguntes O1 i O3 s'han tractat parcialment a Puntual.cat i a la premsa, sempre amb un sol indicador. O2, O4 i O5 requereixen el creuament de fonts que aporta aquest projecte i no les he trobat plantejades en cap altra visualització.

### Límits que els objectius respecten

- No s'analitzen trens individuals: la granularitat mínima és el mes per estació i el dia per línia.
- No s'atribueixen causes a cada retard. L'origen de la incidència només està disponible per nucli i mes a la font oficial.
- No es mesura l'impacte per gènere, edat o discapacitat, perquè les fonts no identifiquen viatgers.
- Les relacions amb renda i població són associacions entre territoris, no efectes causals ni característiques dels viatgers.
- La comparació entre nuclis de l'Estat només es fa amb indicadors oficials, perquè les dades ciutadanes només cobreixen Catalunya.

## 7. Diccionari de variables

El diccionari separa els **fets** (el que s'observa i es mostra: retards, parades, cancel·lacions) de les **dimensions** (com s'organitza i es talla: estació, línia, mes, operador). Les variables derivades es calculen sempre a partir dels fets i indiquen com s'han d'agregar.

La columna **Estat** indica si la variable ja és a les taules que genera `scripts/descarrega_puntualcat.py` (`estacions_mes`, `linies_mes`, `linies_dia` i `linies_gelida`) o si depèn d'una font que encara s'ha d'incorporar. Les variables oficials són a la taula renfe_nucli_mes, que genera scripts/descarrega_renfe.py. Els cinc objectius es poden abordar amb les variables disponibles; les pendents, que són la franja horària i el calendari de vagues, només afinen O3 i O4. Les variables municipals són a estacions_municipi, que genera scripts/descarrega_idescat.py. Les bretxes són a bretxes_mes, que genera scripts/calcula_bretxes.py.

### Dimensions

| Variable | Tipus | Taula | Estat | Significat |
| --- | --- | --- | --- | --- |
| `mes` | Temporal (any-mes) | Totes | Disponible | Mes de referència de l'observació |
| `data` | Temporal (dia) | `linies_dia` | Disponible | Dia de l'observació |
| `estacio_id`, `codi` | Categòrica nominal | `estacions_mes` | Disponible | Identificador únic amb prefix d'operador (`renfe-65400`, `fgc-ab`) i codi original de l'estació |
| `estacio_nom` | Text | `estacions_mes` | Disponible | Nom de l'estació |
| `lon`, `lat` | Geoespacial | `estacions_mes` | Disponible | Coordenades de l'estació, extretes del camp `location` en format WKT |
| `operador` | Categòrica nominal (2) | Totes | Disponible | `renfe` o `fgc`, derivat del prefix de l'identificador |
| `linia_id`, `linia`, `linia_nom` | Categòrica nominal (29) | `linies_mes`; `linia_id` també a `linies_dia` i `linies_gelida` | Disponible | Línia (R1, R2N, S1…) i el seu recorregut |
| `servei` | Categòrica nominal (6) | `linies_mes`, `linies_dia`, `linies_gelida` | Disponible | Rodalies de Barcelona, Regionals, Rodalies de Girona, de Tarragona, de Lleida o FGC; derivat de la línia |
| `sentit` | Categòrica nominal (3) | `linies_mes` | Disponible | `ASC`, `DSC` o `ANY` (agregat dels dos sentits) |
| `tipus_dia` | Categòrica nominal (3) | `linies_mes` | Disponible | `WEEKDAY` (feiner), `HOLIDAY` (festiu) o `ANY` (agregat) |
| `es_agregat` | Booleana | `linies_mes` | Disponible | Cert si `sentit` o `tipus_dia` val `ANY`; aquestes files no se sumen amb les de detall |
| `periode` | Categòrica ordinal (2) | `estacions_mes`, `linies_mes`, `linies_dia` | Disponible | `abans_gelida` o `despres_gelida`; el tall és el gener de 2026 a les taules mensuals i el 20 de gener de 2026 a la diària |
| `corona` | Categòrica ordinal (4) | `estacions_mes` | Disponible | Tram de distància a Barcelona-Sants: fins a 15 km, de 15 a 40, de 40 a 80 i més de 80 |
| Tram de retard | Categòrica ordinal (9) | Codificada en el nom de les columnes `prop_tram_*` | Disponible en format ample; pivot a format llarg pendent | Fins a 1, 5, 10, 15, 20, 25, 30 minuts, més de 30 i sense dada |
| Estat de la parada | Categòrica nominal (7) | Codificada en el nom de les columnes `parades_*` i `trajectes_*` | Disponible en format ample; pivot a format llarg pendent | Arribada, sortida, cancel·lada, pendent i desconeguda; a les línies, també omesa i sense estat |
| `franja` | Temporal ordinal | Per construir | Pendent (descàrrega amb `--tot`) | Franja horària del dia |
| `vaga` | Booleana | Per construir | Pendent (calendari propi) | Dies o mesos amb vaga convocada |
| `nucli` | Categòrica nominal (12) | `renfe_nucli_mes` | Disponible | Nucli de Rodalia d'ample ibèric de l'informe oficial (Rodalia de Barcelona, Madrid, València…) |
| `llindar` | Categòrica ordinal (4) | Codificada en el nom de les columnes `puntualitat_oficial_*` | Disponible en format ample | Llindar de puntualitat: 5, 15, 30 o 60 minuts |
| `origen_incidencia` | Categòrica nominal (4) | Codificada en el nom de les columnes `minuts_retard_*` | Disponible en format ample | Retard atribuït a Renfe, a Adif, a altres operadors o a causes externes |
| `municipi`, `comarca` | Categòrica nominal, jeràrquica | `estacions_municipi` | Disponible | Ubicació administrativa de l'estació |

### Fets (mesures observades)

| Variable | Tipus i unitat | Taula | Estat | Significat | Com s'agrega |
| --- | --- | --- | --- | --- | --- |
| `parades_registrades` | Enter | `estacions_mes` | Disponible | Nombre de parades de tren observades (`stops_count`) | Suma |
| `parades_arribada`, `parades_sortida`, `parades_cancellades`, `parades_pendents`, `parades_desconegudes` | Enter | `estacions_mes`, `linies_mes` | Disponible | Recompte de parades per estat | Suma |
| `parades_omeses`, `parades_sense_estat` | Enter | `linies_mes` | Disponible | Parades omeses i parades sense estat informat | Suma |
| `trajectes_arribada`, `trajectes_cancellades` i la resta de `trajectes_*` | Enter | `linies_mes` | Disponible | Recompte de trajectes segons l'estat de l'última parada | Suma |
| `retard_mitja` | Continu, minuts | `estacions_mes`, `linies_mes`, `linies_dia` | Disponible | Retard mitjà de les parades (`avg_delay`) | Mitjana ponderada per `parades_servides`, o per `pes` a la taula diària; mai mitjana simple |
| `retard_final` | Continu, minuts | `linies_mes` | Disponible | Retard mitjà a l'última parada del trajecte (`avg_end_delays`) | Mitjana ponderada per trajectes |
| `prop_tram_1` … `prop_tram_180`, `prop_tram_sense_dada` | Proporció (0–1) | `estacions_mes`, `linies_mes` | Disponible | Part de les parades registrades que cau en cada tram de retard | Es reconverteix a recompte abans de sumar |
| `prop_final_tram_1` … `prop_final_tram_sense_dada` | Proporció (0–1) | `linies_mes` | Disponible | El mateix, per a l'última parada del trajecte | Es reconverteix a recompte abans de sumar |
| `pes` | Enter | `linies_dia` | Disponible | Pes de l'observació diària que dona l'API per ponderar el retard | Suma |
| `n_estacions` | Enter | `linies_mes` | Disponible | Nombre d'estacions de la línia | No s'agrega |
| `trens_programats`, `trens_realitzats` | Enter | `renfe_nucli_mes` | Disponible | Trens programats i realitzats segons Renfe | Suma |
| `trens_amb_arribada` | Enter | `renfe_nucli_mes` | Disponible | Trens realitzats amb retard a l'arribada registrat, sense els serveis amb autobús | Suma |
| `puntualitat_oficial_5`, `puntualitat_oficial_15`, `puntualitat_oficial_30`, `puntualitat_oficial_60` | Proporció (0–1) | `renfe_nucli_mes` | Disponible | Trens que arriben al destí final amb retard igual o inferior a 5, 15, 30 i 60 minuts, segons Renfe | Ponderada per `trens_amb_arribada` |
| `parades_puntuals`, `parades_impuntuals` | Enter | `renfe_nucli_mes` | Disponible | Parades amb desviació de fins a 3 minuts sobre l'horari, i la resta, segons Renfe | Suma |
| `parades_regulars`, `parades_irregulars` | Enter | `renfe_nucli_mes` | Disponible | Parades que mantenen o no la freqüència respecte del tren anterior | Suma |
| `parades_circulades`, `parades_suprimides` | Enter | `renfe_nucli_mes` | Disponible | Parades servides i parades suprimides segons Renfe | Suma |
| `minuts_retard_renfe`, `minuts_retard_adif`, `minuts_retard_externes`, `minuts_retard_altres_operadors`, `minuts_retard_total` | Enter, minuts | `renfe_nucli_mes` | Disponible | Minuts de retard a l'arribada per incidències, segons a qui s'atribueixen | Suma |
| `viatgers` | Enter | `renfe_nucli_mes` | Disponible | Viatgers transportats per mes; només per a Rodalia de Barcelona, l'únic nucli on la xifra s'ha pogut validar | Suma |
| `retard_franja` | Continu, minuts | Per construir | Pendent (descàrrega amb `--tot`) | Retard mitjà per franja horària | Mitjana ponderada |
| `poblacio`, `poblacio_dones` | Enter | `estacions_municipi` | Disponible | Població total i de dones del municipi | Suma |
| `renda_per_habitant` | Continu, euros | `estacions_municipi` | Disponible | Renda familiar disponible bruta per habitant del municipi, o de la comarca quan Idescat no publica la municipal; la columna `renda_ambit` indica quina és | No s'agrega; és un atribut del municipi |

### Variables derivades

| Variable | Càlcul | Taula | Estat | Què permet veure |
| --- | --- | --- | --- | --- |
| `parades_servides` | `parades_arribada` + `parades_sortida` | `estacions_mes` | Disponible | Denominador correcte per al retard |
| `puntualitat_5` | `prop_tram_1` + `prop_tram_5` | `estacions_mes`, `linies_mes` | Disponible | Part de les parades amb fins a 5 minuts de retard |
| `puntualitat_final_5` | `prop_final_tram_1` + `prop_final_tram_5` | `linies_mes` | Disponible | El mateix al destí final, comparable amb la puntualitat oficial |
| `taxa_retard_greu` | `prop_tram_20` + `prop_tram_25` + `prop_tram_30` + `prop_tram_180` | `estacions_mes` | Disponible | Retards de més de 15 minuts, que fan perdre enllaços |
| `taxa_cancellacio` | `parades_cancellades` / `parades_registrades` | `estacions_mes` | Disponible | Cancel·lacions captades per les dades ciutadanes, que n'infracompten el nombre |
| `minuts_perduts` | `retard_mitja` × `parades_servides` | `estacions_mes` | Disponible | Volum total de retard, per comparar estacions grans i petites |
| `dist_sants_km` | Distància geodèsica entre l'estació i Barcelona-Sants | `estacions_mes` | Disponible | Gradient centre–perifèria |
| `n_linies` | Nombre de línies que inclouen l'estació aquell mes | `estacions_mes` | Disponible | Distingeix intercanviadors d'estacions terminals |
| `acumulacio_retard` | `retard_final` − `retard_mitja` | `linies_mes` | Disponible | Si el retard creix al llarg del recorregut |
| `retard_abans`, `retard_despres`, `canvi_post_gelida` | Mitjana de `retard_mitja` ponderada per `pes` abans i després del 20 de gener de 2026, i la diferència | `linies_gelida` | Disponible | Impacte i recuperació per línia |
| `compliment_servei` | `trens_realitzats` / `trens_programats` | `renfe_nucli_mes` | Disponible | Part dels trens programats que han circulat |
| `compliment_horari` | `parades_puntuals` / (`parades_puntuals` + `parades_impuntuals`) | `renfe_nucli_mes` | Disponible | Mesura oficial de puntualitat per parada, amb llindar de 3 minuts |
| `taxa_suprimides` | `parades_suprimides` / (`parades_circulades` + `parades_suprimides`) | `renfe_nucli_mes` | Disponible | Servei no prestat segons la font oficial |
| `quota_renfe` | `minuts_retard_renfe` / `minuts_retard_total` | `renfe_nucli_mes` | Disponible | Part del retard que la font oficial atribueix a l'operadora |
| `bretxa_parada` | `compliment_horari` de Rodalia de Barcelona − `puntualitat_5` de les seves línies, per mes | `bretxes_mes` | Disponible | Distància entre la mesura oficial i la ciutadana per parada |
| `bretxa_desti` | `puntualitat_oficial_5` de Rodalia de Barcelona − `puntualitat_final_5` de les seves línies, per mes | `bretxes_mes` | Disponible | Distància entre la mesura oficial i la ciutadana al destí final |

### Precaucions per no distorsionar els fets

- **Percentatges i mitjanes no se sumen ni es fan mitjanes simples.** Tota agregació es fa tornant als recomptes (parades, circulacions) i recalculant.
- **Cancel·lada no vol dir retard zero.** Les parades cancel·lades, pendents i desconegudes s'exclouen del retard mitjà i es mostren a part.
- **Una dimensió no és un fet.** El tram de retard i el llindar són dimensions que classifiquen parades; el fet és el nombre de parades de cada tram.
- **Les dues puntualitats mesuren fets diferents.** L'oficial compta trens al destí final; la ciutadana, parades. Es mostraran amb la seva definició i no es presentaran com una mateixa magnitud.
- **Interpretació dels trams.** La correspondència exacta de les claus d'`avg_scores` amb els intervals de minuts es va deduir dels valors i l'autor de Puntual.cat la va confirmar per correu el 20 de novembre de 2026: els valors delimiten els trams.
- **Atributs municipals.** Renda i població descriuen el municipi, no els viatgers de l'estació.

## 8. Fonts i referències

**Dades**

- [Puntual.cat – Estadístiques](https://www.puntual.cat/dades/estadistica) i [descripció de les fonts](https://www.puntual.cat/sobre). Consultat el 14 de novembre de 2026.
- [Renfe – Puntualitat en els serveis de Rodalia](https://grupo.renfe.com/es/es/gobierno-y-transparencia/puntualidad-en-los-servicios/cercanias). Consultat el 14 de novembre de 2026.
- [Renfe Data – Catàleg de conjunts de dades](https://data.renfe.com/dataset).
- [Idescat – Institut d'Estadística de Catalunya](https://www.idescat.cat/).
- [Idescat – API «El municipi en xifres»](https://api.idescat.cat/emex/v1/nodes.json?tipus=mun&lang=ca). Consultat el 14 de novembre de 2026.
- [ICGC – Geocodificador invers](https://eines.icgc.cat/geocodificador/invers?lat=41.379079&lon=2.140284&size=1). Consultat el 14 de novembre de 2026.
- Comunicació personal amb l'autor de Puntual.cat, 20 de novembre de 2026: confirma la interpretació d'`avg_scores` i dóna el vistiplau a la reutilització de les dades de l'API.

**Context**

- [Metròpoli Abierta, 14 de novembre de 2026: radiografia del caos a Rodalies](https://metropoliabierta.cat/mobilitat/20261114/radiografia-caos-rodalies-set-trens-arribar-tard-loctubre-sagreuja-novembre/1003742812067_0.html).
- [ElNacional.cat: Rodalies, al límit](https://elnacional.cat/ca/societat/rodalies-limit-set-cada-deu-trens-arriben-tard-puntualitat-enfonsa_1725581_102.html).
- [3CatInfo: mig any des de l'accident de Gelida](https://www.3cat.cat/3catinfo/mig-any-des-de-laccident-de-gelida-menys-viatgers-al-tren-i-continuen-els-retards/noticia-amp/3420943/).
- [3CatInfo: els informàtics que han posat Rodalies al descobert](https://www.3cat.cat/esport3/els-informatics-que-han-posat-rodalies-al-descobert-es-pitjor-del-que-pensava/noticia/3421013/).
- [Diari de Tarragona, 28 de gener de 2026: Rodalies de Barcelona compleix la meitat dels horaris el 2025](https://www.diaridetarragona.com/catalunya/250829/rodalies-barcelona-cumple-mitad-horarios-programados-2025.html).
- [ARA: per què Renfe diu que els trens només van arribar 2,5 minuts tard](https://en.ara.cat/society/why-does-renfe-say-that-the-trains-were-only-2-5-minutes-late-in-the-middle-of-the-rodalies-chaos_1_5705508.amp.html).
- [Sostenible.cat (AMB i TMB): la mobilitat des de l'òptica de les dones](https://www.sostenible.cat/print/noticia/mobilitat-des-de-loptica-de-les-dones), amb dades de l'EMEF 2022.
- [Idescat: renda familiar disponible bruta territorial](https://www.idescat.cat/dades/rfdbc/rfdbc2022ca.html).

**Materials de l'assignatura**

- Giménez, X.; Minguillón, J. *Aspectes a considerar per la Pràctica de visualització de dades*. UOC.
- Minguillón, J. (2024). *Introducció a la preparació de dades*. UOC.

**Metodologia**

- Fry, B. (2004). *Computational Information Design*. Tesi doctoral, Massachusetts Institute of Technology.
- Stefaner, M. *Information Visualization workflow*. Citat a la guia de l'assignatura.