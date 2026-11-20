#!/usr/bin/env python3
"""
Assigna a cada estació el seu municipi i hi afegeix població i renda d'Idescat.

Passos:
  1. Llegeix les estacions de puntualcat/estacions_mes.csv (cal haver executat abans
     scripts/descarrega_puntualcat.py).
  2. Per a cada estació, demana al geocodificador invers de l'ICGC a quin municipi
     pertanyen les seves coordenades. Les estacions de fora de Catalunya queden sense municipi.
  3. Per a cada municipi, demana a l'API «El municipi en xifres» d'Idescat la població
     per sexe i la renda familiar disponible bruta (RFDB) per habitant. Quan Idescat no
     publica la renda del municipi (municipis petits), es fa servir la de la comarca.

Ús (des de l'arrel del repositori):
    python scripts/descarrega_idescat.py

Sortida:
    puntualcat/estacions_municipi.csv   una fila per estació
    puntualcat/raw_idescat/             còpia de cada resposta (memòria cau)

Fonts: Institut Cartogràfic i Geològic de Catalunya (https://eines.icgc.cat/geocodificador)
i Institut d'Estadística de Catalunya (https://api.idescat.cat/emex/v1).
"""
import json
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path("puntualcat")
RAW = OUT / "raw_idescat"
ICGC = "https://eines.icgc.cat/geocodificador/invers"
EMEX = "https://api.idescat.cat/emex/v1/dades.json"
CAPCALERES = {"User-Agent": "practica-visualitzacio-UOC (us academic, no comercial)"}
PAUSA = 0.3

# Indicadors d'«El municipi en xifres»
INDICADORS = {
    "f321": "poblacio",
    "f320": "poblacio_dones",
    "f318": "poblacio_homes",
    "f7": "renda_per_habitant",     # RFDB per habitant, en euros
}


def amb_cau(fitxer, url, params):
    """Descarrega un JSON o el llegeix del disc si ja s'havia demanat."""
    if fitxer.exists():
        return json.loads(fitxer.read_text(encoding="utf-8"))
    time.sleep(PAUSA)
    r = requests.get(url, params=params, headers=CAPCALERES, timeout=60)
    r.raise_for_status()
    dades = r.json()
    fitxer.write_text(json.dumps(dades, ensure_ascii=False), encoding="utf-8")
    return dades


def municipi_de(estacio_id, lon, lat):
    """Municipi i comarca del punt, segons l'element més proper que torna l'ICGC."""
    dades = amb_cau(RAW / f"icgc_{estacio_id}.json", ICGC, {"lat": lat, "lon": lon, "size": 1})
    candidats = [f["properties"] for f in dades.get("features", [])
                 if f.get("properties", {}).get("id_municipi")]
    if not candidats:
        return {"municipi_id": None, "municipi": None, "comarca": None}
    p = min(candidats, key=lambda x: x.get("distancia", 1e9))
    return {"municipi_id": p["id_municipi"], "municipi": p.get("municipi"), "comarca": p.get("comarca")}


def cerca_indicadors(node, any_pare=None, trobats=None):
    """Recorre la fitxa d'Idescat i recull els indicadors d'INDICADORS amb el seu any."""
    if trobats is None:
        trobats = {}
    if isinstance(node, list):
        for x in node:
            cerca_indicadors(x, any_pare, trobats)
    elif isinstance(node, dict):
        any_ = node.get("r", any_pare)
        if node.get("id") in INDICADORS and "v" in node:
            trobats[node["id"]] = (node["v"], any_)
        for v in node.values():
            if isinstance(v, (dict, list)):
                cerca_indicadors(v, any_, trobats)
    return trobats


def numero(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def dades_municipi(codi):
    """Població i renda del municipi, i renda de la seva comarca quan la fitxa la porta."""
    fitxa = amb_cau(RAW / f"emex_{codi}.json", EMEX, {"id": codi, "lang": "ca"})
    trobats = cerca_indicadors(fitxa)
    fila = {"municipi_id": codi}
    for ind, nom in INDICADORS.items():
        valors, any_ = trobats.get(ind, ("_,_,_", None))
        mun, com, _cat = (valors.split(",") + ["_", "_", "_"])[:3]   # municipi, comarca, Catalunya
        v = numero(mun)
        if nom == "renda_per_habitant":
            fila["renda_ambit"] = "municipi" if v is not None else None
            fila["renda_comarca"] = numero(com)
            fila["any_renda"] = any_
        elif nom == "poblacio":
            fila["any_poblacio"] = any_
        fila[nom] = v
    return fila


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    est = pd.read_csv(OUT / "estacions_mes.csv")
    est = (est.sort_values("mes").drop_duplicates("estacio_id", keep="last")
           [["estacio_id", "estacio_nom", "operador", "lon", "lat"]])
    print(f"{len(est)} estacions")

    geo = [{"estacio_id": r.estacio_id, **municipi_de(r.estacio_id, r.lon, r.lat)}
           for r in est.itertuples()]
    t = est.merge(pd.DataFrame(geo), on="estacio_id")

    codis = sorted(t["municipi_id"].dropna().unique())
    print(f"{len(codis)} municipis")
    mun = pd.DataFrame([dades_municipi(c) for c in codis])
    t = t.merge(mun, on="municipi_id", how="left")

    # Idescat no publica la renda dels municipis petits: s'hi posa la de la comarca,
    # presa de la fitxa d'un altre municipi de la mateixa comarca.
    renda_comarca = t.dropna(subset=["renda_comarca"]).groupby("comarca")["renda_comarca"].first()
    any_renda = t["any_renda"].dropna().iloc[0] if t["any_renda"].notna().any() else None
    sense = t["renda_per_habitant"].isna() & t["comarca"].isin(renda_comarca.index)
    t.loc[sense, "renda_per_habitant"] = t.loc[sense, "comarca"].map(renda_comarca)
    t.loc[sense, "renda_ambit"] = "comarca"
    t.loc[sense, "any_renda"] = any_renda
    t["pct_dones"] = t["poblacio_dones"] / t["poblacio"]

    cols = ["estacio_id", "estacio_nom", "operador", "municipi_id", "municipi", "comarca",
            "poblacio", "poblacio_dones", "poblacio_homes", "pct_dones", "any_poblacio",
            "renda_per_habitant", "renda_ambit", "any_renda"]
    t[cols].to_csv(OUT / "estacions_municipi.csv", index=False)

    fora = int(t["municipi_id"].isna().sum())
    print(f"estacions_municipi.csv: {len(t)} files x {len(cols)} columnes")
    print(f"  {fora} estacions sense municipi (fora de Catalunya)")
    print(f"  renda municipal: {int((t.renda_ambit == 'municipi').sum())} estacions; "
          f"comarcal: {int((t.renda_ambit == 'comarca').sum())}")


if __name__ == "__main__":
    main()