# ATL08KIT

A Python package and command-line toolkit for turning **ICESat-2 ATL08 HDF5 land segments into filtered, GIS-ready point data**.

Developed by **Yiyi Cen** during Geospatial Programming coursework, the toolkit brings extraction, quality control, beam selection, spatial masking, and export into reusable modules.

## What it does

| Step | Capability |
|---|---|
| Inspect and extract | Discover aligned land-segment fields and export point tables from HDF5 |
| Quality control | Apply column-based expressions through an AST-validated expression language |
| Beam selection | Resolve strong beams from each source file's `sc_orient` metadata |
| Spatial masking | Clip or exclude polygons; filter points by sampled raster values |
| Export | Write GeoJSON, GeoPackage, and Shapefile through GeoPandas |
| Repeat workflows | Process individual tables or batches with summary outputs |

## Install

Python **3.10+** is required. From a fresh clone:

```bash
git clone https://github.com/yiyilv/ATL08KIT.git
cd ATL08KIT
python -m venv .venv
```

Activate the virtual environment using the command for your operating system, then install the package with vector support and test dependencies:

```bash
python -m pip install -e ".[vector,dev]"
atl08kit --help
atl08kit version
```

The core dependencies are NumPy, pandas, h5py, Shapely, and Rasterio. GeoPandas is supplied by the optional `vector` extra and is needed for vector masking/export.

## Quick start

Use an ATL08 HDF5 file obtained from its data provider. The filenames below are examples; supply your own input and boundary files.

```bash
# 1. Extract aligned land_segments fields.
atl08kit extract --h5 /path/to/ATL08_file.h5 --out points_raw.csv --summary

# 2. Apply an explicit quality-control rule.
atl08kit filter --in points_raw.csv --out points_qc.csv \
  --expr "abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3" \
  --summary

# 3. Keep strong beams using the original source HDF5 metadata.
atl08kit beams --in points_qc.csv --out points_strong.csv \
  --h5-folder /path/to/ATL08_files --summary

# 4. Clip to a polygon area of interest.
atl08kit vector --in points_strong.csv --out points_aoi.csv \
  --mask /path/to/boundary.geojson --mode clip --summary

# 5. Export the result to a GIS format.
atl08kit export --in points_aoi.csv --out points_aoi.gpkg --summary
```

Extraction retains `lon`, `lat`, `beam`, and `source_file` for downstream processing and source traceability. Nested field names are flattened, for example `terrain/h_te_best_fit` becomes `terrain_h_te_best_fit`.

The numerical thresholds above are example analysis choices, not universal ATL08 quality recommendations. Check field availability and choose rules appropriate to your data version and scientific task.

## Python API

```python
import pandas as pd
from atl08kit.filters import filter_by_expr

points = pd.read_csv("points_raw.csv")
filtered, summary = filter_by_expr(
    points,
    "abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3",
)
print(summary)
filtered.to_csv("points_qc.csv", index=False)
```

## Batch processing and command reference

```bash
atl08kit batch --in-dir points_raw --out-dir points_qc \
  --expr "cloud_flag_atm < 3" --summary batch_summary.csv
atl08kit extract --help
atl08kit vector --help
```

See the [detailed command and module reference](docs/CLI_REFERENCE.md) for raster masking, monthly polygon masks, pipeline options, and the test-suite structure. Each subcommand also exposes `--help`.

## Engineering and contribution

My work in this repository covers the reusable Python package, expression-based filtering, beam handling, spatial-processing modules, CLI/pipeline orchestration, and automated tests. The package separates I/O, filtering logic, spatial operations, and command-line entry points so the same operations can be composed in scripts and notebooks.

```text
src/atl08kit/
  atl08.py         HDF5 field discovery and extraction
  expr.py          expression parsing and validation
  filters.py       quality filtering and summaries
  beams.py         satellite orientation and beam selection
  vector_mask.py   polygon masks and monthly AOIs
  raster.py        raster sampling and masks
  pipeline.py      single-table processing
  batch.py         repeated processing and summaries
  export.py        GIS export
  cli.py           command-line entry point
tests/             unit, CLI, and integration tests
```

## Tests

```bash
python -m pytest
```

The existing suite covers extraction, expressions, beam logic, table I/O, spatial masks, exports, and CLI workflows using synthetic fixtures. No large satellite download is required for those fixtures.

## Licence and data

Code is distributed under the [MIT licence](LICENSE). Satellite inputs and user-supplied boundaries or raster masks retain their providers' terms. Download those inputs separately and preserve their citations and provenance.

