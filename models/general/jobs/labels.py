import re
from pydantic import AfterValidator
from typing import Annotated, Dict
from config.constants.jobs import LABEL_REGEX, LABEL_VALUE_REGEX, FORBIDDEN_LABELS


def validate_labels(v: Dict[str, str]) -> Dict[str, str]:
    key_pattern = re.compile(LABEL_REGEX)
    value_pattern = re.compile(LABEL_VALUE_REGEX)

    if v:
        for key, value in v.items():
            if key in FORBIDDEN_LABELS:
                raise ValueError(f"Forbidden label: {key}")
            if not key_pattern.match(key):
                raise ValueError(f"Invalid label key: {key}")
            if not value_pattern.match(value):
                raise ValueError(f"Invalid label value: {value}")
    return v


JobLabels = Annotated[Dict[str, str], AfterValidator(validate_labels)]