from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.models.associations import title_platforms


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    website_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    titles = relationship(
        "Title",
        secondary=title_platforms,
        back_populates="platforms"
    )

    def __repr__(self):
        return f"<Platform(id={self.id}, name='{self.name}')>"
