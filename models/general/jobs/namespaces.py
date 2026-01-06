import re
from pydantic import AfterValidator
from typing import Annotated, List
from config.constants.jobs import NAMESPACE_REGEX


def validate_namespaces(value: List[str]) -> List[str]:
    if not value:
        raise ValueError("Namespaces cannot be empty")
    pattern = re.compile(NAMESPACE_REGEX)
    for namespace in value:
        if not pattern.match(namespace):
            raise ValueError("Invalid namespace format")
    return value

JobNamespaces = Annotated[List[str], AfterValidator(validate_namespaces)]