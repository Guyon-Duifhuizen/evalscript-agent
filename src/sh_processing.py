from datetime import datetime, timedelta

from sentinelhub import (
    CRS,
    DataCollection,
    Geometry,
    MimeType,
    SentinelHubRequest,
    SHConfig,
)
from shapely.geometry import mapping


def process_feature(
    config: SHConfig,
    collection_id: str,
    feature,
    evalscript: str,
    resolution: tuple = (10, 10),
):
    geometry = Geometry(mapping(feature.geometry), crs=CRS(feature["proj:epsg"]))
    feature_datetime = datetime.fromisoformat(feature["datetime"])
    time_window = timedelta(seconds=1)
    time_interval = (feature_datetime - time_window, feature_datetime + time_window)

    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.define_byoc(collection_id),
                time_interval=time_interval,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        config=config,
        geometry=geometry,
        resolution=resolution,
    )

    return request.get_data()
