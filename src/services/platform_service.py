from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.platform import Platform
from src.schemas.platform import PlatformCreate, PlatformUpdate


def get_platforms(db: Session):
    return db.query(Platform).order_by(Platform.name).all()


def get_platform(db: Session, platform_id: int):
    return db.query(Platform).filter(Platform.id == platform_id).first()


def create_platform(db: Session, platform_data: PlatformCreate):
    data = platform_data.model_dump()

    if data.get("website_url") is not None:
        data["website_url"] = str(data["website_url"])

    platform = Platform(**data)
    db.add(platform)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Platform already exists")

    db.refresh(platform)
    return platform


def update_platform(
    db: Session,
    platform_id: int,
    platform_data: PlatformUpdate,
):
    platform = get_platform(db, platform_id)

    if platform is None:
        return None

    changes = platform_data.model_dump(exclude_unset=True)

    if changes.get("website_url") is not None:
        changes["website_url"] = str(changes["website_url"])

    for field, value in changes.items():
        setattr(platform, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Platform already exists")

    db.refresh(platform)
    return platform


def delete_platform(db: Session, platform_id: int):
    platform = get_platform(db, platform_id)

    if platform is None:
        return False

    db.delete(platform)
    db.commit()
    return True