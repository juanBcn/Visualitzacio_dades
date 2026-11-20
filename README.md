# Visualització de dades · Pràctica final

Pràctica de l'assignatura de Visualització de dades del màster de Ciència de Dades (UOC).

**Autor:** Juan Rogel Navarro · Màster universitari de Ciència de Dades, UOC · 14 de novembre de 2026

**Tema:** puntualitat i incidències ferroviàries a Catalunya. Qui pateix els retards del tren, on i quan, i fins a quin punt la resposta depèn de qui mesura.

## Contingut

| Ruta | Què és |
| --- | --- |
| `docs/PR1_seleccio_conjunt_dades.md` | Part I: selecció del conjunt de dades, objectius i diccionari de variables |
| `scripts/descarrega_puntualcat.py` | Descàrrega de les estadístiques mensuals de Puntual.cat i construcció de les taules |
| `scripts/descarrega_renfe.py` | Descàrrega dels indicadors oficials de Renfe per nucli i mes |
| `scripts/descarrega_idescat.py` | Municipi de cada estació (ICGC) i població i renda municipals (Idescat) |
| `scripts/calcula_bretxes.py` | Bretxa mensual entre la mesura oficial i la ciutadana a Rodalia de Barcelona |
| `puntualcat/*.csv` | Taules generades pels scripts |
| `puntualcat/raw/` | Respostes originals de l'API de Puntual.cat (JSON), punt de partida de les transformacions |
| `puntualcat/raw_idescat/` | Respostes originals de l'ICGC i de l'Idescat (JSON) |
| `requirements.txt` | Dependències de Python |

## Fonts de dades

- [Puntual.cat](https://www.puntual.cat/dades/estadistica): retard per estació, línia i dia de Rodalies i FGC, amb dades recollides per Transporta'm.
- [Renfe – Puntualitat en els serveis de Rodalia](https://grupo.renfe.com/es/es/gobierno-y-transparencia/puntualidad-en-los-servicios/cercanias): indicadors oficials per nucli i mes.
- [Renfe Data](https://data.renfe.com/dataset): estacions i horaris programats.
- [Idescat](https://www.idescat.cat/): població i renda per municipi.

## Com descarregar les dades

```bash
pip install -r requirements.txt
python scripts/descarrega_puntualcat.py          # estacions, línies i sèrie diària
python scripts/descarrega_puntualcat.py --tot    # també franges horàries
python scripts/descarrega_renfe.py               # indicadors oficials de Renfe
python scripts/descarrega_idescat.py             # municipi, població i renda de cada estació
python scripts/calcula_bretxes.py                # bretxa entre la mesura oficial i la ciutadana
```

L'API de Puntual.cat admet 12 peticions per minut. L'script n'envia una cada 6 segons, desa cada resposta a `puntualcat/raw/` i no repeteix les que ja té, de manera que es pot interrompre i reprendre. La descàrrega bàsica triga uns 7 minuts.

Sortida, a la carpeta `puntualcat/`:

- `estacions_mes.csv`: una fila per estació i mes (taula principal), amb les variables derivades.
- `linies_mes.csv`: una fila per línia, sentit, tipus de dia i mes. Les files amb `es_agregat` cert són totals ja calculats i no s'han de sumar amb les de detall.
- `linies_dia.csv`: una fila per línia i dia.
- `linies_gelida.csv`: una fila per línia, amb el retard abans i després del 20 de gener de 2026.
- `renfe_nucli_mes.csv`: una fila per nucli de Rodalia i mes, amb els indicadors oficials de Renfe.
- `estacions_municipi.csv`: una fila per estació, amb el municipi, la població per sexe i la renda per habitant.
- `bretxes_mes.csv`: una fila per mes, amb la bretxa entre la mesura oficial i la ciutadana a Rodalia de Barcelona.

El significat de cada columna és al diccionari de variables de `docs/PR1_seleccio_conjunt_dades.md`.

## Ús de les dades

Les taules generades s'inclouen al repositori per facilitar l'avaluació de la pràctica. Les respostes en brut de les API no s'hi inclouen: es regeneren amb els scripts.

Puntual.cat i l'informe de Renfe no indiquen llicència de reutilització. L'ús que se'n fa aquí és acadèmic i no comercial, citant-ne la font, i s'ha demanat permís a l'autor de Puntual.cat. Si algun dels titulars no n'autoritza la publicació, les taules es retiraran. Les dades d'Idescat i de l'ICGC es publiquen amb llicència oberta.