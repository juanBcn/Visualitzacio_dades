#!/usr/bin/env python3
"""
Descarrega indicadors oficials de Rodalia de l'informe públic de puntualitat de Renfe
(https://grupo.renfe.com/es/es/gobierno-y-transparencia/puntualidad-en-los-servicios/cercanias)
i els agrega per nucli i mes.

L'informe és un Power BI publicat al web, sense botó de descàrrega. Aquest script fa
consultes agregades al mateix model de dades que fa servir l'informe i en desa el resultat.
Només demana recomptes i totals per nucli; no baixa registres de trens individuals.

Ús (des de l'arrel del repositori):
    python scripts/descarrega_renfe.py

Sortida:
    puntualcat/renfe_nucli_mes.csv   una fila per nucli i mes

Validació feta el 14-11-2026 contra el que mostra l'informe:
    - compliment_servei i compliment_horari: Astúries i Rodalia de Barcelona, setembre de 2026
    - puntualitat_oficial_5/15/30/60: mateixos nuclis i mes, diferència màxima de 0,1 punts
    - viatgers (només Rodalia de Barcelona): gener-maig de 2025 i de 2026
    - minuts de retard per origen: quota de Renfe a Rodalia de Barcelona el 2025
El retard mitjà oficial no s'inclou perquè no s'ha pogut reproduir el valor de l'informe.
"""
import re
import sys
from pathlib import Path

import pandas as pd
import requests

RESOURCE_KEY = "4ec7240f-a23a-4333-a438-a668b1d239ec"   # clau pública de l'informe
BASE = "https://wabi-north-europe-l-primary-api.analysis.windows.net/public/reports/"
CAPCALERES = {
    "X-PowerBI-ResourceKey": RESOURCE_KEY,
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json",
    "User-Agent": "practica-visualitzacio-UOC (us academic, no comercial)",
}
OUT = Path("puntualcat")
PRIMER_MES = "2025-01"   # l'informe publica dades de Rodalia des del gener de 2025
MES_GELIDA = "2026-01"

# Nom de l'àrea al model -> nom del nucli (ample ibèric; les xarxes de via estreta queden fora)
NUCLIS = {
    "CERCANIAS ASTURIAS": "Astúries",
    "CERCANIAS BILBAO": "Bilbao",
    "CERCANIAS CADIZ": "Cadis",
    "CERCANIAS DE MADRID": "Madrid",
    "CERCANIAS MALAGA": "Màlaga",
    "CERCANIAS MURCIA": "Múrcia/Alacant",
    "CERCANIAS SAN SEBASTIAN": "Sant Sebastià",
    "CERCANIAS SANTANDER": "Cantàbria",
    "CERCANIAS SEVILLA": "Sevilla",
    "CERCANIAS VALENCIA": "València",
    "CERCANIAS ZARAGOZA": "Saragossa",
    "RODALIES BARCELONA": "Rodalia de Barcelona",
}
# Les taules de viatgers fan servir un altre nom per a cada nucli
NUCLIS_VIATGERS = {
    "ASTURIAS": "Astúries", "BILBAO": "Bilbao", "CADIZ": "Cadis", "MADRID": "Madrid",
    "MALAGA": "Màlaga", "MURCIA": "Múrcia/Alacant", "SAN SEBASTIAN": "Sant Sebastià",
    "SANTANDER": "Cantàbria", "SEVILLA": "Sevilla", "VALENCIA": "València",
    "ZARAGOZA": "Saragossa", "BARCELONA": "Rodalia de Barcelona",
}
# Origen de la incidència al model -> columna de sortida
ORIGENS = {
    "D.G.V.": "minuts_retard_renfe",          # Renfe Viatgers
    "ADIF": "minuts_retard_adif",             # infraestructura i gestió de la circulació
    "EXTERNAS": "minuts_retard_externes",
    "OTROS OPERADORES": "minuts_retard_altres_operadors",
}
LLINDARS = [5, 15, 30, 60]
SUMA, MINIM, MAXIM, RECOMPTE = 0, 3, 4, 5   # codis d'agregació de Power BI


def get(ruta):
    r = requests.get(BASE + ruta, headers=CAPCALERES, timeout=60)
    r.raise_for_status()
    return r.json()


