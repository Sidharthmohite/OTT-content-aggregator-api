from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from src.core.database import Base


class WebSeries(Base):
    __tablename__ = "web_series"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    release_year = Column(Integer, nullable=False)
    language = Column(String(100), nullable=False)
    number_of_seasons = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
