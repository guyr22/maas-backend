from typing import Dict, Any
import json
from aiokafka import AIOKafkaProducer
from config import config
from enums.job_type import JobType
from exceptions.produce_failure_error import ProduceFailureError
from models.events import JobEvent
from utils.logger import create_logger

KAFKA_CONFIG = config['kafka']
logger = create_logger("producer")
ENCODING_FORMAT = 'utf-8'


class KafkaProducer:
    _instance = None
    _producer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KafkaProducer, cls).__new__(cls)
        
        return cls._instance
    
    async def start(self):
        if self._producer is None:
            params = {
                'bootstrap_servers': KAFKA_CONFIG['bootstrap_servers'],
                'client_id': KAFKA_CONFIG['sasl_username'],
                'acks': 'all',
                'security_protocol': KAFKA_CONFIG['security_protocol'],
                'sasl_mechanism': KAFKA_CONFIG['sasl_mechanism'],
                'sasl_plain_username': KAFKA_CONFIG['sasl_username'],
                'sasl_plain_password': KAFKA_CONFIG['sasl_password']            
                }
            
            self._producer = AIOKafkaProducer(**params)
            await self._producer.start()
            logger.info("Kafka producer started")
    
    async def stop(self):
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped")

    async def send_event(self, action: str, maas_pool: str, collector_cluster: str, job_type: JobType, job_name: str, job_data: Dict[str, Any] = None):
        if not self._producer:
            await self.start()
        
        event = JobEvent(action=action, maas_pool=maas_pool, collector_cluster=collector_cluster, job_type=job_type, job_name=job_name, job_data=job_data)
        value_bytes = json.dumps(event.model_dump()).encode(ENCODING_FORMAT)
        event_key = maas_pool.encode(ENCODING_FORMAT)

        try:
            await self._producer.send_and_wait(KAFKA_CONFIG['topic'], value=value_bytes, key=event_key)
            logger.info(f"Event {event} sent successfully")
        except Exception as e:
            logger.error(f"Failed to send event {event}: {str(e)}")
            raise ProduceFailureError(str(e))
    
producer = KafkaProducer()