class JobNameExistsError(Exception):
    def __init__(self, job_name: str, collector_cluster: str):
        super().__init__(f"Job name {job_name} already exists for collector {collector_cluster}")