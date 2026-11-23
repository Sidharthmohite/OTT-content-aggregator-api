from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PlatformCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    website_url: Optional[HttpUrl] = Field(default=None, max_length=500)
    description: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class PlatformUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    website_url: Optional[HttpUrl] = Field(default=None, max_length=500)
    description: Optional[str] = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            raise ValueError("Name must not be null")
        if isinstance(value, str):
            return value.strip()
        return value


class PlatformResponse(BaseModel):
    id: int
    name: str
    website_url: Optional[str]
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)
