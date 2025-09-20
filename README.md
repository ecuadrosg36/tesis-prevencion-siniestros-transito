# tesis-prevencion-siniestros-transito

Pipeline para normalizar siniestros de tránsito (Perú 2008–2023) en una sola tabla.

## Instalación rápida

```bash
python -m venv .venv
# Linux/Mac
#source .venv/bin/activate
# Windows PowerShell
 .\.venv\Scripts\Activate.ps1

pip install -U pip
pip install -r requirements.txt
pip install -e .
```

## Uso

Copia tu Excel a `data/raw/` y ejecuta:

```bash
tpst-normalizar "data/raw/PERU. SINIESTROS DE TRANSITO POR AÑO 2008-2023.xlsx"   -o "data/processed/siniestros_normalizado.csv"   --parquet "data/processed/siniestros_normalizado.parquet"
```

## Verificación del Parquet

Genera las salidas y verifica:

```bash
tpst-normalizar "data/raw/PERU. SINIESTROS DE TRANSITO POR AÑO 2008-2023.xlsx"   -o "data/processed/siniestros_normalizado.csv"   --parquet "data/processed/siniestros_normalizado.parquet"   --verify
```

O con script dedicado:

```bash
python scripts/verify_outputs.py "data/processed/siniestros_normalizado.parquet"
```

## Publicación en GitHub

```bash
# Dentro de la carpeta del proyecto
git init
git add .
git commit -m "feat: initial commit (tesis-prevencion-siniestros-transito)"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/tesis-prevencion-siniestros-transito.git
git push -u origin main
```
