# Data Directory

## MWRD O'Brien Outfall Data

**File:** `obrien_outfall_timeseries.csv`

This file contains daily outfall discharge data (in MGD) from the O'Brien Water 
Reclamation Plant on the North Shore Channel, operated by the Metropolitan Water 
Reclamation District of Greater Chicago (MWRD).

### How to obtain this data

1. Go to [https://mwrd.org/search](https://mwrd.org/search) and search for 
   **"O'Brien Outfall"**
2. Download the Excel spreadsheet (e.g. `O'Brien Outfall 2021-2030.xlsx`)
3. Extract the relevant sheet and save as `obrien_outfall_timeseries.csv` in 
   this directory

The CSV should have at minimum the following columns:

| Column | Description |
|---|---|
| `timestamp` | Date of measurement (parseable by pandas `parse_dates`) |
| `FLOW` | Discharge in MGD (million gallons per day) |

### Notes

- MWRD does not currently provide an API for this data
- Data is updated periodically; check the MWRD website for the most recent file
- The notebook converts MGD to cfs using the factor `1 MGD = 1.5472 cfs`

## USGS NWIS Data

All USGS gauge data is fetched at runtime via the 
[dataretrieval](https://doi-usgs.github.io/dataretrieval-python/) package 
and does not need to be downloaded manually.