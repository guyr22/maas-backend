from enum import Enum


class JobType(str, Enum):
    BLACKBOX = "blackbox"
    GENERAL = "general"
    HTTP_SD = "http_sd"
    KUBERNETES_SD = "kubernetes_sd"
    