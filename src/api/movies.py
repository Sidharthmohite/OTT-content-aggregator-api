from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.movie import MovieCreate, MovieUpdate, MovieResponse
from src.services import movie_service


router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get("/", response_model=list[MovieResponse])
def read_movies(db: Session = Depends(get_db)):
    return movie_service.get_movies(db)


@router.get("/{movie_id}", response_model=MovieResponse)
def read_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    movie = movie_service.get_movie(db, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return movie


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED
)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db)
):
    movie = movie_service.create_movie(db, movie_data)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie already exists"
        )

    return movie


@router.patch("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db)
):
    movie = movie_service.update_movie(
        db, movie_id, movie_data
    )

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    if movie == "duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Movie already exists"
        )

    return movie


@router.delete("/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    deleted = movie_service.delete_movie(db, movie_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return {"message": "Movie deleted successfully"}
