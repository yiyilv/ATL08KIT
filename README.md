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

atl08kit is motivated by the way **ICESat-2 ATL08 data** are commonly used in real geospatial research workflows.

ATL08 is a land and vegetation height product derived from spaceborne LiDAR observations and is widely used for terrain analysis, vegetation studies, and multi-source elevation comparison.
In practice, ATL08 data are almost always processed as point tables and require strict and repeatable quality control.

Typical workflows repeatedly involve:
- Quality filtering based on elevation differences, terrain flags, and cloud indicators
- Strong- and weak-beam selection using satellite orientation information (sc_orient)
- Spatial clipping to areas of interest or masking with raster datasets
- Iterative adjustment of filtering rules across experiments

However, these operations are often implemented as ad-hoc scripts with limited reusability and poor testability.

For this reason, atl08kit does not aim to implement a full ICESat-2 processing chain.
Instead, it focuses on the **most common and error-prone steps** in ATL08 point data analysis and abstracts them into a modular, composable, and testable Python library.
    

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

This section demonstrates a typical end-to-end workflow using `atl08kit`,
starting from raw ATL08 HDF5 files and producing analysis-ready geospatial outputs.

### Step 1 — Extract point tables from ATL08 HDF5

ATL08 data are distributed as HDF5 files.
The `extract` command converts ATL08 `land_segments` into a flat CSV point table
that can be processed by all other modules in `atl08kit`.

```bash
atl08kit extract \
  --h5 ATL08_20220102113835_01711406_007_01.h5 \
  --out points_raw.csv \
  --summary
```

This command:
- Reads ATL08 land_segments from the input HDF5 file
- Extracts all 1D datasets aligned with latitude and longitude
- Skips non-aligned or multi-dimensional datasets
- Produces a CSV file compatible with downstream processing steps

The output table always includes:
- lon, lat - point coordinates
- beam — beam identifier (e.g. gt1l, gt2r)
- source_file — ATL08 file stem for traceability

### Step 2 — Quality filtering using expressions

Points can be filtered using a safe, expression-based DSL.

```bash
atl08kit filter \
  --in points_raw.csv \
  --out points_qc.csv \
  --expr "abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3" \
  --summary
```

This command:
- Evaluates the expression on each row of the point table
- Keeps only points that satisfy the specified conditions
- Writes the filtered table to a new CSV file



### Step3 - Select strong-beam points

```bash
atl08kit beams \
  --in points.csv \
  --out points_strong.csv \
  --h5-folder /path/to/ATL08_h5_files \
  --summary
```

This command:
- Reads ATL08 HDF5 files from the provided folder
- Determines strong beams based on /orbit_info/sc_orient
- Keeps only rows corresponding to strong beams



### Step 4 — Spatial filtering using a vector mask (AOI)

Filtered points can be clipped to an area of interest using a vector polygon.

```bash
atl08kit vector \
  --in points_qc.csv \
  --out points_aoi.csv \
  --mask boundary/2022.shp \
  --mode clip \
  --summary
```

This command:
- Applies a spatial clip using the provided polygon mask
- Keeps only points inside the area of interest

### Step 5 — Export to geospatial vector formats

Point tables can be exported to common GIS formats.

```bash
atl08kit export \
  --in points_aoi.csv \
  --out points_aoi.geojson \
  --summary
```
Supported output formats:
- GeoJSON (.geojson)
- GeoPackage (.gpkg)
- ESRI Shapefile (.shp)

All attribute columns are preserved in the output.

### (Optional) Run a combined processing pipeline

For convenience, the same steps can be combined using the run command.
```bash
atl08kit run \
  --in points_raw.csv \
  --out points_result.csv \
  --h5-folder /path/to/ATL08_h5_files \
  --expr "abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3" \
  --summary
```
  
The pipeline applies:
- Optional strong-beam selection
- Optional expression-based filtering
- A single consolidated output



---
## Core Concepts

atl08kit is designed around a small number of explicit concepts:

- **Point Table**  
  A flat CSV table where each row represents an ATL08 land segment.

- **Quality Control (QC)**  
  Boolean filtering rules applied to point attributes.

- **Beam Semantics**  
  Explicit handling of strong and weak beams based on satellite orientation.

- **Spatial Context**  
  Integration of vector and raster masks to restrict analysis regions.
---



## Input Data Format

General Requirements
-	Input data are provided as CSV point tables
-	Column names are user-defined and referenced directly in expressions
-	Coordinates are typically stored as lon / lat (EPSG:4326) or projected coordinates

Filtering (filter command)

The filtering expression may use:
-	Arithmetic operators: + - * / **
-	Comparison operators: < <= > >= == !=
-	Boolean operators: and, or, not
-	Built-in function: abs(x)

All referenced columns must exist in the input table.

Strong-Beam Selection (beams command)

The input CSV must contain:
-	beam: beam identifier (e.g. gt1l, gt2r)
-	source_file: source ATL08 filename (used to match HDF5 metadata)

---


## Command Reference


This section documents the core commands provided by `atl08kit`.
Each command is designed to perform a single, well-defined operation and can be
used independently or composed into a larger workflow.


