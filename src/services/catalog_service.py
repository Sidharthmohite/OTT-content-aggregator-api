from sqlalchemy.orm import Session

from src.models.title import Title
from src.schemas.title import TitleCreate, TitleUpdate


def get_titles(db: Session):
    return db.query(Title).all()


def get_title(db: Session, title_id: int):
    return db.query(Title).filter(Title.id == title_id).first()


def create_title(db: Session, title_data: TitleCreate):
    new_title = Title(**title_data.model_dump())

    db.add(new_title)
    db.commit()
    db.refresh(new_title)

    return new_title


def update_title(
    db: Session,
    title_id: int,
    title_data: TitleUpdate
):
    title = get_title(db, title_id)

    if title is None:
        return None

    update_data = title_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(title, key, value)

    db.commit()
    db.refresh(title)

    return title


def delete_title(db: Session, title_id: int):
    title = get_title(db, title_id)

    if title is None:
        return False

    db.delete(title)
    db.commit()

    return True
