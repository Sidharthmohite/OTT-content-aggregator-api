from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.genre import Genre
from src.schemas.genre import GenreCreate, GenreUpdate


def get_genres(db: Session):
    return db.query(Genre).order_by(Genre.name).all()


def get_genre(db: Session, genre_id: int):
    return db.query(Genre).filter(Genre.id == genre_id).first()


def create_genre(db: Session, genre_data: GenreCreate):
    genre = Genre(**genre_data.model_dump())
    db.add(genre)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Genre already exists")

    db.refresh(genre)
    return genre


def update_genre(db: Session, genre_id: int, genre_data: GenreUpdate):
    genre = get_genre(db, genre_id)

    if genre is None:
        return None

    changes = genre_data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(genre, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Genre already exists")

    db.refresh(genre)
    return genre


def delete_genre(db: Session, genre_id: int):
    genre = get_genre(db, genre_id)

    if genre is None:
        return False

    db.delete(genre)
    db.commit()
    return True