from enum import Enum


class BlackboxJobModules(str, Enum):
    DEFAULT = "default"
    HTTP_2XX = "http_2xx"
    
