"""
national_map_client.py

Python clients for USGS National Map ArcGIS REST services.

Provides access to:
  - Watershed Boundary Dataset (WBD): HUC-12 subwatershed polygons
    Source: USGS, USDA, NRCS
  - National Hydrography Dataset (NHD): Flowlines and Waterbodies (Large Scale)
    Source: USGS (retired October 2023; still available, no longer maintained)
  - NHDPlus High Resolution: Flowlines with network connectivity attributes
    Source: USGS (current standard; development paused pending 3D Hydrography Program)

All clients query ArcGIS REST MapServer endpoints and return geopandas GeoDataFrames.

Note: NHDPlus HR column names are uppercase (GNIS_NAME, FTYPE, FCODE).
      Standard NHD column names are lowercase (gnis_name, ftype, fcode).
"""

import io
import warnings
from typing import List, Union

import requests
import geopandas as gpd


class NationalMapClient:
    """
    Base client for USGS National Map ArcGIS REST services.

    Subclasses provide pre-configured URLs for specific datasets and layers.
    All queries return a GeoDataFrame in EPSG:4326.

    Parameters
    ----------
    base_url : str
        ArcGIS REST MapServer layer query endpoint URL.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def query(
        self,
        bbox: str | None = None,
        mask: gpd.GeoDataFrame | None = None,
        huc_prefix: str | None = None,
        huc_col: str = "huc12",
        where_clause: str = "1=1",
        out_fields: Union[str, List[str]] = "*",
        geometry_precision: int | None = None,
        normalize_columns: bool = False,
    ) -> gpd.GeoDataFrame:
        """
        Query the ArcGIS REST service and return a GeoDataFrame.

        Spatial filtering is applied via either a bounding box string or a
        GeoDataFrame mask. If both are provided, bbox takes precedence.
        Attribute filtering can be combined with spatial filtering.

        Parameters
        ----------
        bbox : str, optional
            Bounding box as a comma-separated string "minx,miny,maxx,maxy"
            in EPSG:4326.
        mask : geopandas.GeoDataFrame, optional
            GeoDataFrame whose bounding box is used for spatial filtering.
            Automatically reprojected to EPSG:4326 if needed.
        huc_prefix : str, optional
            HUC ID prefix for attribute filtering, e.g. "0712" selects all
            HUCs beginning with those digits.
        huc_col : str, default "huc12"
            Column name to apply the huc_prefix filter against.
        where_clause : str, default "1=1"
            SQL WHERE clause for additional attribute filtering.
        out_fields : str or list of str, default "*"
            Fields to return. Pass a list for convenience; it will be
            joined to a comma-separated string automatically.
        geometry_precision : int, optional
            Number of decimal places for returned coordinates. Reducing
            this (e.g. to 5) decreases payload size at the cost of precision.
        normalize_columns : bool, default False
            If True, convert all column names to lowercase. Useful when querying
            NHDPlus HR, which returns uppercase column names (GNIS_NAME, FTYPE,
            FCODE) unlike standard NHD which uses lowercase.
            
        Returns
        -------
        geopandas.GeoDataFrame
            Query results with geometry in EPSG:4326.

        Raises
        ------
        RuntimeError
            If the ArcGIS service returns an error response.
        requests.HTTPError
            If the HTTP request fails.

        Warns
        -----
        UserWarning
            If the service reports that the transfer limit was exceeded and
            results are incomplete.
        """
        if isinstance(out_fields, list):
            out_fields = ",".join(out_fields)

        params: dict = {
            "where": where_clause,
            "outFields": out_fields,
            "returnGeometry": "true",
            "f": "geojson",
        }

        if bbox:
            params["geometry"] = bbox
            params["geometryType"] = "esriGeometryEnvelope"
            params["inSR"] = "4326"
            params["spatialRel"] = "esriSpatialRelIntersects"

        elif mask is not None:
            mask_4326 = mask.to_crs(4326) if mask.crs and mask.crs.to_epsg() != 4326 else mask
            bounds = mask_4326.total_bounds
            params["geometry"] = f"{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]}"
            params["geometryType"] = "esriGeometryEnvelope"
            params["inSR"] = "4326"
            params["spatialRel"] = "esriSpatialRelIntersects"

        if geometry_precision is not None:
            params["geometryPrecision"] = geometry_precision

        if huc_prefix:
            huc_filter = f"{huc_col} LIKE '{huc_prefix}%'"
            if params["where"] == "1=1":
                params["where"] = huc_filter
            else:
                params["where"] = f"({params['where']}) AND ({huc_filter})"

        response = requests.get(self.base_url, params=params, timeout=60)
        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise RuntimeError(data["error"])

        if data.get("exceededTransferLimit"):
            warnings.warn(
                "Transfer limit exceeded — results are incomplete. "
                "Consider using a smaller bbox, huc_prefix filter, or contact "
                "the service for pagination support.",
                UserWarning,
                stacklevel=2,
            )
            
        gdf = gpd.read_file(io.BytesIO(response.content))

        if normalize_columns:
            gdf.columns = gdf.columns.str.lower()

        return gdf




class WBDClient(NationalMapClient):
    """
    Client for the Watershed Boundary Dataset (WBD), HUC-12 subwatersheds.

    Source: USGS/USDA/NRCS
    Service: WBD MapServer, layer 6
    """
    def __init__(self) -> None:
        super().__init__(
            "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/6/query"
        )


class NHDFlowlineClient(NationalMapClient):
    """
    Client for NHD Flowlines at large scale (1:24,000).

    Source: USGS National Hydrography Dataset (NHD)
    Service: NHD MapServer, layer 6
    Note: NHD was retired October 2023 and is no longer maintained.
    """
    def __init__(self) -> None:
        super().__init__(
            "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/6/query"
        )


class NHDWaterbodyClient(NationalMapClient):
    """
    Client for NHD Waterbodies at large scale (1:24,000).

    Source: USGS National Hydrography Dataset (NHD)
    Service: NHD MapServer, layer 12
    Note: NHD was retired October 2023 and is no longer maintained.
    """
    def __init__(self) -> None:
        super().__init__(
            "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/12/query"
        )


class NHDPlusFlowlineClient(NationalMapClient):
    """
    Client for NHDPlus High Resolution Flowlines.

    Source: USGS NHDPlus High Resolution
    Service: NHDPlus_HR MapServer, layer 3 (NetworkNHDFlowline)

    Note: Column names are uppercase (GNIS_NAME, FTYPE, FCODE), unlike
    standard NHD which uses lowercase. Normalize with:
        gdf.columns = gdf.columns.str.lower()
    """
    def __init__(self) -> None:
        super().__init__(
            "https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer/3/query"
        )