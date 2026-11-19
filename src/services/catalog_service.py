from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.title import Title
from src.schemas.title import TitleCreate, TitleUpdate


def get_titles(db: Session):
    return db.query(Title).all()


def get_title(db: Session, title_id: int):
    return db.query(Title).filter(Title.id == title_id).first()


def create_title(db: Session, title_data: TitleCreate):
    new_title = Title(**title_data.model_dump())

    db.add(new_title)
    commit_title(db)
    db.refresh(new_title)

    return new_title


def update_title(
    db: Session,
    title_id: int,
    title_data: TitleUpdate,
):
    title = get_title(db, title_id)

    if title is None:
        return None

    changes = title_data.model_dump(exclude_unset=True)

    current_data = {
        field: getattr(title, field)
        for field in TitleCreate.model_fields
    }

    validated = TitleCreate.model_validate({
        **current_data,
        **changes,
    })

    for field in changes:
        setattr(title, field, getattr(validated, field))

    commit_title(db)
    db.refresh(title)

    return title


def delete_title(db: Session, title_id: int):
    title = get_title(db, title_id)

    if title is None:
        return False

    db.delete(title)
    db.commit()

    return True
class DuplicateTitleError(Exception):
    pass


def commit_title(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        constraint_name = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )
        sqlite_duplicate = (
            "UNIQUE constraint failed: titles.title, "
            "titles.content_type, titles.release_year, titles.language"
        )

        if (
            constraint_name == "uq_titles_identity"
            or sqlite_duplicate in str(exc.orig)
        ):
            raise DuplicateTitleError(
                "A title with the same name, content type, "
                "release year, and language already exists."
            ) from exc

        raise