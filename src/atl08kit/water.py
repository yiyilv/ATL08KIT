from __future__ import annotations

import re
from pathlib import Path

# Match: ATL08_YYYYMMDDxxxxxx_...
# We only need YYYYMM for monthly mask selection.
_ATL08_YYYYMM_RE = re.compile(r"ATL08_(\d{4})(\d{2})\d{2}")

def extract_yyyymm_from_atl08_name(name: str) -> str:
    """
    Extract YYYYMM from an ATL08 filename (or stem).

    Examples
    --------
    >>> extract_yyyymm_from_atl08_name("ATL08_20220102113835_01711406_007_01.h5")
    '202201'
    >>> extract_yyyymm_from_atl08_name("ATL08_20220102113835_01711406_007_01")
    '202201'

    """
    stem = Path(name).stem  # handles both with/without suffix
    m = _ATL08_YYYYMM_RE.search(stem)
    if not m:
        raise ValueError(
            f"Cannot infer YYYYMM from ATL08 name: {name}. "
            "Expected pattern like 'ATL08_YYYYMMDD...'."
        )
    yyyy, mm = m.group(1), m.group(2)
    return f"{yyyy}{mm}"