# Rivers

A collection of Python tools and notebooks for visualizing and analyzing river
watersheds, environmental conditions, and streamflow data using USGS, NOAA, and
USBR public datasets. Currently this is divided into two sections. One for Chicago area waterways,
and another for the Colorado River in the Grand Canyon.

## Overview

This repository provides reusable Python clients for querying federal hydrological
and climate data services, along with Jupyter notebooks that demonstrate their use
for specific river systems. It is intended for geoscientists, environmental
scientists, educators, students, and river enthusiasts.

The core modules are:

* **`national_map_client.py`** — Query the USGS National Map for watershed
  boundaries, flowlines, and waterbodies.
* **`ncei_io.py`** — Fetch climate and weather data from the NOAA National
  Centers for Environmental Information (NCEI).
* **`usgs_io.py`** — Helper functions for wrangling USGS Water Data tables
  returned by the `dataretrieval.waterdata` API.

## Repository Structure

```text
rivers/
├── national_map_client.py      # USGS National Map client
├── ncei_io.py                  # NOAA NCEI client
├── usgs_io.py                  # USGS Water Data helper functions
├── chicagoland/
│   ├── nbcr.ipynb              # North Branch Chicago River watershed map
│   └── figures/
├── grand_canyon/
│   ├── grand_canyon_conditions.ipynb
│   ├── crsp.ipynb              # CRSP reservoir storage from Bureau of Reclamation RISE
│   ├── images/                 # input image (CRSP map)
│   └── figures/                # generated plots
├── environment.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

## Quick Start

### Install dependencies

Using conda:

```bash
conda env create -f environment.yml
conda activate rivers
```

Or using pip:

```bash
pip install -r requirements.txt
pip install -e .
```

For the Grand Canyon notebook, the most important Python packages are:

```bash
pip install pandas matplotlib requests dataretrieval
```

## Notebooks

### North Branch Chicago River (`chicagoland/nbcr.ipynb`)

A watershed map of the North Branch Chicago River system showing HUC-12
subwatersheds, NHDPlus flowlines scaled by mean annual discharge, USGS gage
locations, and water resource facilities. Developed for use in environmental
science education.

### Grand Canyon Conditions (`grand_canyon/grand_canyon_conditions.ipynb`)

[![Open Grand Canyon Conditions in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gregorywanderson/rivers/blob/main/grand_canyon/grand_canyon_conditions.ipynb)

This notebook plots river, reservoir, and weather conditions in the Grand Canyon
corridor. It uses USGS Water Data for Colorado River discharge, Lees Ferry water
temperature, and Lake Powell elevation, and NOAA/NCEI data for Phantom Ranch air
temperature.

The notebook produces two main figures:

1. A multi-year daily-values plot showing Colorado River discharge, Lake Powell
   elevation, Lees Ferry water temperature, and Phantom Ranch air temperature.
2. A shorter continuous-values plot showing higher-frequency Colorado River flow
   and water-temperature changes over a selected time window.

The notebook can be run locally or launched in Google Colab using the badge
above.

### Colorado River Storage Project (`grand_canyon/crsp.ipynb`)

[![Open CRSP Storage in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gregorywanderson/rivers/blob/main/grand_canyon/crsp.ipynb)

This notebook downloads and plots multi-year storage for the seven major Colorado
River Storage Project (CRSP) reservoirs in the Upper Basin: Lake Powell, Flaming
Gorge, Navajo, Blue Mesa, Fontenelle, Morrow Point, and Crystal. Data are pulled
at runtime from the Bureau of Reclamation's Reclamation Information Sharing
Environment (RISE) API.

The notebook produces a two-panel figure:

1. Absolute storage (million acre-feet) for all seven reservoirs, showing how Lake
   Powell dwarfs the others combined.
2. Percent of live capacity for the four primary storage reservoirs, where the
   multi-year drought drawdown and the annual spring snowmelt cycle are visible.

The notebook can be run locally or launched in Google Colab using the badge above.


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
    normalize_columns=True,
)

print(f"Found {len(flowlines)} flowlines")
```


## Data Sources

All data are retrieved at runtime from public federal services.

| Dataset                               | Source                                                                                        | Access                    |
| ------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------- |
| Watershed Boundary Dataset (WBD)      | USGS / USDA / NRCS                                                                            | USGS National Map         |
| NHD Flowlines                         | USGS                                                                                          | USGS National Map         |
| NHDPlus HR Flowlines                  | USGS                                                                                          | USGS National Map         |
| River discharge and water temperature | USGS Water Data                                                                               | `dataretrieval.waterdata` |
| Lake Powell elevation                 | USGS Water Data; Bureau of Reclamation is the definitive source for reservoir operations data | `dataretrieval.waterdata` |
| Climate and weather data              | NOAA NCEI                                                                                     | `ncei_io.py`              |
| CRSP reservoir storage                | Bureau of Reclamation                                                                         | RISE API (`data.usbr.gov`) |

USGS and NOAA data are in the public domain.

## Notes on USGS Water Data

The Grand Canyon notebook uses the modern `waterdata` module from the USGS
`dataretrieval` Python package.

The notebook uses:

* `waterdata.get_daily()` for daily values,
* `waterdata.get_continuous()` for higher-frequency continuous values.

The USGS Water Data API returns long/tidy tables with columns such as
`monitoring_location_id`, `parameter_code`, `statistic_id`, `time`, and `value`.
The helper functions in `usgs_io.py` convert these returned tables into
time-indexed dataframes suitable for plotting and exploratory analysis.

Useful USGS links:

* https://doi-usgs.github.io/dataretrieval-python/
* https://help.waterdata.usgs.gov/codes-and-parameters/parameters
* https://waterdata.usgs.gov/
* https://maps.waterdata.usgs.gov/mapper/

## Notes on NOAA/NCEI Data

The Grand Canyon notebook uses `ncei_io.py` to retrieve Phantom Ranch air
temperature data from NOAA's National Centers for Environmental Information
using the GHCN-Daily dataset.

The Phantom Ranch station used in the notebook is:

```text
USC00026471
```

Useful NCEI links:

* https://www.ncei.noaa.gov/
* https://www.ncei.noaa.gov/cdo-web/search?datasetid=GHCND

## Requirements

* Python 3.11 or later
* See `environment.yml` for the full environment

Key dependencies include:

* `pandas`
* `matplotlib`
* `requests`
* `dataretrieval`
* `geopandas`
* `contextily`

Some notebooks use only a subset of these packages.

## License

Copyright (C) 2025 Gregory Anderson

This program is free software: you can redistribute it and/or modify it under
the terms of the [GNU General Public License v3](LICENSE) as published by the
Free Software Foundation.

## Contributing

Contributions, bug reports, and suggestions are welcome via
[GitHub Issues](https://github.com/gregorywanderson/rivers/issues).
