
# -*- coding: utf-8 -*-
import argparse
import sys
from typing import Optional, List, Tuple, Dict
import pandas as pd

YEARS_VALID = set(range(1990, 2101))

def _clean_region(s):
    if pd.isna(s):
        return None
    return str(s).strip().upper()

def _to_int_year(y):
    if pd.isna(y):
        return None
    try:
        yi = int(float(y))
        return yi if yi in YEARS_VALID else None
    except Exception:
        return None

def _safe_parquet(df: pd.DataFrame, path: str) -> bool:
    try:
        df.to_parquet(path, index=False)
        return True
    except Exception as e:
        print(f"[WARN] No se pudo escribir Parquet ({e}). Continúo solo con CSV.", file=sys.stderr)
        return False

def parse_region_year_simple(path, sheet, header_row=2, region_col=0, metric_name="value", metric_label="siniestros_total"):
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header = raw.iloc[header_row].copy()
    header.iloc[region_col] = "region"
    df = raw.iloc[header_row + 1 :].copy()
    df.columns = header
    df = df[df["region"].notna()]
    value_cols = [c for c in df.columns if c != "region" and _to_int_year(c) is not None]
    df_long = df.melt(id_vars=["region"], value_vars=value_cols, var_name="year", value_name="value")
    df_long["year"] = df_long["year"].apply(_to_int_year)
    df_long["region"] = df_long["region"].map(_clean_region)
    df_long = df_long.dropna(subset=["region", "year", "value"])
    df_long.insert(2, "metric", metric_label)
    df_long["dim_name"] = None
    df_long["dim_value"] = None
    return df_long[["year", "region", "metric", "dim_name", "dim_value", "value"]]

def parse_year_category_by_region(path, sheet, year_row=1, category_row=2, start_row=3, region_col=0, dim_name="categoria", metric_label="conteo"):
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    years = raw.iloc[year_row].copy().ffill(axis=0)
    cats = raw.iloc[category_row].copy()
    data = raw.iloc[start_row:].copy()
    data = data[data.iloc[:, region_col].notna()]
    region_series = data.iloc[:, region_col].map(_clean_region)
    value_block = data.iloc[:, region_col + 1 :].copy()
    tuples = []
    for j in range(region_col + 1, region_col + 1 + value_block.shape[1]):
        y = _to_int_year(years.iloc[j])
        c = cats.iloc[j]
        c = str(c).strip() if pd.notna(c) else None
        tuples.append((y, c))
    columns = pd.MultiIndex.from_tuples(tuples, names=["year", dim_name])
    value_block.columns = columns
    stacked = value_block.stack(level=[0, 1]).to_frame(name="value").reset_index()
    stacked = stacked.rename(columns={"level_0": "orig_idx"})
    stacked["region"] = stacked["orig_idx"].map(region_series)
    stacked = stacked.dropna(subset=["value", "year", dim_name, "region"])
    stacked["year"] = stacked["year"].astype(int)
    stacked[dim_name] = stacked[dim_name].astype(str).str.strip()
    out = stacked[["year", "region", dim_name, "value"]].copy()
    out.insert(2, "metric", metric_label)
    out["dim_name"] = dim_name
    out["dim_value"] = out[dim_name]
    out = out.drop(columns=[dim_name])
    return out[["year", "region", "metric", "dim_name", "dim_value", "value"]]

def parse_two_row_header_no_region(path, sheet, year_row=1, category_row=2, start_row=3, metric_label="conteo", dim_name="categoria", region_default="PERÚ"):
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    years = raw.iloc[year_row].copy().ffill(axis=0)
    cats = raw.iloc[category_row].copy()
    data = raw.iloc[start_row:].copy()
    value_block = data.copy()
    tuples = []
    for j in value_block.columns:
        y = _to_int_year(years.iloc[j]) if j < len(years) else None
        c = cats.iloc[j] if j < len(cats) else None
        c = str(c).strip() if pd.notna(c) else None
        tuples.append((y, c))
    value_block.columns = pd.MultiIndex.from_tuples(tuples, names=["year", dim_name])
    stacked = value_block.stack(level=[0, 1]).to_frame(name="value").reset_index()
    stacked = stacked.dropna(subset=["value", "year", dim_name])
    stacked["year"] = stacked["year"].astype(int)
    stacked[dim_name] = stacked[dim_name].astype(str).str.strip()
    out = stacked[["year", dim_name, "value"]].copy()
    out.insert(1, "region", region_default)
    out.insert(2, "metric", metric_label)
    out["dim_name"] = dim_name
    out["dim_value"] = out[dim_name]
    out = out.drop(columns=[dim_name])
    return out[["year", "region", "metric", "dim_name", "dim_value", "value"]]

