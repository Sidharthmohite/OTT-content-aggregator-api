from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.models.genre import Genre
from src.schemas.genre import GenreCreate, GenreUpdate


class DuplicateGenreError(Exception):
    pass


def get_genres(db: Session):
    return db.query(Genre).order_by(Genre.name, Genre.id).all()


def get_genre(db: Session, genre_id: int):
    return db.get(Genre, genre_id)


def _ensure_unique_name(db: Session, name: str, exclude_id=None):
    query = db.query(Genre).filter(Genre.name == name)
    if exclude_id is not None:
        query = query.filter(Genre.id != exclude_id)

    if query.first() is not None:
        raise DuplicateGenreError("A genre with this name already exists.")


def _commit_genre(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        original = exc.orig
        diagnostic = getattr(original, "diag", None)
        sqlstate = getattr(original, "sqlstate", None)
        constraint = getattr(diagnostic, "constraint_name", None)
        message = str(original)

        postgres_duplicate = (
            sqlstate == "23505"
            and constraint in {"genres_name_key", "ix_genres_name"}
        )
        sqlite_duplicate = (
            "UNIQUE constraint failed: genres.name" in message
        )

        if postgres_duplicate or sqlite_duplicate:
            raise DuplicateGenreError(
                "A genre with this name already exists."
            ) from exc
        raise


def create_genre(db: Session, genre_data: GenreCreate):
    _ensure_unique_name(db, genre_data.name)
    genre = Genre(**genre_data.model_dump())
    db.add(genre)
    _commit_genre(db)
    db.refresh(genre)
    return genre


def update_genre(db: Session, genre_id: int, genre_data: GenreUpdate):
    genre = get_genre(db, genre_id)
    if genre is None:
        return None

    changes = genre_data.model_dump(exclude_unset=True)
    if "name" in changes:
        _ensure_unique_name(db, changes["name"], exclude_id=genre_id)
    for field, value in changes.items():
        setattr(genre, field, value)

    _commit_genre(db)
    db.refresh(genre)
    return genre


def delete_genre(db: Session, genre_id: int):
    genre = get_genre(db, genre_id)
    if genre is None:
        return False

    # Remove title links while keeping the associated titles.
    genre.titles.clear()
    db.delete(genre)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return True