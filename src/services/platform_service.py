from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.platform import Platform
from src.schemas.platform import PlatformCreate, PlatformUpdate


class DuplicatePlatformError(Exception):
    pass


def get_platforms(db: Session):
    return db.query(Platform).order_by(Platform.name, Platform.id).all()


def get_platform(db: Session, platform_id: int):
    return db.get(Platform, platform_id)


def _ensure_unique_name(db: Session, name: str, exclude_id=None):
    query = db.query(Platform).filter(Platform.name == name)
    if exclude_id is not None:
        query = query.filter(Platform.id != exclude_id)

    if query.first() is not None:
        raise DuplicatePlatformError(
            "A platform with this name already exists."
        )


def _commit_platform(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        original = exc.orig
        diagnostic = getattr(original, "diag", None)
        sqlstate = getattr(original, "sqlstate", None)
        constraint = getattr(diagnostic, "constraint_name", None)

        postgres_duplicate = (
            sqlstate == "23505"
            and constraint in {"platforms_name_key", "ix_platforms_name"}
        )
        sqlite_duplicate = (
            "UNIQUE constraint failed: platforms.name" in str(original)
        )

        if postgres_duplicate or sqlite_duplicate:
            raise DuplicatePlatformError(
                "A platform with this name already exists."
            ) from exc
        raise


def create_platform(db: Session, platform_data: PlatformCreate):
    _ensure_unique_name(db, platform_data.name)
    data = platform_data.model_dump(mode="json")

    platform = Platform(**data)
    db.add(platform)
    _commit_platform(db)
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

    changes = platform_data.model_dump(
        exclude_unset=True,
        mode="json",
    )

    if "name" in changes:
        _ensure_unique_name(
            db, changes["name"], exclude_id=platform_id
        )

    for field, value in changes.items():
        setattr(platform, field, value)

    _commit_platform(db)
    db.refresh(platform)
    return platform


def delete_platform(db: Session, platform_id: int):
    platform = get_platform(db, platform_id)
    if platform is None:
        return False

    # Remove title links while preserving the titles.
    platform.titles.clear()
    db.delete(platform)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return True