def normalize_workbook(path: str):
    xls = pd.ExcelFile(path)
    sheets = xls.sheet_names
    logs = {}
    normalized_parts = []
    # Handlers explícitos + genéricos
    handlers = {
        "SINIESTROS AÑO REGIÓN": lambda: parse_region_year_simple(
            path, "SINIESTROS AÑO REGIÓN",
            header_row=2, region_col=0,
            metric_name="value", metric_label="siniestros_total"
        ),
        "SINIESTROS POR TIPO": lambda: parse_year_category_by_region(
            path, "SINIESTROS POR TIPO",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="tipo_accidente", metric_label="siniestros_por_tipo"
        ),
        "CAUSAS POR REGIÓN": lambda: parse_year_category_by_region(
            path, "CAUSAS POR REGIÓN",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="causa", metric_label="siniestros_por_causa"
        ),
        # Extras (intento con el genérico por región: año + categoría)
        "CONDUCTORES INVOLUCRADOS": lambda: parse_year_category_by_region(
            path, "CONDUCTORES INVOLUCRADOS",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="condicion_conductor", metric_label="conductores_involucrados"
        ),
        "VEHICULOS INVOLUCRADOS": lambda: parse_year_category_by_region(
            path, "VEHICULOS INVOLUCRADOS",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="tipo_vehiculo", metric_label="vehiculos_involucrados"
        ),
        "VEHICULOS POR TIPO Y REGIÓN": lambda: parse_year_category_by_region(
            path, "VEHICULOS POR TIPO Y REGIÓN",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="tipo_vehiculo", metric_label="vehiculos_por_tipo_region"
        ),
        "FRANJA HORARIA": lambda: parse_year_category_by_region(
            path, "FRANJA HORARIA",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="franja_horaria", metric_label="siniestros_por_franja_horaria"
        ),
        "DÍA": lambda: parse_year_category_by_region(
            path, "DÍA",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="dia_semana", metric_label="siniestros_por_dia"
        ),
        "SINIESTROS RURALES POR TIPO": lambda: parse_year_category_by_region(
            path, "SINIESTROS RURALES POR TIPO",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="tipo_accidente_rural", metric_label="siniestros_rurales_por_tipo"
        ),
        "SINIES. RURAL HERIDO FALLECIDO": lambda: parse_year_category_by_region(
            path, "SINIES. RURAL HERIDO FALLECIDO",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="condicion_victima", metric_label="siniestros_rurales_victimas"
        ),
        # FALLECIDOS/HERIDOS suelen tener cabeceras dobles complejas; probamos genérico por región
        "FALLECIDOS": lambda: parse_year_category_by_region(
            path, "FALLECIDOS",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="grupo_edad_o_categoria", metric_label="fallecidos"
        ),
        "HERIDOS": lambda: parse_year_category_by_region(
            path, "HERIDOS",
            year_row=1, category_row=2, start_row=3, region_col=0,
            dim_name="grupo_edad_o_categoria", metric_label="heridos"
        ),
    }
    for sh in sheets:
        try:
            if sh in handlers:
                df = handlers[sh]()
                normalized_parts.append(df)
                logs[sh] = f"OK: {len(df)} filas"
            else:
                # Intento genérico
                try:
                    df_try = parse_year_category_by_region(
                        path, sh,
                        year_row=1, category_row=2, start_row=3, region_col=0,
                        dim_name="categoria", metric_label=f"{sh.lower().replace(' ', '_')}"
                    )
                    normalized_parts.append(df_try)
                    logs[sh] = f"OK (genérico por región): {len(df_try)} filas"
                except Exception as e1:
                    try:
                        df_try2 = parse_two_row_header_no_region(
                            path, sh,
                            year_row=1, category_row=2, start_row=3,
                            dim_name="categoria", metric_label=f"{sh.lower().replace(' ', '_')}"
                        )
                        normalized_parts.append(df_try2)
                        logs[sh] = f"OK (genérico nacional): {len(df_try2)} filas"
                    except Exception as e2:
                        logs[sh] = f"SKIP: no se pudo normalizar automáticamente ({e1} / {e2})"
        except Exception as e:
            logs[sh] = f"ERROR: {e}"
    if not normalized_parts:
        raise RuntimeError("No se pudo normalizar ninguna hoja. Revisa parámetros.")
    final_df = pd.concat(normalized_parts, ignore_index=True)
    final_df["region"] = final_df["region"].map(_clean_region)
    final_df = final_df.dropna(subset=["year", "region", "value"])
    final_df["year"] = final_df["year"].astype(int)
    final_df = final_df[["year", "region", "metric", "dim_name", "dim_value", "value"]]
    return final_df, logs

def main():
    parser = argparse.ArgumentParser(description="Normalizar libro de siniestros en una sola tabla (formato largo).")
    parser.add_argument("excel_path", help="Ruta al archivo Excel de entrada")
    parser.add_argument("-o", "--output_csv", default="data/processed/siniestros_normalizado.csv", help="Ruta de salida CSV")
    parser.add_argument("--parquet", default="data/processed/siniestros_normalizado.parquet", help="Ruta de salida Parquet (opcional)")
    parser.add_argument("--verify", action="store_true", help="Leer el Parquet generado y mostrar resumen para comprobar.")
    args = parser.parse_args()
    final_df, logs = normalize_workbook(args.excel_path)
    # Guardar CSV
    final_df.to_csv(args.output_csv, index=False, encoding="utf-8")
    print(f"[OK] CSV escrito: {args.output_csv} ({len(final_df)} filas)")
    # Guardar Parquet (si es posible)
    wrote_parquet = False
    if args.parquet:
        wrote_parquet = _safe_parquet(final_df, args.parquet)
        if wrote_parquet:
            print(f"[OK] Parquet escrito: {args.parquet}")
    print("\n=== LOGS POR HOJA ===")
    for sh, msg in logs.items():
        print(f"- {sh}: {msg}")
    print("\n=== Resumen rápido ===")
    print(f"Regiones: {final_df['region'].nunique()}")
    print(f"Años: {final_df['year'].min()}..{final_df['year'].max()}")
    print("Métricas:", final_df["metric"].value_counts().to_dict())
    if args.verify and wrote_parquet:
        print("\n=== VERIFICACIÓN PARQUET ===")
        try:
            dfp = pd.read_parquet(args.parquet)
            print("Filas (parquet):", len(dfp))
            print("Schema:", dfp.dtypes.to_dict())
            print("Top métricas:", dfp["metric"].value_counts().head(10).to_dict())
        except Exception as e:
            print("[WARN] No se pudo leer el Parquet para verificación:", e)

if __name__ == "__main__":
    main()
