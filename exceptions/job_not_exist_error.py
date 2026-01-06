class JobNotExistsError(Exception):
    def __init__(self, job_name: str, collector_name: str):
        super().__init__(f"Job name {job_name} does not exist for collector {collector_name}")