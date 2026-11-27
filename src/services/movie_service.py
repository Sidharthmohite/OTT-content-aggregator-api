from sqlalchemy.orm import Session

from src.models.movie import Movie
from src.schemas.movie import MovieCreate, MovieUpdate


def get_movies(db: Session):
    return db.query(Movie).all()


def get_movie(db: Session, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first()


def is_duplicate_movie(
    db: Session,
    title: str,
    release_year: int,
    language: str,
    exclude_id: int = None
):
    query = db.query(Movie).filter(
        Movie.title.ilike(title.strip()),
        Movie.release_year == release_year,
        Movie.language.ilike(language.strip())
    )

    if exclude_id is not None:
        query = query.filter(Movie.id != exclude_id)

    return query.first() is not None


def create_movie(db: Session, movie_data: MovieCreate):
    if is_duplicate_movie(
        db,
        movie_data.title,
        movie_data.release_year,
        movie_data.language
    ):
        return None

    new_movie = Movie(**movie_data.model_dump())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie


def update_movie(db: Session, movie_id: int, movie_data: MovieUpdate):
    movie = get_movie(db, movie_id)

    if movie is None:
        return None

    update_data = movie_data.model_dump(exclude_unset=True)
    new_title = update_data.get("title", movie.title)
    new_year = update_data.get("release_year", movie.release_year)
    new_language = update_data.get("language", movie.language)

    if is_duplicate_movie(
        db, new_title, new_year, new_language, exclude_id=movie_id
    ):
        return "duplicate"

    for key, value in update_data.items():
        setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie_id: int):
    movie = get_movie(db, movie_id)

    if movie is None:
        return False

    db.delete(movie)
    db.commit()
    return True
