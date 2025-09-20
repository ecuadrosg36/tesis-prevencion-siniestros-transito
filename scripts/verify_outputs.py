
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Verificar parquet consolidado")
    parser.add_argument("parquet_path", help="Ruta al archivo Parquet a verificar")
    args = parser.parse_args()
    df = pd.read_parquet(args.parquet_path)
    print("Filas:", len(df))
    print("Columnas:", df.columns.tolist())
    print("Schema:", df.dtypes.to_dict())
    print("\nMétricas (top 10):")
    print(df["metric"].value_counts().head(10))
    print("\nAños:", df["year"].min(), "..", df["year"].max())
    print("\nMuestra:")
    print(df.sample(10, random_state=1))

if __name__ == "__main__":
    main()
