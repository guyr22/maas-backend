import motor.motor_asyncio
from beanie import init_beanie
from models.db_schemas.api_keys import ApiKey
from models.db_schemas.jobs import BaseJob, GeneralJob, BlackboxJob, KubernetesJob, HttpJob
from models.db_schemas.maas_pools import MaasPool
from config import config


async def init_db():
    MONGO_CONNECTION_STRING = config['db']['MONGO_CONNECTION_STRING']
    client = motor.motor_asyncio.AsyncIoMotorClient(MONGO_CONNECTION_STRING)
    database = client.maas

    await init_beanie(database=database, document_models=[ApiKey, MaasPool, BaseJob, GeneralJob, BlackboxJob, KubernetesJob, HttpJob])