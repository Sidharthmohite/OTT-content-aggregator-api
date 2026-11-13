from sqlalchemy import Table, Column, Integer, ForeignKey

from src.core.database import Base


# Connects Titles with Genres
title_genres = Table(
    "title_genres",
    Base.metadata,
    Column("title_id", Integer, ForeignKey("titles.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True)
)


# Connects Titles with OTT Platforms
title_platforms = Table(
    "title_platforms",
    Base.metadata,
    Column("title_id", Integer, ForeignKey("titles.id"), primary_key=True),
    Column("platform_id", Integer, ForeignKey("platforms.id"), primary_key=True)
)
