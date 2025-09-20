# scripts/make_single_pivot.py
# -*- coding: utf-8 -*-
import argparse, unicodedata, re, pandas as pd
from pathlib import Path

def _slug(s: str) -> str:
    if s is None: return "total"
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+","_", s).strip("_")
    return s or "total"

def pivot_metric(df: pd.DataFrame, metric: str, fillna0: bool) -> pd.DataFrame:
    d = df[df["metric"] == metric].copy()
    # métricas sin dimensión -> columna 'total'
    if d["dim_name"].isna().all() and d["dim_value"].isna().all():
        d = d.assign(dim_value="total")
    d["dim_value"] = d["dim_value"].apply(_slug)
    wide = d.pivot_table(
        index=["year","region"],
        columns="dim_value",
        values="value",
        aggfunc="sum",
        observed=True
    )
    if fillna0:
        wide = wide.fillna(0)
    wide.columns = [str(c) for c in wide.columns]
    return wide.sort_index(axis=1)

def main():
    ap = argparse.ArgumentParser(description="Generar un único tablón ancho para ML.")
    ap.add_argument("parquet_in", help="Parquet consolidado (tabla larga).")
    ap.add_argument("-o","--outdir", default="data/processed", help="Carpeta de salida.")
    ap.add_argument("--fillna0", action="store_true", help="Rellenar NaN con 0.")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(args.parquet_in)
    df["region"] = df["region"].astype(str)
    df["metric"] = df["metric"].astype(str)

    base = None
    for m in sorted(df["metric"].unique()):
        w = pivot_metric(df, m, fillna0=args.fillna0)
        pref = _slug(m)
        w = w.rename(columns={c: f"{pref}__{c}" for c in w.columns})
        base = w if base is None else base.join(w, how="outer")

    base = base.reset_index()
    if args.fillna0:
        cols = [c for c in base.columns if c not in ("year","region")]
        base[cols] = base[cols].fillna(0)

    out_parquet = outdir / "siniestros_normalizado_pivot.parquet"
    out_csv = outdir / "siniestros_normalizado_pivot.csv"
    base.to_parquet(out_parquet, index=False)
    base.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[OK] {out_parquet} y {out_csv} -> {base.shape[0]} filas, {base.shape[1]} columnas")

if __name__ == "__main__":
    main()
