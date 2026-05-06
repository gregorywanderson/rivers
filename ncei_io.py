# ncei_io.py
#
# High-level Python interface to the NOAA/NCEI "Access Data Service" (data/v1),
# plus token-free station-search helpers for GHCND (daily-summaries) and
# ISD/GSOD (global-hourly / global-summary-of-the-day).
#
# This module provides:
#   • A unified internal helper (_get_ncei_data) for making requests to:
#       https://www.ncei.noaa.gov/access/services/data/v1
#
#   • Wrapper functions for specific datasets:
#       - get_ghcnd_daily_summaries()      → GHCN-Daily (daily-summaries)
#       - get_isd_hourly()                 → ISD (global-hourly)
#       - get_gsod_daily()                 → GSOD (global-summary-of-the-day)
#       - get_normals_daily_1991_2020()    → U.S. Climate Normals 1991–2020
#
#   • Token-free station search utilities:
#       - search_ncei_stations_bbox()      → GHCND station metadata
#       - search_isd_stations_bbox()       → ISD/GSOD station metadata
#
# About NCEI / NCDC terminology:
#   • NCEI = National Centers for Environmental Information (NOAA)
#       - formed by merging NCDC (climate), NGDC (geophysical), NODC (ocean)
#
#   • GHCND (Global Historical Climatology Network – Daily)
#       - Daily temperature, precipitation, snow
#       - Used via dataset='daily-summaries'
#
#   • ISD (Integrated Surface Database)
#       - Hourly data (TMP, DEW, WND, VIS, etc.)
#       - Used via dataset='global-hourly'
#
#   • GSOD (Global Summary of the Day)
#       - Daily airport-style summaries
#       - Used via dataset='global-summary-of-the-day'
#
#   • U.S. Climate Normals 1991–2020
#       - Daily climatological normals
#       - Used via dataset='normals-daily-1991-2020'
#
# No part of this module uses the older CDO v2 API (api/v2).


import requests
import pandas as pd
from io import StringIO

BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"

def _get_ncei_data(
    *,
    dataset: str,
    station_id: str,
    start_date: str,
    end_date: str,
    data_types=None,
    units: str | None = None,
    include_station_name: bool = False,
    include_attributes: bool = False,
    extra_params: dict | None = None,
    parse_dates: bool = True,
    index_col: str = "DATE",
) -> pd.DataFrame:
    """
    Generic helper for NCEI Access Data Service (data/v1).

    Parameters
    ----------
    dataset : str
        NCEI dataset name, e.g. "daily-summaries", "global-hourly".
    station_id : str
        Station ID appropriate for the dataset.
    start_date, end_date : str
        Date range "YYYY-MM-DD" (or "0001-..-.." for normals).
    data_types : str or iterable of str, optional
        Data types to request (e.g. "TMAX,TMIN", ["TMP", "DEW"]).
    units : str or None
        If not None, passed as the "units" parameter.
    include_station_name : bool
        If True, includeStationName=true is sent.
    include_attributes : bool
        If True, includeAttributes=true is sent.
    extra_params : dict or None
        Any additional query parameters to merge into the request.
    parse_dates : bool
        Whether to parse index_col as datetime and set as index.
    index_col : str
        Column name to parse as datetime and use as index (default "DATE").

    Returns
    -------
    pandas.DataFrame
    """
    params: dict[str, str] = {
        "dataset": dataset,
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "format": "csv",
        "includeAttributes": "true" if include_attributes else "false",
    }

    if units is not None:
        params["units"] = units

    if include_station_name:
        params["includeStationName"] = "true"

    # Handle dataTypes argument (list or string)
    if data_types is not None:
        if isinstance(data_types, (list, tuple, set)):
            params["dataTypes"] = ",".join(sorted(data_types))
        else:
            params["dataTypes"] = str(data_types)

    # Merge any dataset-specific extras
    if extra_params:
        params.update(extra_params)

    resp = requests.get(BASE_URL, params=params, timeout=60)
    resp.raise_for_status()

    df = pd.read_csv(StringIO(resp.text))

    if parse_dates and index_col in df.columns:
        df[index_col] = pd.to_datetime(df[index_col])
        df["DATE_TMP"] = df[index_col]
        df = df.set_index(index_col).sort_index()
        df.rename(columns={"DATE_TMP": "DATE"}, inplace=True)

    return df


def get_ghcnd_daily_summaries(
    station_id: str,
    start_date: str,
    end_date: str,
    data_types=None,
    units: str = "standard",
    include_station_name: bool = True,
) -> pd.DataFrame:
    """
    Fetch daily GHCND 'daily-summaries' data for a single station from the
    NOAA NCEI Access Data Service (no API token required).
    """
    return _get_ncei_data(
        dataset="daily-summaries",
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        data_types=data_types,
        units=units,
        include_station_name=include_station_name,
        include_attributes=False,
    )


