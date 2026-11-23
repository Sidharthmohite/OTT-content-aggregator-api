from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.platform import PlatformCreate, PlatformResponse, PlatformUpdate
from src.services import platform_service


router = APIRouter(prefix="/platforms", tags=["OTT Platforms"])


@router.get("/", response_model=list[PlatformResponse])
def read_platforms(db: Session = Depends(get_db)):
    return platform_service.get_platforms(db)


@router.get(
    "/{platform_id}",
    response_model=PlatformResponse,
    responses={404: {"description": "Platform not found"}},
)
def read_platform(platform_id: int, db: Session = Depends(get_db)):
    platform = platform_service.get_platform(db, platform_id)
    if platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform


@router.post(
    "/",
    response_model=PlatformResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Platform name already exists"}},
)
def create_platform(
    platform_data: PlatformCreate,
    db: Session = Depends(get_db),
):
    try:
        return platform_service.create_platform(db, platform_data)
    except (platform_service.DuplicatePlatformError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch(
    "/{platform_id}",
    response_model=PlatformResponse,
    responses={
        404: {"description": "Platform not found"},
        409: {"description": "Platform name already exists"},
    },
)
def update_platform(
    platform_id: int,
    platform_data: PlatformUpdate,
    db: Session = Depends(get_db),
):
    try:
        platform = platform_service.update_platform(
            db, platform_id, platform_data
        )
    except (platform_service.DuplicatePlatformError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform


@router.delete(
    "/{platform_id}",
    responses={404: {"description": "Platform not found"}},
)
def delete_platform(platform_id: int, db: Session = Depends(get_db)):
    if not platform_service.delete_platform(db, platform_id):
        raise HTTPException(status_code=404, detail="Platform not found")
    return {"message": "Platform deleted successfully"}