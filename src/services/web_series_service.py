from sqlalchemy.orm import Session

from src.models.web_series import WebSeries
from src.schemas.web_series import WebSeriesCreate, WebSeriesUpdate


def get_web_series_list(db: Session):
    return db.query(WebSeries).all()


def get_web_series(db: Session, series_id: int):
    return db.query(WebSeries).filter(
        WebSeries.id == series_id
    ).first()


def is_duplicate_web_series(
    db: Session,
    title: str,
    release_year: int,
    language: str,
    exclude_id: int = None
):
    query = db.query(WebSeries).filter(
        WebSeries.title.ilike(title.strip()),
        WebSeries.release_year == release_year,
        WebSeries.language.ilike(language.strip())
    )

    if exclude_id is not None:
        query = query.filter(WebSeries.id != exclude_id)

    return query.first() is not None


def create_web_series(db: Session, series_data: WebSeriesCreate):
    if is_duplicate_web_series(
        db,
        series_data.title,
        series_data.release_year,
        series_data.language
    ):
        return None

    new_series = WebSeries(**series_data.model_dump())

    db.add(new_series)
    db.commit()
    db.refresh(new_series)

    return new_series


def update_web_series(
    db: Session,
    series_id: int,
    series_data: WebSeriesUpdate
):
    series = get_web_series(db, series_id)

    if series is None:
        return None

    update_data = series_data.model_dump(exclude_unset=True)

    new_title = update_data.get("title", series.title)
    new_year = update_data.get("release_year", series.release_year)
    new_language = update_data.get("language", series.language)

    if is_duplicate_web_series(
        db,
        new_title,
        new_year,
        new_language,
        exclude_id=series_id
    ):
        return "duplicate"

    for key, value in update_data.items():
        setattr(series, key, value)

    db.commit()
    db.refresh(series)

    return series


def delete_web_series(db: Session, series_id: int):
    series = get_web_series(db, series_id)

    if series is None:
        return False

    db.delete(series)
    db.commit()

    return True
