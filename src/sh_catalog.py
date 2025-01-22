import geopandas as gpd
from sentinelhub import BBox, SentinelHubCatalog, SHConfig


def get_features(config: SHConfig, collection_id: str) -> gpd.GeoDataFrame:
    catalog = SentinelHubCatalog(config=config)
    bbox = BBox(bbox=[-180, -90, 180, 90], crs="EPSG:4326")
    search_iterator = catalog.search(
        collection=collection_id,
        limit=1,
        time=("2000-01-01", "2024-12-01"),
        bbox=bbox,
    )
    features = search_iterator._fetch_features()
    return gpd.GeoDataFrame.from_features(features).set_crs("EPSG:4326")
