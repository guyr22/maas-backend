import re
from pydantic import AfterValidator
from typing import Annotated, List
from config.constants.jobs import TARGETS_REGEX


def validate_targets(value: List[str]) -> List[str]:
    if not value:
        raise ValueError("Targets cannot be empty")
    
    pattern = re.compile(TARGETS_REGEX)
    for target in value:
        if not pattern.match(target):
            raise ValueError("Invalid targets format")
    return value

JobTargets = Annotated[List[str], AfterValidator(validate_targets)]