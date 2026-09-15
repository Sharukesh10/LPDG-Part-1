"""Gateway ID normalisation and validation utilities."""

from __future__ import annotations

import re
from typing import Any
import pandas as pd

_HEX_12_PATTERN = re.compile(r"^[0-9A-Fa-f]{12}$")

def normalize_gateway_id(val: Any) -> str | None:
    """Normalises gateway identifier into a canonical 12-character uppercase hex string.
    
    Rules:
    - Accepts bare 12-char hex (e.g. '0639EA5602C1') or colon-separated MAC format (e.g. '06:39:EA:56:02:C1')
    - Trims leading/trailing whitespace
    - Removes colon separators
    - Converts to uppercase
    - Validates resulting string is exactly 12 hexadecimal characters
    - Returns None for null, empty, or malformed inputs
    """
    if val is None:
        return None
    
    text = str(val).strip()
    if not text or text.lower() == "nan" or text.lower() == "none":
        return None
    
    # Remove colon separators
    cleaned = text.replace(":", "")
    
    # Check if exactly 12 hex characters
    if _HEX_12_PATTERN.match(cleaned):
        return cleaned.upper()
    
    return None


def canonicalize_gateway_id_series(series: Any, column_name: str = "gateway_id") -> pd.Series:
    """Canonicalises a Series/column of gateway IDs while preserving nulls.

    - Preserves original raw values by returning a new Series.
    - Fails clearly with a ValueError specifying row index, column name, and value if a non-null ID is malformed.
    """
    if not isinstance(series, pd.Series):
        series = pd.Series(series)

    canonical_values = []
    for idx, val in series.items():
        if pd.isna(val) or val is None:
            canonical_values.append(None)
            continue
        
        text = str(val).strip()
        if not text or text.lower() == "nan" or text.lower() == "none":
            canonical_values.append(None)
            continue

        norm = normalize_gateway_id(val)
        if norm is None:
            raise ValueError(
                f"Malformed gateway ID at index {idx} in column '{column_name}': {repr(val)}"
            )
        canonical_values.append(norm)

    return pd.Series(canonical_values, index=series.index, dtype="object")
