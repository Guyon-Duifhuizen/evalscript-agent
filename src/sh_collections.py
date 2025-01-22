from sentinelhub import SentinelHubCatalog, SHConfig


def list_byoc_collections(config: SHConfig) -> list:
    catalog = SentinelHubCatalog(config=config)
    return [c for c in catalog.get_collections() if "byoc" in c["id"]]
