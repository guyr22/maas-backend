class CollectorNotInPoolError(Exception):
    def __init__(self, maas_pool: str, collector_cluster: str):
        super().__init__(f"Collector {collector_cluster} does not exist in pool {maas_pool}")