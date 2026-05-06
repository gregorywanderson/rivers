# rivers

A collection of Python tools and notebooks for visualizing and analyzing river 
watersheds, environmental conditions, and streamflow data using USGS and NOAA 
public datasets.

![North Branch Chicago River Watersheds](chicagoland/figures/north_branch_watersheds.png)

## Overview

This repository provides reusable Python clients for querying federal hydrological 
and climate data services, along with Jupyter notebooks that demonstrate their use 
for specific river systems. It is intended for geo-scientists, environmental 
scientists, educators, and river enthusiasts.

The two core modules are:

- **`national_map_client.py`** — Query the USGS National Map for watershed 
  boundaries (WBD), flowlines, and waterbodies (NHD and NHDPlus HR).
- **`ncei_io.py`** — Fetch climate and weather data from the NOAA National 
  Centers for Environmental Information (NCEI).

## Repository Structure

rivers/
├── national_map_client.py   # USGS National Map client
├── ncei_io.py               # NOAA NCEI client
├── chicagoland/
│   ├── nbcr.ipynb           # North Branch Chicago River watershed map
│   └── figures/
├── grand_canyon/
│   ├── grand_canyon_conditions.ipynb  # Colorado River flow and climate
│   └── figures/
├── environment.yml
├── pyproject.toml
├── LICENSE
└── README.md

## Quick Start

### Install dependencies

Using conda (recommended):

```bash
conda env create -f environment.yml
conda activate rivers
```

Or using pip:

```bash
pip install -e .
```

### Example: Fetch watersheds for the North Branch Chicago River

```python
from national_map_client import WBDClient

wbd_client = WBDClient()
watersheds = wbd_client.query(huc_prefix="07120003")
print(f"Found {len(watersheds)} HUC-12 watersheds")
watersheds.plot()
```

### Example: Fetch NHDPlus flowlines for a study area

```python
from national_map_client import NHDPlusFlowlineClient

nhd_client = NHDPlusFlowlineClient()
flowlines = nhd_client.query(
    mask=watersheds,
    normalize_columns=True
)
print(f"Found {len(flowlines)} flowlines")
```

## Notebooks

### North Branch Chicago River (`chicagoland/nbcr.ipynb`)
A watershed map of the North Branch Chicago River system showing HUC-12 
subwatersheds, NHDPlus flowlines scaled by mean annual discharge, USGS gauge 
locations, and water resource facilities. Developed for use in environmental 
science education.

### Grand Canyon (`grand_canyon/`)
Streamflow and climate conditions along the Colorado River through the Grand 
Canyon, using USGS NWIS discharge data and NOAA NCEI climate records. Useful 
for trip planning and historical analysis.

## Data Sources

All data is retrieved at runtime from public federal services:

| Dataset | Source | Access |
|---|---|---|
| Watershed Boundary Dataset (WBD) | USGS/USDA/NRCS | USGS National Map |
| NHD Flowlines | USGS (retired Oct 2023) | USGS National Map |
| NHDPlus HR Flowlines | USGS | USGS National Map |
| Streamflow (NWIS) | USGS | dataretrieval package |
| Climate (GHCND, ISD) | NOAA NCEI | ncei_io module |

USGS and NOAA data are in the public domain.

## Requirements

- Python 3.11 or later
- See `environment.yml` for full dependency list

Key dependencies: `geopandas`, `contextily`, `matplotlib`, `requests`, 
`dataretrieval`

## License

Copyright (C) 2025 Gregory Anderson

This program is free software: you can redistribute it and/or modify it under 
the terms of the [GNU General Public License v3](LICENSE) as published by the 
Free Software Foundation.

## Contributing

Contributions, bug reports, and suggestions are welcome via 
[GitHub Issues](https://github.com/gregorywanderson/rivers/issues).