def get_isd_hourly(
    station_id: str,
    start_date: str,
    end_date: str,
    data_types=None,
    units: str = "metric",
) -> pd.DataFrame:
    """
    Fetch hourly data from the Integrated Surface Dataset (ISD) via
    the NCEI Access Data Service (dataset='global-hourly').
    """
    return _get_ncei_data(
        dataset="global-hourly",
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        data_types=data_types,
        units=units,
        include_station_name=False,
        include_attributes=False,
    )


def get_gsod_daily(
    station_id: str,
    start_date: str,
    end_date: str,
    units: str = "standard",
) -> pd.DataFrame:
    """
    Fetch daily data from Global Summary of the Day (GSOD) via
    the NCEI Access Data Service (dataset='global-summary-of-the-day').
    """
    return _get_ncei_data(
        dataset="global-summary-of-the-day",
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        data_types=None,
        units=units,
        include_station_name=False,
        include_attributes=False,
    )


# first
def get_normals_daily_1991_2020(
    station_id: str,
    start_date: str = "0001-01-01",
    end_date: str = "0001-12-31",
) -> pd.DataFrame:
    """
    Fetch U.S. Daily Climate Normals (1991–2020) for a single station
    via the NCEI Access Data Service (dataset='normals-daily-1991-2020').
    """
    # Normals don't use units or station name flags in the same way,
    # so we leave units=None and include_station_name=False.
    return _get_ncei_data(
        dataset="normals-daily-1991-2020",
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        data_types=None,
        units=None,
        include_station_name=False,
        include_attributes=False,
    )

import numpy as np
import pandas as pd

def nearest_station(
    lat: float,
    lon: float,
    stations_df: pd.DataFrame,
    n: int = 3
) -> pd.DataFrame:
    """
    Return the N nearest stations to a given (lat, lon) using the Haversine distance.

    Parameters
    ----------
    lat, lon : float
        Target location in decimal degrees.
    stations_df : pandas.DataFrame
        Must contain LATITUDE and LONGITUDE columns.
        Example: output from search_ncei_stations_bbox() or search_isd_stations_bbox().
    n : int, default 3
        Number of nearest stations to return.

    Returns
    -------
    pandas.DataFrame
        The nearest 'n' stations with an added 'DIST_KM' column.
    """
    # Convert degrees to radians
    lat1 = np.radians(lat)
    lon1 = np.radians(lon)
    lat2 = np.radians(stations_df["LATITUDE"].astype(float))
    lon2 = np.radians(stations_df["LONGITUDE"].astype(float))

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # Earth's radius in km
    R = 6371.0
    dist_km = R * c

    # Attach distance and return nearest N
    df = stations_df.copy()
    df["DIST_KM"] = dist_km

    return df.sort_values("DIST_KM").head(n).reset_index(drop=True)



# ---------------------------------------------------------------------
# GHCND STATION METADATA (token-free, via ghcnd-stations.txt)
# ---------------------------------------------------------------------
_GHCND_STATIONS_DF: pd.DataFrame | None = None


def _load_ghcnd_stations() -> pd.DataFrame:
    """
    Download and parse the GHCND station metadata file using a robust
    fixed-width reader (pandas.read_fwf).

    Source:
        https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt

    Official file layout (fixed width):
        Variable   Columns   Type
        ID         1-11      Character
        LATITUDE   13-20     Real
        LONGITUDE  22-30     Real
        ELEVATION  32-37     Real
        STATE      39-40     Character
        NAME       42-71     Character
        GSN_FLAG   73-75     Character
        HCN/CRN    77-79     Character
        WMO_ID     81-85     Character

    Returns
    -------
    pandas.DataFrame
        Columns:
            STATION, LATITUDE, LONGITUDE, ELEVATION, STATE, NAME,
            GSN_FLAG, HCN_CRN_FLAG, WMO_ID
    """
    global _GHCND_STATIONS_DF
    if _GHCND_STATIONS_DF is not None:
        return _GHCND_STATIONS_DF

    url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    # Column specs are 0-based, end-exclusive
    colspecs = [
        (0, 11),   # ID
        (12, 20),  # LATITUDE
        (21, 30),  # LONGITUDE
        (31, 37),  # ELEVATION
        (38, 40),  # STATE
        (41, 71),  # NAME
        (72, 75),  # GSN_FLAG
        (76, 79),  # HCN/CRN
        (80, 85),  # WMO_ID
    ]
    names = [
        "STATION",
        "LATITUDE",
        "LONGITUDE",
        "ELEVATION",
        "STATE",
        "NAME",
        "GSN_FLAG",
        "HCN_CRN_FLAG",
        "WMO_ID",
    ]

    df = pd.read_fwf(
        StringIO(resp.text),
        colspecs=colspecs,
        names=names,
        dtype={
            "STATION": "string",
            "STATE": "string",
            "NAME": "string",
            "GSN_FLAG": "string",
            "HCN_CRN_FLAG": "string",
            "WMO_ID": "string",
        },
    )

    # Clean up numeric fields and missing values
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
    df["ELEVATION"] = pd.to_numeric(df["ELEVATION"], errors="coerce")

    _GHCND_STATIONS_DF = df
    return df


