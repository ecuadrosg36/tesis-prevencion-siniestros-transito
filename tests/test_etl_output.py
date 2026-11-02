from pathlib import Path

import pandas as pd

from tesis_prevencion_siniestros_transito.normalize import normalize_workbook

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "PERU. SINIESTROS DE TRANSITO POR AÑO 2008-2023.xlsx"
PROCESSED = ROOT / "data" / "processed" / "siniestros_normalizado.parquet"


def test_etl_matches_processed_data():
    """Running the ETL on the raw Excel must give the same table we publish."""
    new_df, _ = normalize_workbook(str(RAW))
    expected = pd.read_parquet(PROCESSED)

    cols = list(expected.columns)
    new_df = new_df[cols].sort_values(cols).reset_index(drop=True)
    expected = expected.sort_values(cols).reset_index(drop=True)

    assert len(new_df) == len(expected)
    pd.testing.assert_frame_equal(new_df, expected, check_dtype=False)
