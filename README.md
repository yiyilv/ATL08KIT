# atl08kit — A Python Toolkit for ICESat-2 ATL08 Point Data

`atl08kit` is a lightweight Python library for geospatial analysis and
quality control of ICESat-2 ATL08 point data.

This project was developed as part of the **Geospatial Programming** course
and focuses on building a **well-structured, testable, and reusable Python library**
rather than a monolithic application or a collection of scripts.

The toolkit supports:

- Flexible quality control of ATL08 point tables using a safe, expression-based DSL
- Strong-beam selection based on satellite orientation (`sc_orient`)
- An end-to-end processing pipeline accessible via both a Python API and a CLI
- Reproducible geospatial data processing with comprehensive automated tests

---



## Motivation

atl08kit is motivated by the way ICESat-2 ATL08 data are commonly used in real geospatial research workflows.

ATL08 is a land and vegetation height product derived from spaceborne LiDAR observations and is widely used for terrain analysis, vegetation studies, and multi-source elevation comparison.
In practice, ATL08 data are almost always processed as point tables and require strict and repeatable quality control.

Typical workflows repeatedly involve:
    •    Quality filtering based on elevation differences, terrain flags, and cloud indicators
    •    Strong- and weak-beam selection using satellite orientation information (sc_orient)
    •    Spatial clipping to areas of interest or masking with raster datasets
    •    Iterative adjustment of filtering rules across experiments

However, these operations are often implemented as ad-hoc scripts with limited reusability and poor testability.

For this reason, atl08kit does not aim to implement a full ICESat-2 processing chain.
Instead, it focuses on the most common and error-prone steps in ATL08 point data analysis and abstracts them into a modular, composable, and testable Python library.
    
---

## Project Scope

The goal of this project is to design and implement a **Python geospatial library**
that demonstrates good software engineering practices applied to real Earth
observation data.

The library focuses on **point-based ICESat-2 ATL08 data** represented as tabular
datasets (CSV format) and provides reusable components for filtering and
quality control.

The project intentionally avoids implementing a full ICESat-2 processing chain.
Instead, it emphasizes:

- Modular design
- Extensibility
- Clear and stable interfaces
- Correctness validated through automated tests

---

## Installation

We recommend using a dedicated conda environment:

```bash
conda create -n atl08kit python=3.10 -y
conda activate atl08kit
```
Install the package in editable mode:
```bash
pip install -e .
```

Verify installation:
```bash
atl08kit version
```



---

## Quick Start (Command Line Interface)
0. Extract point data from ATL08 HDF5 files

## Extracting Point Tables from ATL08 HDF5

ATL08 data are originally distributed as HDF5 files.  
`atl08kit` provides a dedicated CLI command to **extract land_segments point data**
from ATL08 H5 files into a tabular CSV format that can be processed by all other
modules in the toolkit.

### Extract all aligned land_segments fields

```bash
atl08kit extract \
  --h5 ATL08_20220102113835_01711406_007_01.h5 \
  --out points.csv \
  --summary
```
This command:
• Reads ATL08 land_segments from the specified HDF5 file
• Automatically extracts all 1D datasets aligned with latitude/longitude
• Skips non-aligned or multi-dimensional datasets (e.g. canopy metrics)
• Outputs a CSV file compatible with all downstream atl08kit commands

The output table always includes:
• lon, lat — point coordinates
• beam — beam identifier (gt1l, gt2r, etc.)
• source_file — ATL08 file stem for traceability

1. Filter points using a boolean expression

```bash
atl08kit filter \
  --in input.csv \
  --out filtered.csv \
  --expr "abs(dem_h - h_te_best_fit) <= 3 and terrain_flg == 0 and cloud_flag_atm < 3" \
  --summary
```

This command:

- Reads ATL08 land_segments from the specified HDF5 file
- Automatically extracts all 1D datasets aligned with latitude/longitude
- Skips non-aligned or multi-dimensional datasets (e.g. canopy metrics)
- Outputs a CSV file compatible with all downstream atl08kit commands

---

2. Select strong-beam points

```bash
atl08kit beams \
  --in points.csv \
  --out points_strong.csv \
  --h5-folder /path/to/ATL08_h5_files \
  --summary
```

This command:
	•	Reads ATL08 HDF5 files from the provided folder
	•	Determines strong beams based on /orbit_info/sc_orient
	•	Keeps only rows corresponding to strong beams

---

3. Run the full processing pipeline

```bash
atl08kit run \
  --in points.csv \
  --out result.csv \
  --h5-folder /path/to/ATL08_h5_files \
  --expr "abs(dem_h - h_te_best_fit) <= 3 and cloud_flag_atm < 3" \
  --summary
```
The pipeline combines:
	•	Optional strong-beam selection
	•	Optional expression-based filtering
	•	A single consolidated output

---

## Exporting Point Tables to Vector Formats

Filtered point tables can be exported to common geospatial vector formats
using the `export` command.

Supported output formats:

- GeoJSON (`.geojson`)
- GeoPackage (`.gpkg`)
- ESRI Shapefile (`.shp`)

Example:

```bash
atl08kit export \
  --in filtered.csv \
  --out filtered.geojson \
  --lon lon \
  --lat lat \
  --crs EPSG:4326 \
  --summary
```
This command:
	•	Converts the input CSV into a GeoDataFrame
	•	Writes the output vector file using geopandas
	•	Preserves all attribute columns


## Python API Example

The same functionality is also accessible programmatically:

```python
import pandas as pd
from atl08kit.filters import filter_by_expr

df = pd.read_csv("input.csv")

out, summary = filter_by_expr(
    df,
    "abs(dem_h - h_te_best_fit) <= 3 and cloud_flag_atm < 3"
)

print(summary)
out.to_csv("filtered.csv", index=False)
```

---

## Input Data Format

General Requirements
	•	Input data are provided as CSV point tables
	•	Column names are user-defined and referenced directly in expressions
	•	Coordinates are typically stored as lon / lat (EPSG:4326) or projected coordinates

Filtering (filter command)

The filtering expression may use:
	•	Arithmetic operators: + - * / **
	•	Comparison operators: < <= > >= == !=
	•	Boolean operators: and, or, not
	•	Built-in function: abs(x)

All referenced columns must exist in the input table.

Strong-Beam Selection (beams command)

The input CSV must contain:
	•	beam: beam identifier (e.g. gt1l, gt2r)
	•	source_file: source ATL08 filename (used to match HDF5 metadata)

---

## Testing

Automated tests are implemented using pytest.

Run the full test suite:
```bash
pytest
```
The tests include:
	•	Unit tests for expression parsing and filtering
	•	Unit tests for strong-beam logic
	•	CLI tests executed via subprocess
	•	Pipeline and batch integration tests

Synthetic test data are generated inside the test suite to ensure
reproducibility and independence from large external datasets.

---

## Project Structure
```bash
src/atl08kit/
  expr.py        # safe expression parsing and validation
  filters.py     # expression-based filtering logic
  beams.py       # strong-beam detection using sc_orient
  raster.py      # raster-based masking utilities
  vector_mask.py # vector-based masking utilities
  pipeline.py    # end-to-end processing pipeline
  cli.py         # command-line interface
  atl08.py       # HDF5 (ATL08) land_segments extraction utilities

tests/
  test_filters.py
  test_beams.py
  test_cli.py
  test_pipeline_cli.py
  ...
```

---

## Notes

This project was developed by a group of up to three students as required by the course.
Version control was managed using Git, and the project emphasizes clarity, modularity,
and testability over feature completeness.
