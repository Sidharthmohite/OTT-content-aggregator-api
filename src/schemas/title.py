
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class TitleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: Literal["movie", "web_series"]
    release_year: int = Field(..., ge=1888, le=2100)
    language: str
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    number_of_seasons: Optional[int] = Field(default=None, gt=0)


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
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    content_type: Optional[Literal["movie", "web_series"]] = None
    release_year: Optional[int] = Field(default=None, ge=1888, le=2100)
    language: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    number_of_seasons: Optional[int] = Field(default=None, gt=0)

