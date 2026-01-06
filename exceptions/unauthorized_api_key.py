class UnauthorizedApiKeyError(Exception):
    def __init__(self, maas_pool: str):
        super().__init__(f"API key is not authorized for pool {maas_pool}")