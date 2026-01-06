from pydantic import BaseModel, Field
from config.constants.jobs import USERNAME_REGEX, PASSWORD_REGEX


class BasicAuth(BaseModel):
    username: str = Field(..., pattern=USERNAME_REGEX)
    password: str = Field(..., pattern=PASSWORD_REGEX)
