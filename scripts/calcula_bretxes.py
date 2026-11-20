#!/usr/bin/env python3
"""
Calcula la bretxa entre la mesura oficial (Renfe) i la ciutadana (Puntual.cat)
per a Rodalia de Barcelona, mes a mes.

Cal haver executat abans descarrega_puntualcat.py i descarrega_renfe.py.

Ús (des de l'arrel del repositori):
    python scripts/calcula_bretxes.py

Sortida:
    puntualcat/bretxes_mes.csv   una fila per mes

    bretxa_parada = compliment_horari (oficial, fins a 3 minuts per parada)
                    - puntualitat_5 (ciutadana, fins a 5 minuts per parada)
    bretxa_desti  = puntualitat_oficial_5 (oficial, fins a 5 minuts al destí final)
                    - puntualitat_final_5 (ciutadana, fins a 5 minuts a l'última parada)

Les mesures ciutadanes són la mitjana de les línies de Rodalies de Barcelona, ponderada
pel nombre de parades (per parada) o de trajectes (al destí final) de cada línia.
Totes les proporcions van de 0 a 1; les bretxes són diferències de proporcions.
"""
from pathlib import Path

import pandas as pd

OUT = Path("puntualcat")
NUCLI = "Rodalia de Barcelona"
SERVEI = "Rodalies de Barcelona"


def mitjana_ponderada(df, valor, pes):
    d = df.dropna(subset=[valor])
    total = d[pes].sum()
    return (d[valor] * d[pes]).sum() / total if total else float("nan")


def main():
    lin = pd.read_csv(OUT / "linies_mes.csv")
    ren = pd.read_csv(OUT / "renfe_nucli_mes.csv")

    # Files agregades de cada línia (tots dos sentits i tots els tipus de dia)
    lin = lin[(lin["servei"] == SERVEI) & (lin["sentit"] == "ANY") & (lin["tipus_dia"] == "ANY")].copy()
    lin["n_parades"] = lin.filter(regex=r"^parades_").sum(axis=1)
    lin["n_trajectes"] = lin.filter(regex=r"^trajectes_").sum(axis=1)

    ciutada = pd.DataFrame({
        "puntualitat_5": lin.groupby("mes").apply(
            lambda g: mitjana_ponderada(g, "puntualitat_5", "n_parades"), include_groups=False),
        "puntualitat_final_5": lin.groupby("mes").apply(
            lambda g: mitjana_ponderada(g, "puntualitat_final_5", "n_trajectes"), include_groups=False),
        "linies": lin.groupby("mes")["linia_id"].nunique(),
    }).reset_index()

    oficial = ren.loc[ren["nucli"] == NUCLI,
                      ["mes", "compliment_horari", "puntualitat_oficial_5", "taxa_suprimides", "periode"]]

    t = oficial.merge(ciutada, on="mes", how="inner").dropna(subset=["puntualitat_oficial_5"])
    t["bretxa_parada"] = t["compliment_horari"] - t["puntualitat_5"]
    t["bretxa_desti"] = t["puntualitat_oficial_5"] - t["puntualitat_final_5"]
    t = t[["mes", "periode", "linies", "compliment_horari", "puntualitat_5", "bretxa_parada",
           "puntualitat_oficial_5", "puntualitat_final_5", "bretxa_desti", "taxa_suprimides"]]
    t.to_csv(OUT / "bretxes_mes.csv", index=False)

    print(f"bretxes_mes.csv: {len(t)} files x {t.shape[1]} columnes ({t.mes.min()} - {t.mes.max()})")
    m = t[["compliment_horari", "puntualitat_5", "bretxa_parada",
           "puntualitat_oficial_5", "puntualitat_final_5", "bretxa_desti"]].mean() * 100
    print(m.round(1).to_string())


if __name__ == "__main__":
    main()