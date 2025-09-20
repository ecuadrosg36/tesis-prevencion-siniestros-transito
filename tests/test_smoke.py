
from tesis_prevencion_siniestros_transito.normalize import _to_int_year, _clean_region

def test_year_parse():
    assert _to_int_year("2008") == 2008
    assert _to_int_year(2015.0) == 2015
    assert _to_int_year("abcd") is None

def test_clean_region():
    assert _clean_region(" Lima ") == "LIMA"
    assert _clean_region(None) is None
