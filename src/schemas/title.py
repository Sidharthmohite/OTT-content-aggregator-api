from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class TitleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: Literal["movie", "web_series"]
    release_year: int = Field(..., ge=1888, le=2100)
    language: str
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    number_of_seasons: Optional[int] = Field(default=None, gt=0)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Language must not be blank")
        return value

    @model_validator(mode="after")
    def validate_content_fields(self):
        if self.content_type == "movie" and self.number_of_seasons is not None:
            raise ValueError("Movies cannot have number_of_seasons")

        if self.content_type == "web_series" and self.duration_minutes is not None:
            raise ValueError("Web series cannot have duration_minutes")

        return self


class TitleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content_type: str
    release_year: int
    language: str
    duration_minutes: Optional[int]
    number_of_seasons: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TitleUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: Optional[str] = None
    content_type: Optional[Literal["movie", "web_series"]] = None
    release_year: Optional[int] = Field(default=None, ge=1888, le=2100)
    language: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    number_of_seasons: Optional[int] = Field(default=None, gt=0)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: Optional[str]) -> str:
        if value is None or not value.strip():
            raise ValueError("Language must not be blank")
        return value.strip()