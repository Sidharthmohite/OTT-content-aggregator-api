from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.platform import PlatformCreate, PlatformUpdate, PlatformResponse
from src.services import platform_service

router = APIRouter(
    prefix="/platforms",
    tags=["Platforms"],
)


@router.get("/", response_model=list[PlatformResponse])
def read_platforms(db: Session = Depends(get_db)):
    return platform_service.get_platforms(db)


@router.get("/{platform_id}", response_model=PlatformResponse)
def read_platform(platform_id: int, db: Session = Depends(get_db)):
    platform = platform_service.get_platform(db, platform_id)

    if platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")

    return platform


@router.post("/", response_model=PlatformResponse, status_code=201)
def create_platform(
    platform_data: PlatformCreate,
    db: Session = Depends(get_db),
):
    try:
        return platform_service.create_platform(db, platform_data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{platform_id}", response_model=PlatformResponse)
def update_platform(
    platform_id: int,
    platform_data: PlatformUpdate,
    db: Session = Depends(get_db),
):
    try:
        platform = platform_service.update_platform(
            db, platform_id, platform_data
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")

    return platform


@router.delete("/{platform_id}")
def delete_platform(platform_id: int, db: Session = Depends(get_db)):
    deleted = platform_service.delete_platform(db, platform_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Platform not found")

    return {"message": "Platform deleted successfully"}