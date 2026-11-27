from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_year: int = Field(..., ge=1888, le=2100)
    language: str = Field(..., min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(default=None, gt=0)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(default=None, ge=1888, le=2100)
    language: Optional[str] = Field(default=None, min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(default=None, gt=0)


class MovieResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    release_year: int
    language: str
    duration_minutes: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
