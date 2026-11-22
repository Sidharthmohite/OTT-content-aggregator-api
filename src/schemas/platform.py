from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class PlatformCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    website_url: HttpUrl | None = None
    description: str | None = None


class PlatformUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    website_url: HttpUrl | None = None
    description: str | None = None


class PlatformResponse(BaseModel):
    id: int
    name: str
    website_url: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)