def llegeix_dsr(resposta):
    """Converteix la resposta comprimida de Power BI (DSR) en una llista de files."""
    dades = resposta["results"][0]["result"]["data"]
    if "dsr" not in dades or "DS" not in dades["dsr"]:
        raise RuntimeError("Resposta inesperada: " + str(dades.get("dsr"))[:400])
    ds = dades["dsr"]["DS"][0]
    diccionaris = ds.get("ValueDicts", {})
    files, anterior, esquema = [], [], None
    for bloc in ds["PH"]:
        for registres in bloc.values():
            for reg in registres:
                if "S" in reg:
                    esquema = reg["S"]
                repetits, nuls = reg.get("R", 0), reg.get("Ø", 0)
                valors = iter(reg.get("C", []))
                fila = []
                for i in range(len(esquema)):
                    if repetits & (1 << i):
                        v = anterior[i]
                    elif nuls & (1 << i):
                        v = None
                    else:
                        v = next(valors)
                        dn = esquema[i].get("DN")
                        if dn and isinstance(v, int):
                            v = diccionaris[dn][v]
                    fila.append(v)
                files.append(fila)
                anterior = fila
    return files, bool(ds.get("RT"))


def consulta(model, entitat, columnes, agregats, filtres=(), finestra=30000):
    """Agrupa `entitat` per `columnes` i calcula `agregats` = [(columna, codi), ...].

    `filtres` = [(columna, valor), ...] restringeix les files abans d'agrupar.
    """
    font = {"SourceRef": {"Source": "t"}}
    select = [{"Column": {"Expression": font, "Property": c}, "Name": "t." + c} for c in columnes]
    select += [{"Aggregation": {"Expression": {"Column": {"Expression": font, "Property": c}},
                                "Function": f}, "Name": f"A{f}({c})"} for c, f in agregats]
    query = {"Version": 2, "From": [{"Name": "t", "Entity": entitat, "Type": 0}], "Select": select}
    if filtres:
        query["Where"] = [{"Condition": {"In": {
            "Expressions": [{"Column": {"Expression": font, "Property": c}}],
            "Values": [[{"Literal": {"Value": f"'{v}'"}}]]}}} for c, v in filtres]
    cos = {
        "version": "1.0.0",
        "queries": [{"Query": {"Commands": [{"SemanticQueryDataShapeCommand": {
            "Query": query,
            "Binding": {"Primary": {"Groupings": [{"Projections": list(range(len(select)))}]},
                        "DataReduction": {"DataVolume": 4,
                                          "Primary": {"Window": {"Count": finestra}}},
                        "Version": 1}}}]}, "QueryId": ""}],
        "cancelQueries": [],
        "modelId": model,
    }
    r = requests.post(BASE + "querydata?synchronous=true", headers=CAPCALERES, json=cos, timeout=180)
    r.raise_for_status()
    files, truncat = llegeix_dsr(r.json())
    if truncat:
        print(f"  Avís: {entitat} ha tornat dades truncades", file=sys.stderr)
    noms = list(columnes) + [f"{c}__{f}" for c, f in agregats]
    return pd.DataFrame(files, columns=noms)


def mes_de_ms(serie):
    return pd.to_datetime(pd.to_numeric(serie), unit="ms").dt.strftime("%Y-%m")


# ------------------------------------------------------------------ blocs

def trens(model):
    """Trens programats i realitzats per nucli i mes."""
    c = consulta(model, "Circulaciones RealPro",
                 ["Area de Gestion Prestadora", "Año", "Mes numero"],
                 [("Programadas", SUMA), ("Realizadas", SUMA)])
    c = c[c["Area de Gestion Prestadora"].isin(NUCLIS)].copy()
    c["mes"] = (c["Año"].astype(int).astype(str) + "-"
                + c["Mes numero"].astype(int).astype(str).str.zfill(2))
    c["nucli"] = c["Area de Gestion Prestadora"].map(NUCLIS)
    c["trens_programats"] = pd.to_numeric(c[f"Programadas__{SUMA}"], errors="coerce")
    c["trens_realitzats"] = pd.to_numeric(c[f"Realizadas__{SUMA}"], errors="coerce")
    return c[["mes", "nucli", "trens_programats", "trens_realitzats"]]


