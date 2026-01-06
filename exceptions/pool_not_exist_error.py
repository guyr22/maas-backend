class PoolNotExistsError(Exception):
    def __init__(self, pool_name: str):
        super().__init__(f"Pool {pool_name} does not exist")
    