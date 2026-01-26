import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import h5py


def _write_minimal_atl08_h5(path: Path):
    """
    Create a minimal ATL08-like H5 file for CLI testing.

    Structure:
      /gt2l/land_segments/
        latitude                (1D, aligned)
        longitude               (1D, aligned)
        dem_h                   (1D, aligned)        -> should be extracted
        canopy/canopy_h_metrics (2D, NOT aligned)    -> should be skipped
    """
    with h5py.File(path, "w") as f:
        grp = f.create_group("gt2l/land_segments")

        grp.create_dataset("latitude", data=[10.0, 10.1, 10.2])
        grp.create_dataset("longitude", data=[100.0, 100.1, 100.2])
        grp.create_dataset("dem_h", data=[50.0, 51.0, 52.0])

        canopy = grp.create_group("canopy")
        canopy.create_dataset(
            "canopy_h_metrics",
            data=[[1, 2], [3, 4], [5, 6]],  # 2D -> must be skipped
        )


def test_cli_extract_minimal_h5(tmp_path: Path):
    h5_path = tmp_path / "test.h5"
    out_csv = tmp_path / "out.csv"

    _write_minimal_atl08_h5(h5_path)

    cmd = [
        sys.executable,
        "-m",
        "atl08kit.cli",
        "extract",
        "--h5",
        str(h5_path),
        "--out",
        str(out_csv),
        "--summary",
    ]

    res = subprocess.run(
        cmd,
        cwd=str(tmp_path),
        text=True,
        capture_output=True,
    )

    # ---- CLI execution ----
    assert res.returncode == 0, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

    # ---- output CSV exists ----
    assert out_csv.exists()
    assert out_csv.stat().st_size > 0

    # ---- CSV content sanity ----
    df = pd.read_csv(out_csv)

    # required base columns
    for col in ["lon", "lat", "beam", "dem_h", "source_file"]:
        assert col in df.columns

    # dem_h extracted
    assert len(df) == 3
    assert df["dem_h"].tolist() == [50.0, 51.0, 52.0]

    # ---- summary output ----
    # should mention skipped fields (2D canopy dataset)
    assert "fields_skipped" in res.stdout