def parades(model):
    """Parades puntuals (fins a 3 minuts), regulars, circulades i suprimides."""
    cols = ["PUNTUALES", "IMPUNTUALES", "REGULAR", "IRREGULAR", "CIRCULADOS", "SUPRIMIDOS"]
    g = consulta(model, "Regularidad_R", ["NUCLEO", "FECHA"], [(c, SUMA) for c in cols])
    g = g[g["NUCLEO"].isin(NUCLIS)].dropna(subset=["FECHA"]).copy()
    g["mes"] = mes_de_ms(g["FECHA"])
    g["nucli"] = g["NUCLEO"].map(NUCLIS)
    noms = {"PUNTUALES": "parades_puntuals", "IMPUNTUALES": "parades_impuntuals",
            "REGULAR": "parades_regulars", "IRREGULAR": "parades_irregulars",
            "CIRCULADOS": "parades_circulades", "SUPRIMIDOS": "parades_suprimides"}
    for c, nou in noms.items():
        g[nou] = pd.to_numeric(g[f"{c}__{SUMA}"], errors="coerce")
    return g.groupby(["mes", "nucli"], as_index=False)[list(noms.values())].sum()


def puntualitat(model, entitats):
    """Trens que arriben al destí final amb un retard igual o inferior a cada llindar.

    Les dades són en una taula per mes. S'hi compten trens per minuts de retard a
    l'arribada, sense els serveis substitutoris amb autobús, com fa l'informe.
    """
    taules = sorted(e for e in entitats if re.fullmatch(r"Puntualidad_Cercanias_20\d\d_\d+", e))
    files = []
    for t in taules:
        any_, mes = re.fullmatch(r"Puntualidad_Cercanias_(20\d\d)_(\d+)", t).groups()
        print(f"  {t}")
        d = consulta(model, t,
                     ["Area de Gestion Prestadora", "Minutos Llegada Tren",
                      "Circulaciones Realizadas", "Serie Generica"],
                     [("Tren Produccion", RECOMPTE)])
        d = d[d["Area de Gestion Prestadora"].isin(NUCLIS)
              & (d["Circulaciones Realizadas"].astype(str) == "1")
              & ~d["Serie Generica"].fillna("").str.startswith("Autob")].copy()
        d["minuts"] = pd.to_numeric(d["Minutos Llegada Tren"], errors="coerce")
        d["n"] = pd.to_numeric(d[f"Tren Produccion__{RECOMPTE}"], errors="coerce")
        for area, g in d.groupby("Area de Gestion Prestadora"):
            fila = {"mes": f"{any_}-{int(mes):02d}", "nucli": NUCLIS[area],
                    "trens_amb_arribada": g["n"].sum()}
            for ll in LLINDARS:
                fila[f"puntualitat_oficial_{ll}"] = g.loc[g["minuts"] <= ll, "n"].sum() / g["n"].sum()
            files.append(fila)
    return pd.DataFrame(files)


def incidencies(model):
    """Minuts de retard a l'arribada per incidències, segons a qui s'atribueixen."""
    files = []
    for area, nucli in NUCLIS.items():
        d = consulta(model, "Impuntualidad", ["Fecha Tren Incidencia", "Imputabilidad"],
                     [("Retraso a la Llegada", SUMA)],
                     filtres=[("Area de Gestion Prestadora Tren Incidencia", area)])
        d = d.dropna(subset=["Fecha Tren Incidencia"])
        d["mes"] = mes_de_ms(d["Fecha Tren Incidencia"])
        d["nucli"] = nucli
        d["minuts"] = pd.to_numeric(d[f"Retraso a la Llegada__{SUMA}"], errors="coerce")
        d["origen"] = d["Imputabilidad"].map(ORIGENS)
        files.append(d.dropna(subset=["origen"]))
    d = pd.concat(files)
    t = d.pivot_table(index=["mes", "nucli"], columns="origen", values="minuts",
                      aggfunc="sum", fill_value=0).reset_index()
    for col in ORIGENS.values():
        if col not in t.columns:
            t[col] = 0
    t["minuts_retard_total"] = t[list(ORIGENS.values())].sum(axis=1)
    t["quota_renfe"] = t["minuts_retard_renfe"] / t["minuts_retard_total"]
    return t


