from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.genre import GenreCreate, GenreResponse
from src.services import genre_service


router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/", response_model=list[GenreResponse])
def read_genres(db: Session = Depends(get_db)):
    return genre_service.get_genres(db)


@router.post(
    "/",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Genre name already exists"}},
)
def create_genre(
    genre_data: GenreCreate,
    db: Session = Depends(get_db),
):
    try:
        return genre_service.create_genre(db, genre_data)
    except genre_service.DuplicateGenreError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
