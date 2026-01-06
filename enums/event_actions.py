from enum import Enum


class EventActions(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"