def viatgers(model):
    """Viatgers de Rodalia de Barcelona per mes: 2025 de la taula consolidada, 2026 de la diària."""
    a = consulta(model, "VIAJEROSConsolidados", ["Nucleo", "AÑO", "MES"], [("VIAJEROS", SUMA)])
    a = a[a["Nucleo"].isin(NUCLIS_VIATGERS) & (pd.to_numeric(a["AÑO"], errors="coerce") == 2025)].copy()
    a["mes"] = "2025-" + pd.to_numeric(a["MES"]).astype(int).astype(str).str.zfill(2)
    a["viatgers"] = pd.to_numeric(a[f"VIAJEROS__{SUMA}"], errors="coerce")

    b = consulta(model, "Viajeros_Día_Cercanías_Ev_Mensual", ["Núcleo", "Fecha Venta"],
                 [("TOTALES ENTRADAS", SUMA)])
    b = b[b["Núcleo"].isin(NUCLIS_VIATGERS)
          & b["Fecha Venta"].astype(str).str.fullmatch(r"\d{8}")].copy()
    b["mes"] = b["Fecha Venta"].str[:4] + "-" + b["Fecha Venta"].str[4:6]
    b["viatgers"] = pd.to_numeric(b[f"TOTALES ENTRADAS__{SUMA}"], errors="coerce")
    b = b.rename(columns={"Núcleo": "Nucleo"})

    v = pd.concat([a[["Nucleo", "mes", "viatgers"]], b[["Nucleo", "mes", "viatgers"]]])
    v["nucli"] = v["Nucleo"].map(NUCLIS_VIATGERS)
    # A la resta de nuclis la taula consolidada de 2025 té mesos sense any informat
    # i els totals no s'han pogut validar: només es conserva Rodalia de Barcelona.
    v = v[v["nucli"] == "Rodalia de Barcelona"]
    v = v.groupby(["mes", "nucli"], as_index=False)["viatgers"].sum()
    v["viatgers"] = v["viatgers"].round().astype("Int64")
    return v


# -------------------------------------------------------------------- main

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    model = get(RESOURCE_KEY + "/modelsAndExploration?preferReadOnlySession=true")["models"][0]["id"]
    r = requests.post(BASE + "conceptualschema", headers=CAPCALERES,
                      json={"modelIds": [model], "userPreferredLocale": "es-ES"}, timeout=120)
    r.raise_for_status()
    entitats = [e["Name"] for e in r.json()["schemas"][0]["schema"]["Entities"]]

    print("Trens i parades")
    t = trens(model).merge(parades(model), on=["mes", "nucli"], how="outer")
    print("Puntualitat al destí final")
    t = t.merge(puntualitat(model, entitats), on=["mes", "nucli"], how="left")
    print("Incidències")
    t = t.merge(incidencies(model), on=["mes", "nucli"], how="left")
    print("Viatgers")
    t = t.merge(viatgers(model), on=["mes", "nucli"], how="left")

    t = t[t["mes"] >= PRIMER_MES].sort_values(["nucli", "mes"])
    t["compliment_servei"] = t["trens_realitzats"] / t["trens_programats"]
    t["compliment_horari"] = t["parades_puntuals"] / (t["parades_puntuals"] + t["parades_impuntuals"])
    t["taxa_suprimides"] = t["parades_suprimides"] / (t["parades_circulades"] + t["parades_suprimides"])
    t["periode"] = t["mes"].map(lambda m: "abans_gelida" if m < MES_GELIDA else "despres_gelida")

    t.to_csv(OUT / "renfe_nucli_mes.csv", index=False)
    print(f"renfe_nucli_mes.csv: {len(t)} files x {t.shape[1]} columnes "
          f"({t.nucli.nunique()} nuclis, {t.mes.min()} - {t.mes.max()})")
    print("L'últim mes pot estar incomplet: comproveu-ho abans de fer-lo servir.")


if __name__ == "__main__":
    main()