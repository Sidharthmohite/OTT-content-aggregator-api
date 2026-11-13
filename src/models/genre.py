from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.models.associations import title_genres


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    titles = relationship(
        "Title",
        secondary=title_genres,
        back_populates="genres"
    )

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"
