from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.web_series import (
    WebSeriesCreate,
    WebSeriesUpdate,
    WebSeriesResponse
)
from src.services import web_series_service


router = APIRouter(
    prefix="/web-series",
    tags=["Web Series"]
)


@router.get("/", response_model=list[WebSeriesResponse])
def read_web_series_list(db: Session = Depends(get_db)):
    return web_series_service.get_web_series_list(db)


@router.get("/{series_id}", response_model=WebSeriesResponse)
def read_web_series(
    series_id: int,
    db: Session = Depends(get_db)
):
    series = web_series_service.get_web_series(db, series_id)

    if series is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web Series not found"
        )

    return series


@router.post(
    "/",
    response_model=WebSeriesResponse,
    status_code=status.HTTP_201_CREATED
)
def create_web_series(
    series_data: WebSeriesCreate,
    db: Session = Depends(get_db)
):
    series = web_series_service.create_web_series(db, series_data)

    if series is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Web Series already exists"
        )

    return series


@router.patch("/{series_id}", response_model=WebSeriesResponse)
def update_web_series(
    series_id: int,
    series_data: WebSeriesUpdate,
    db: Session = Depends(get_db)
):
    series = web_series_service.update_web_series(
        db, series_id, series_data
    )

    if series is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web Series not found"
        )

    if series == "duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Web Series already exists"
        )

    return series


@router.delete("/{series_id}")
def delete_web_series(
    series_id: int,
    db: Session = Depends(get_db)
):
    deleted = web_series_service.delete_web_series(db, series_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web Series not found"
        )

    return {"message": "Web Series deleted successfully"}
