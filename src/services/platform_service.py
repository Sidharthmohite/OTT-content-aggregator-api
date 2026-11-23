from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.platform import Platform
from src.schemas.platform import PlatformCreate


class DuplicatePlatformError(Exception):
    pass


def get_platforms(db: Session):
    return db.query(Platform).order_by(Platform.name, Platform.id).all()


def create_platform(db: Session, platform_data: PlatformCreate):
    existing = db.query(Platform).filter(
        Platform.name == platform_data.name
    ).first()

    if existing is not None:
        raise DuplicatePlatformError(
            "A platform with this name already exists."
        )

    data = platform_data.model_dump()
    if data["website_url"] is not None:
        data["website_url"] = str(data["website_url"])

    platform = Platform(**data)
    db.add(platform)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        existing = db.query(Platform).filter(
            Platform.name == platform_data.name
        ).first()

        if existing is not None:
            raise DuplicatePlatformError(
                "A platform with this name already exists."
            ) from exc

        raise

    db.refresh(platform)
    return platform
