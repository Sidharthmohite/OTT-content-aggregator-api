from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.models.associations import title_genres, title_platforms


class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False, index=True)

    description = Column(Text, nullable=True)

    content_type = Column(String(20), nullable=False)

    release_year = Column(Integer, nullable=False)

    language = Column(String(100), nullable=False)

    duration_minutes = Column(Integer, nullable=True)

    number_of_seasons = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "content_type IN ('movie', 'web_series')",
            name="check_content_type"
        ),
    )

    genres = relationship(
        "Genre",
        secondary=title_genres,
        back_populates="titles"
    )

    platforms = relationship(
        "Platform",
        secondary=title_platforms,
        back_populates="titles"
    )