### `extract` — Convert ATL08 HDF5 to point tables

The `extract` command converts ICESat-2 ATL08 HDF5 files into flat CSV point tables
based on the `land_segments` group.

```bash
atl08kit extract \
  --h5 ATL08_20220102113835_01711406_007_01.h5 \
  --out points_raw.csv \
  --summary
```
#### Behavior
-   Reads all available beams (gt1l–gt3r) by default
-    Traverses the land_segments group of each beam
-    Extracts all 1D datasets aligned with latitude/longitude
-    Automatically skips:
-    Multi-dimensional datasets
-    Datasets whose length does not match the number of land segments
-    Flattens nested dataset paths into column names(e.g. terrain/h_te_best_fit → terrain_h_te_best_fit)

#### Always included columns
-    lon, lat — point coordinates
-    beam — beam identifier (gt1l, gt2r, etc.)
-    source_file — ATL08 file stem for traceability

#### Notes

The output CSV is the standard interchange format used by all downstream
commands in atl08kit.

### `filter` — Expression-based quality control

The filter command applies boolean quality-control rules to a point table
using a safe, expression-based DSL.
```bash
atl08kit filter \
  --in points_raw.csv \
  --out points_qc.csv \
  --expr "abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3" \
  --summary
```

#### Expression language

#### Supported elements include:
-    Arithmetic operators: +  -  *  /  **
-    Comparison operators: <  <=  >  >=  ==  !=
-    Boolean operators: and, or, not
-    Built-in functions: abs(x)

Expressions are parsed using Python’s AST and validated against a strict
whitelist to prevent unsafe execution.

#### Examples
-    abs(dem_h - terrain_h_te_best_fit) <= 3
-    terrain_flg == 0 and cloud_flag_atm < 3
-    abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3

#### Notes
-    All referenced column names must exist in the input table
-    The expression must evaluate to a boolean mask
    
### `beams` — Strong-beam selection

The beams command filters a point table to retain only strong-beam
measurements based on satellite orientation (sc_orient).
```bash
atl08kit beams \
  --in points.csv \
  --out points_strong.csv \
  --h5-folder /path/to/ATL08_h5_files \
  --summary
```
Requirements

The input CSV must contain:
-    beam — beam identifier
-    source_file — ATL08 filename or stem

Behavior
-    Reads sc_orient from each ATL08 HDF5 file
-    Determines which beams are strong for each orbit
-    Keeps only rows corresponding to strong beams

This command makes beam semantics explicit and avoids hard-coded assumptions
in analysis scripts.


### `vector` — Spatial filtering with vector masks

The vector command filters points using polygon masks (AOIs).

```bash
atl08kit vector \
  --in points_qc.csv \
  --out points_aoi.csv \
  --mask boundary/2022.shp \
  --mode clip \
  --summary
```
#### Modes
-    clip — keep points inside the polygon
-    exclude — keep points outside the polygon

Spatial predicates
-    within (default)
-    intersects

#### Monthly AOI support

For time-dependent AOIs (e.g. monthly boundaries), vector supports
automatic mask resolution based on the ATL08 filename:

```bash
atl08kit vector \
  --in points.csv \
  --out points_aoi.csv \
  --monthly-folder boundaries/ \
  --source-file ATL08_20220102113835_01711406_007_01 \
  --ext .shp
```
In this mode, the AOI file is inferred from the year-month encoded in
the ATL08 filename.

#### `raster` — Raster-based masking

The raster command filters points by sampling values from a raster dataset.

```bash
atl08kit raster \
  --in points.csv \
  --out points_masked.csv \
  --raster landcover.tif \
  --keep 1 2 3 \
  --summary
```
Capabilities
-    Keep or drop points based on raster values
-    Select raster band
-    Optionally keep or discard nodata samples

This is commonly used for land-cover masks, DEM validity layers,
or classification rasters.

### `export` — Export to geospatial vector formats

The export command converts a CSV point table into standard GIS vector formats

```bash
atl08kit export \
  --in points_aoi.csv \
  --out points_aoi.geojson \
  --summary
  ```
Supported formats
-    GeoJSON (.geojson)
-    GeoPackage (.gpkg)
-    ESRI Shapefile (.shp)

All attribute columns are preserved in the output.
Export requires geopandas.

#### Python API Example

All core functionality in atl08kit is also available programmatically.
```python
import pandas as pd
from atl08kit.filters import filter_by_expr

df = pd.read_csv("points_raw.csv")

filtered, summary = filter_by_expr(
    df,
    "abs(dem_h - terrain_h_te_best_fit) <= 3 and cloud_flag_atm < 3"
)

print(summary)
filtered.to_csv("points_qc.csv", index=False)
```
The Python API mirrors the CLI behavior and is designed for reproducible
research workflows and integration into larger analysis pipelines.

---

## Testing

Automated tests are implemented using pytest.

Run the full test suite:
```bash
pytest
```
The tests include:
-	Unit tests for expression parsing and filtering
-	Unit tests for strong-beam logic
-	CLI tests executed via subprocess
-	Pipeline and batch integration tests

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
