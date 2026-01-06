import re
from pydantic import AfterValidator
from typing import Annotated, List
from config.constants.jobs import ENDPOINT_REGEX


def validate_endpoint(value: List[str]) -> List[str]:
    if not value:
        raise ValueError("Endpoint cannot be empty")
    
    pattern = re.compile(ENDPOINT_REGEX)
    for endpoint in value:
        if not pattern.match(endpoint):
            raise ValueError("Invalid endpoint format")
    return value

JobEndpoints = Annotated[List[str], AfterValidator(validate_endpoint)]
