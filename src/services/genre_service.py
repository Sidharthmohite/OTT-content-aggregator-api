from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.genre import Genre
from src.schemas.genre import GenreCreate


class DuplicateGenreError(Exception):
    pass


def get_genres(db: Session):
    return db.query(Genre).order_by(Genre.name, Genre.id).all()


def create_genre(db: Session, genre_data: GenreCreate):
    existing = db.query(Genre).filter(
        Genre.name == genre_data.name
    ).first()

    if existing is not None:
        raise DuplicateGenreError("A genre with this name already exists.")

    genre = Genre(**genre_data.model_dump())
    db.add(genre)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        existing = db.query(Genre).filter(
            Genre.name == genre_data.name
        ).first()

        if existing is not None:
            raise DuplicateGenreError(
                "A genre with this name already exists."
            ) from exc

        raise

    db.refresh(genre)
    return genre
