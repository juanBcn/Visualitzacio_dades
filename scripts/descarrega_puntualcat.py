#!/usr/bin/env python3
"""
Descarrega les dades mensuals de l'API de Puntual.cat i construeix taules tidy,
amb les variables derivades que descriu el diccionari de la PR1.

Ús (des de l'arrel del repositori):
    pip install -r requirements.txt
    python scripts/descarrega_puntualcat.py          # estacions, línies i sèrie diària
    python scripts/descarrega_puntualcat.py --tot    # també franges horàries (només a raw/)

Sortida (carpeta ./puntualcat):
    raw/<endpoint>_<mes>.json   còpia literal de cada resposta (memòria cau)
    estacions_mes.csv           taula principal: una fila per estació i mes
    linies_mes.csv              una fila per línia, sentit, tipus de dia i mes
                                (sentit o tipus_dia = ANY són agregats ja calculats:
                                no s'han de sumar amb les files de detall; la columna
                                es_agregat els marca)
    linies_dia.csv              una fila per línia i dia
    linies_gelida.csv           una fila per línia: retard abans i després del 20-01-2026

L'API limita a 12 peticions per minut. L'script n'envia una cada 6 segons i
no repeteix les que ja té desades, de manera que es pot interrompre i reprendre.
Font: https://www.puntual.cat (dades recollides per Transporta'm).
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

API = "https://api.puntual.cat"
PAUSA = 6.0  # segons entre peticions: 10 per minut, per sota del límit de 12
OUT = Path("puntualcat")
RAW = OUT / "raw"
CAPCALERES = {"User-Agent": "practica-visualitzacio-UOC (us academic, no comercial)"}

EXTRES = ["average_delays", "delays_by_time_of_day",
          "scores_by_time_of_day", "scores_by_time_of_year"]

# Noms catalans dels estats de parada de l'API
ESTATS = {
    "arrived": "arribada",
    "departed": "sortida",
    "cancelled": "cancellades",
    "pending": "pendents",
    "unknown": "desconegudes",
    "skipped": "omeses",
    "None": "sense_estat",
}
ESTATS_ESTACIO = ["arrived", "departed", "cancelled", "pending", "unknown"]

# Accident de Gelida: la sèrie diària mostra el salt de retard el 20-01-2026
DATA_GELIDA = "2026-01-20"
MES_GELIDA = "2026-01"

# Barcelona-Sants (coordenades de l'estació renfe-71801 a les mateixes dades)
SANTS_LAT, SANTS_LON = 41.379079, 2.140284
CORONES = [0, 15, 40, 80, np.inf]
ETIQUETES_CORONA = ["1: fins a 15 km", "2: 15-40 km", "3: 40-80 km", "4: mes de 80 km"]

SERVEIS = {
    "Rodalies de Barcelona": {"r1", "r2", "r2n", "r2s", "r3", "r4", "r7", "r8"},
    "Regionals": {"r11", "r13", "r14", "r15", "r16", "r17"},
    "Rodalies de Girona": {"rg1"},
    "Rodalies de Tarragona": {"rt1", "rt2"},
    "Rodalies de Lleida": {"rl3", "rl4"},
}

_ultima = 0.0


# ---------------------------------------------------------------- descàrrega

def demana(ruta):
    """GET amb pausa entre peticions i reintent si salta el límit."""
    global _ultima
    for _ in range(4):
        espera = PAUSA - (time.time() - _ultima)
        if espera > 0:
            time.sleep(espera)
        r = requests.get(f"{API}/{ruta}", headers=CAPCALERES, timeout=60)
        _ultima = time.time()
        try:
            dades = r.json()
        except ValueError:
            dades = {"error": f"resposta no JSON (HTTP {r.status_code})"}
        if isinstance(dades, dict) and "error" in dades and len(dades) == 1:
            print(f"  {ruta}: {dades['error']} -> espero 65 s", file=sys.stderr)
            time.sleep(65)
            continue
        return dades
    raise RuntimeError(f"No s'ha pogut descarregar {ruta}")


def desa_o_llegeix(endpoint, mes):
    fitxer = RAW / f"{endpoint}_{mes}.json"
    if fitxer.exists():
        return json.loads(fitxer.read_text(encoding="utf-8"))
    print(f"  {endpoint} {mes}")
    dades = demana(f"{endpoint}?month={mes}")
    fitxer.write_text(json.dumps(dades, ensure_ascii=False), encoding="utf-8")
    return dades


# ------------------------------------------------------- aplanat de l'API

def nom_tram(tram):
    return "sense_dada" if str(tram) == "-1" else str(tram)


def servei_de(linia_id):
    operador, _, codi = (linia_id or "").partition("-")
    if operador == "fgc":
        return "FGC"
    for servei, codis in SERVEIS.items():
        if codi in codis:
            return servei
    return "Altres"


def taula_estacions(mes, stops):
    """Aplana stops?month=: una fila per estació."""
    files = []
    for estacio_id, s in stops.items():
        fila = {
            "mes": mes,
            "estacio_id": estacio_id,
            "operador": estacio_id.split("-")[0],
            "codi": s.get("code"),
            "estacio_nom": s.get("name"),
            "retard_mitja": s.get("avg_delay"),
            "parades_registrades": s.get("stops_count"),
        }
        m = re.search(r"POINT\(([-\d.]+) ([-\d.]+)\)", s.get("location") or "")
        fila["lon"], fila["lat"] = (float(m.group(1)), float(m.group(2))) if m else (None, None)
        estats = s.get("smm_status") or {}
        for estat in ESTATS_ESTACIO:
            fila[f"parades_{ESTATS[estat]}"] = estats.get(estat, 0)
        for tram, valor in (s.get("avg_scores") or {}).items():
            fila[f"prop_tram_{nom_tram(tram)}"] = valor
        files.append(fila)
    return files


def taula_linies(mes, lines):
    """Aplana lines?month=: una fila per línia, sentit i tipus de dia."""
    mesures = {
        "avg_delays": "retard_mitja",
        "avg_end_delays": "retard_final",
        "smm_status": "parades",
        "smm_end_status": "trajectes",
        "avg_scores": "prop_tram",
        "avg_end_scores": "prop_final_tram",
    }
    files = {}
    for l in lines:
        base = {
            "mes": mes,
            "linia_id": l.get("line_id"),
            "operador": (l.get("line_id") or "").split("-")[0],
            "servei": servei_de(l.get("line_id")),
            "linia": l.get("route_short_name"),
            "linia_nom": l.get("route_long_name"),
            "n_estacions": len(l.get("stops") or []),
        }
        for clau, prefix in mesures.items():
            for item in l.get(clau) or []:
                k = (base["linia_id"], item.get("METADATA_DIRECTION"), item.get("METADATA_DAYTYPE"))
                fila = files.setdefault(k, {**base, "sentit": k[1], "tipus_dia": k[2]})
                valor = item.get("value")
                if isinstance(valor, dict):
                    for sub, v in valor.items():
                        if prefix in ("parades", "trajectes"):
                            sub = ESTATS.get(str(sub), str(sub))
                        else:
                            sub = nom_tram(sub)
                        fila[f"{prefix}_{sub}"] = v
                else:
                    fila[prefix] = valor
    return list(files.values())


def estacions_per_linia(mes, lines):
    """Parelles (mes, estació, línia) per calcular quantes línies paren a cada estació."""
    return [(mes, e, l.get("line_id")) for l in lines for e in (l.get("stops") or [])]


def taula_dies(mes, per_dia):
    """Aplana delays_by_time_of_year?month=: una fila per línia i dia."""
    files = []
    for linia_id, bloc in per_dia.items():
        if not isinstance(bloc, dict) or "dates" not in bloc:
            continue
        pesos = bloc.get("weights") or [None] * len(bloc["dates"])
        for data, retard, pes in zip(bloc["dates"], bloc.get("delays") or [], pesos):
            files.append({"mes": mes, "linia_id": linia_id,
                          "operador": linia_id.split("-")[0], "servei": servei_de(linia_id),
                          "data": str(data)[:10], "retard_mitja": retard, "pes": pes})
    return files


# ------------------------------------------------------ variables derivades

def distancia_km(lat, lon, lat0=SANTS_LAT, lon0=SANTS_LON):
    """Distància geodèsica (haversine) en quilòmetres."""
    lat, lon, lat0, lon0 = map(np.radians, (lat, lon, lat0, lon0))
    a = np.sin((lat - lat0) / 2) ** 2 + np.cos(lat0) * np.cos(lat) * np.sin((lon - lon0) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def suma_trams(df, prefix, trams):
    cols = [f"{prefix}_{t}" for t in trams if f"{prefix}_{t}" in df.columns]
    return df[cols].sum(axis=1, min_count=1)


def deriva_estacions(df, parelles=None):
    df = df.copy()
    df["periode"] = np.where(df["mes"] < MES_GELIDA, "abans_gelida", "despres_gelida")
    df["parades_servides"] = df["parades_arribada"] + df["parades_sortida"]
    df["puntualitat_5"] = suma_trams(df, "prop_tram", [1, 5])
    df["taxa_retard_greu"] = suma_trams(df, "prop_tram", [20, 25, 30, 180])
    df["taxa_cancellacio"] = df["parades_cancellades"] / df["parades_registrades"]
    df["minuts_perduts"] = df["retard_mitja"] * df["parades_servides"]
    df["dist_sants_km"] = distancia_km(df["lat"], df["lon"]).round(1)
    df["corona"] = pd.cut(df["dist_sants_km"], CORONES, labels=ETIQUETES_CORONA,
                          include_lowest=True).astype("string")
    if parelles is not None and len(parelles):
        n = (parelles.drop_duplicates().groupby(["mes", "estacio_id"])["linia_id"]
             .nunique().rename("n_linies").reset_index())
        df = df.merge(n, on=["mes", "estacio_id"], how="left")
    return df


def deriva_linies(df):
    df = df.copy()
    df["es_agregat"] = (df["sentit"] == "ANY") | (df["tipus_dia"] == "ANY")
    df["periode"] = np.where(df["mes"] < MES_GELIDA, "abans_gelida", "despres_gelida")
    df["acumulacio_retard"] = df["retard_final"] - df["retard_mitja"]
    df["puntualitat_5"] = suma_trams(df, "prop_tram", [1, 5])
    df["puntualitat_final_5"] = suma_trams(df, "prop_final_tram", [1, 5])
    return df


def deriva_dies(df):
    df = df.copy()
    df["periode"] = np.where(df["data"] < DATA_GELIDA, "abans_gelida", "despres_gelida")
    return df


def canvi_gelida(dies):
    """Retard mitjà ponderat per línia abans i després de l'accident, i la diferència."""
    d = dies.dropna(subset=["retard_mitja", "pes"]).copy()
    d["rp"] = d["retard_mitja"] * d["pes"]
    g = d.groupby(["linia_id", "operador", "servei", "periode"])[["rp", "pes"]].sum()
    g["retard"] = g["rp"] / g["pes"]
    t = g["retard"].unstack("periode").reset_index()
    for c in ("abans_gelida", "despres_gelida"):
        if c not in t.columns:
            t[c] = np.nan
    t = t.rename(columns={"abans_gelida": "retard_abans", "despres_gelida": "retard_despres"})
    t["canvi_post_gelida"] = t["retard_despres"] - t["retard_abans"]
    return t


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tot", action="store_true", help="descarrega també els endpoints extra")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    mesos = demana("months")
    print(f"{len(mesos)} mesos: {mesos[0]} - {mesos[-1]}")

    estacions, linies, dies, parelles = [], [], [], []
    for mes in mesos:
        estacions += taula_estacions(mes, desa_o_llegeix("stops", mes))
        lines = desa_o_llegeix("lines", mes)
        linies += taula_linies(mes, lines)
        parelles += estacions_per_linia(mes, lines)
        dies += taula_dies(mes, desa_o_llegeix("delays_by_time_of_year", mes))
        if args.tot:
            for e in EXTRES:
                desa_o_llegeix(e, mes)

    parelles = pd.DataFrame(parelles, columns=["mes", "estacio_id", "linia_id"])
    est = deriva_estacions(pd.DataFrame(estacions), parelles)
    lin = deriva_linies(pd.DataFrame(linies))
    dia = deriva_dies(pd.DataFrame(dies))
    gel = canvi_gelida(dia)

    est.to_csv(OUT / "estacions_mes.csv", index=False)
    lin.to_csv(OUT / "linies_mes.csv", index=False)
    dia.to_csv(OUT / "linies_dia.csv", index=False)
    gel.to_csv(OUT / "linies_gelida.csv", index=False)

    print(f"estacions_mes.csv: {len(est)} files x {est.shape[1]} columnes")
    print(f"linies_mes.csv:    {len(lin)} files x {lin.shape[1]} columnes "
          f"({int((~lin.es_agregat).sum())} de detall)")
    print(f"linies_dia.csv:    {len(dia)} files x {dia.shape[1]} columnes")
    print(f"linies_gelida.csv: {len(gel)} files x {gel.shape[1]} columnes")


if __name__ == "__main__":
    main()