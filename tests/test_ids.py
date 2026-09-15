"""Tests for gateway ID normalisation."""

from gateway_priority.ids import normalize_gateway_id


def test_colon_format():
    assert normalize_gateway_id("06:39:EA:56:02:C1") == "0639EA5602C1"


def test_bare_format():
    assert normalize_gateway_id("0639EA5602C1") == "0639EA5602C1"


def test_lowercase():
    assert normalize_gateway_id("0639ea5602c1") == "0639EA5602C1"
    assert normalize_gateway_id("06:39:ea:56:02:c1") == "0639EA5602C1"


def test_whitespace():
    assert normalize_gateway_id("  0639EA5602C1  ") == "0639EA5602C1"
    assert normalize_gateway_id("  06:39:EA:56:02:C1\n") == "0639EA5602C1"


def test_invalid_length():
    assert normalize_gateway_id("0639EA5602C") is None
    assert normalize_gateway_id("0639EA5602C12") is None


def test_invalid_hex():
    assert normalize_gateway_id("0639EA5602G1") is None
    assert normalize_gateway_id("ZZZZZZZZZZZZ") is None


def test_null():
    assert normalize_gateway_id(None) is None


def test_empty_string():
    assert normalize_gateway_id("") is None
    assert normalize_gateway_id("   ") is None


def test_canonicalize_gateway_id_series_success():
    import pandas as pd
    from gateway_priority.ids import canonicalize_gateway_id_series

    s = pd.Series(["06:39:EA:56:02:C1", "0639ea5602c1", None, "  "])
    res = canonicalize_gateway_id_series(s, "test_col")
    assert res.iloc[0] == "0639EA5602C1"
    assert res.iloc[1] == "0639EA5602C1"
    assert res.iloc[2] is None
    assert res.iloc[3] is None


def test_canonicalize_gateway_id_series_malformed_raises():
    import pytest
    import pandas as pd
    from gateway_priority.ids import canonicalize_gateway_id_series

    s = pd.Series(["0639EA5602C1", "INVALID_ID_123"])
    with pytest.raises(ValueError, match="Malformed gateway ID at index 1"):
        canonicalize_gateway_id_series(s, "gateway_id")
