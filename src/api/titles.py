from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.title import TitleCreate, TitleResponse, TitleUpdate
from src.services import catalog_service


router = APIRouter(
    prefix="/titles",
    tags=["Titles"],
)


@router.get("/", response_model=list[TitleResponse])
def read_titles(db: Session = Depends(get_db)):
    return catalog_service.get_titles(db)


@router.get(
    "/{title_id}",
    response_model=TitleResponse,
    responses={
        404: {"description": "Title not found"},
    },
)
def read_title(
    title_id: int,
    db: Session = Depends(get_db),
):
    title = catalog_service.get_title(db, title_id)

    if title is None:
        raise HTTPException(status_code=404, detail="Title not found")

    return title


@router.post(
    "/",
    response_model=TitleResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Duplicate title identity"},
    },
)
def create_title(
    title_data: TitleCreate,
    db: Session = Depends(get_db),
):
    try:
        return catalog_service.create_title(db, title_data)
    except catalog_service.DuplicateTitleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch(
    "/{title_id}",
    response_model=TitleResponse,
    responses={
        404: {"description": "Title not found"},
        409: {"description": "Duplicate title identity"},
    },
)
def update_title(
    title_id: int,
    title_data: TitleUpdate,
    db: Session = Depends(get_db),
):
    try:
        title = catalog_service.update_title(db, title_id, title_data)
    except catalog_service.DuplicateTitleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValidationError as exc:
        errors = [
            {**error, "loc": ("body", *error["loc"])}
            for error in exc.errors()
        ]
        raise RequestValidationError(errors) from exc

    if title is None:
        raise HTTPException(status_code=404, detail="Title not found")

    return title


@router.delete(
    "/{title_id}",
    responses={
        404: {"description": "Title not found"},
    },
)
def delete_title(
    title_id: int,
    db: Session = Depends(get_db),
):
    deleted = catalog_service.delete_title(db, title_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Title not found")

    return {"message": "Title deleted successfully"}