def search_ncei_stations_bbox(
    north: float,
    west: float,
    south: float,
    east: float,
    dataset: str = "daily-summaries",
    limit: int = 1000,
    token: str | None = None,  # kept for backwards compatibility; unused
) -> pd.DataFrame:
    """
    Find GHCND stations within a bounding box, token-free.

    This implementation bypasses the NCEI Search API and instead uses the
    public GHCND station metadata file (ghcnd-stations.txt). It is therefore
    specific to the GHCN-Daily / "daily-summaries" dataset.

    Parameters
    ----------
    north, west, south, east : float
        Bounding box edges in decimal degrees:
            north : max latitude
            west  : min longitude
            south : min latitude
            east  : max longitude
    dataset : str, default "daily-summaries"
        Kept for API symmetry; must be "daily-summaries" for now.
    limit : int, default 1000
        Maximum number of stations to return (after filtering).
    token : str, optional
        Ignored (no token needed); present only to avoid breaking callers
        that pass token=NCEI_TOKEN.

    Returns
    -------
    pandas.DataFrame
        Stations within the bounding box. Includes at least:
            STATION, NAME, LATITUDE, LONGITUDE, ELEVATION, STATE
    """
    if dataset != "daily-summaries":
        raise ValueError(
            "search_ncei_stations_bbox currently only supports "
            'dataset="daily-summaries" (GHCN-Daily).'
        )

    stations = _load_ghcnd_stations()

    mask = (
        (stations["LATITUDE"] <= north)
        & (stations["LATITUDE"] >= south)
        & (stations["LONGITUDE"] >= west)
        & (stations["LONGITUDE"] <= east)
    )

    subset = stations.loc[mask].copy()

    if limit is not None and len(subset) > limit:
        subset = subset.head(limit)

    return subset.reset_index(drop=True)


# ================================================================
# ISD / GSOD STATION METADATA (token-free, via isd-history.csv)
# ================================================================

_ISD_HISTORY_DF = None  # cached station metadata


def _load_isd_history() -> pd.DataFrame:
    """
    Download and cache the ISD/GSOD station metadata table.

    Source:
        https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv

    Columns (simplified):
        USAF, WBAN, STATION NAME, CTRY, ST, CALL, LAT, LON, ELEV(M), BEGIN, END

    We construct a numeric 11-char station_id = f"{USAF:06d}{WBAN:05d}",
    which is what the Access Data Service expects for both:
        - dataset=global-hourly
        - dataset=global-summary-of-the-day
    """
    global _ISD_HISTORY_DF
    if _ISD_HISTORY_DF is not None:
        return _ISD_HISTORY_DF

    url = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    df = pd.read_csv(StringIO(resp.text))

    # Clean up and construct STATION_ID (11-digit string)
    # Some rows have WBAN=99999 for “placeholder”; we still keep them.
    df["USAF"] = df["USAF"].astype(str).str.zfill(6)
    df["WBAN"] = df["WBAN"].astype(str).str.zfill(5)
    df["STATION_ID"] = df["USAF"] + df["WBAN"]

    # Rename a few columns to nicer names
    df = df.rename(
        columns={
            "STATION NAME": "NAME",
            "LAT": "LATITUDE",
            "LON": "LONGITUDE",
            "ELEV(M)": "ELEVATION_M",
            "CTRY": "COUNTRY",
            "ST": "STATE",
        }
    )

    _ISD_HISTORY_DF = df
    return df


def search_isd_stations_bbox(
    north: float,
    west: float,
    south: float,
    east: float,
    limit: int = 1000,
) -> pd.DataFrame:
    """
    Token-free station search for ISD / GSOD stations within a bounding box,
    based on isd-history.csv.

    Parameters
    ----------
    north, west, south, east : float
        Bounding box in decimal degrees:
            north : max latitude
            west  : min longitude
            south : min latitude
            east  : max longitude
    limit : int, default 1000
        Maximum number of stations to return.

    Returns
    -------
    pandas.DataFrame
        Subset of ISD history with (at least) columns:
            STATION_ID, NAME, LATITUDE, LONGITUDE, ELEVATION_M,
            COUNTRY, STATE, BEGIN, END
    """
    stations = _load_isd_history()

    mask = (
        (stations["LATITUDE"] <= north)
        & (stations["LATITUDE"] >= south)
        & (stations["LONGITUDE"] >= west)
        & (stations["LONGITUDE"] <= east)
    )
    subset = stations.loc[mask].copy()

    if limit is not None and len(subset) > limit:
        subset = subset.head(limit)

    return subset.reset_index(drop=True)

