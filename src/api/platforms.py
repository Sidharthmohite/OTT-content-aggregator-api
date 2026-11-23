from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.platform import PlatformCreate, PlatformResponse
from src.services import platform_service


router = APIRouter(prefix="/platforms", tags=["OTT Platforms"])


@router.get("/", response_model=list[PlatformResponse])
def read_platforms(db: Session = Depends(get_db)):
    return platform_service.get_platforms(db)


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
    except platform_service.DuplicatePlatformError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
