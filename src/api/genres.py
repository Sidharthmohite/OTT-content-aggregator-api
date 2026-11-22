from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.genre import GenreCreate, GenreUpdate, GenreResponse
from src.services import genre_service

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/", response_model=list[GenreResponse])
def read_genres(db: Session = Depends(get_db)):
    return genre_service.get_genres(db)


@router.get("/{genre_id}", response_model=GenreResponse)
def read_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = genre_service.get_genre(db, genre_id)
    if genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("/", response_model=GenreResponse, status_code=201)
def create_genre(genre_data: GenreCreate, db: Session = Depends(get_db)):
    try:
        return genre_service.create_genre(db, genre_data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{genre_id}", response_model=GenreResponse)
def update_genre(
    genre_id: int,
    genre_data: GenreUpdate,
    db: Session = Depends(get_db),
):
    try:
        genre = genre_service.update_genre(db, genre_id, genre_data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.delete("/{genre_id}")
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    if not genre_service.delete_genre(db, genre_id):
        raise HTTPException(status_code=404, detail="Genre not found")
    return {"message": "Genre deleted successfully"}