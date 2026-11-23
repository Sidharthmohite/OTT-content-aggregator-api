from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GenreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class GenreUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            raise ValueError("Name must not be null")
        if isinstance(value, str):
            return value.strip()
        return value


class GenreResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)
