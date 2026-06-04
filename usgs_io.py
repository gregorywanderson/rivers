# usgs_io.py
#
# Helper functions for USGS Water Data / dataretrieval.waterdata output.

import pandas as pd


def wrangle_waterdata_timeseries(
    df,
    *,
    time_col="time",
    value_col="value",
    value_name="value",
    tz="America/Phoenix",
):
    """
    Convert a USGS waterdata time-series table into a plotting-friendly
    DataFrame.

    The returned DataFrame is sorted by time, indexed by a timezone-aware
    datetime index, and has a numeric data column renamed from `value_col`
    to `value_name`.

    This works for dataretrieval.waterdata.get_daily() and should also work
    for dataretrieval.waterdata.get_continuous(), provided the returned table
    has `time` and `value` columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Output table returned by dataretrieval.waterdata.
    time_col : str, default "time"
        Column containing timestamps.
    value_col : str, default "value"
        Column containing the measured values.
    value_name : str, default "value"
        New name for the measured-value column.
    tz : str, default "America/Phoenix"
        Time zone for the returned datetime index.

    Returns
    -------
    pandas.DataFrame
        Time-indexed DataFrame with the measured value column renamed.
    """
    out = df.copy()

    out[time_col] = pd.to_datetime(out[time_col])
    out[value_col] = pd.to_numeric(out[value_col], errors="coerce")

    out = out.set_index(time_col).sort_index()

    if out.index.tz is None:
        out.index = out.index.tz_localize(tz)
    else:
        out.index = out.index.tz_convert(tz)

    return out.rename(columns={value_col: value_name})


def waterdata_to_wide(
    df,
    *,
    names,
    value_col="value",
):
    """
    Pivot a wrangled USGS waterdata table from long/tidy form to wide form.

    Parameters
    ----------
    df : pandas.DataFrame
        Output from wrangle_waterdata_timeseries().
    names : dict
        Mapping from (parameter_code, statistic_id) to output column name.
    value_col : str, default "value"
        Name of the measured-value column.

    Returns
    -------
    pandas.DataFrame
        Time-indexed DataFrame with one column per named parameter/statistic.
    """
    out = df.copy()

    out["series_name"] = [
        names.get((param, stat))
        for param, stat in zip(out["parameter_code"], out["statistic_id"])
    ]

    out = out.dropna(subset=["series_name"])

    wide = out.pivot_table(
        index=out.index,
        columns="series_name",
        values=value_col,
        aggfunc="first",
    ).sort_index()

    wide.columns.name = None

    return wide