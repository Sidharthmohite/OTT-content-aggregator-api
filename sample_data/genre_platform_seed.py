from src.core.database import SessionLocal
from src.models import Title, Genre, Platform


def seed_data():
    db = SessionLocal()

    try:
        # 1. Insert sample genres
        genre_data = {
            "Action": "Action-packed entertainment",
            "Comedy": "Humorous and entertaining content",
            "Drama": "Emotional storytelling",
            "Thriller": "Suspense and mystery",
            "Horror": "Scary and supernatural content",
            "Romance": "Love and relationships",
        }

        genres = {}

        for name, description in genre_data.items():
            genre = db.query(Genre).filter_by(name=name).first()

            if genre is None:
                genre = Genre(
                    name=name,
                    description=description
                )
                db.add(genre)

            genres[name] = genre

        # 2. Insert sample OTT platforms
        platform_data = {
            "Netflix": (
                "https://www.netflix.com",
                "Global streaming platform"
            ),
            "Amazon Prime Video": (
                "https://www.primevideo.com",
                "Amazon streaming service"
            ),
            "JioHotstar": (
                "https://www.jiohotstar.com",
                "Indian streaming platform"
            ),
        }

        platforms = {}

        for name, (url, description) in platform_data.items():
            platform = (
                db.query(Platform).filter_by(name=name).first()
            )

            if platform is None:
                platform = Platform(
                    name=name,
                    website_url=url,
                    description=description
                )
                db.add(platform)

            platforms[name] = platform

        db.flush()

        # 3. Connect existing titles with genres and platforms
        title_data = {
            "Inception": {
                "genres": ["Action", "Thriller"],
                "platforms": ["Netflix"],
            },
            "Stranger Things": {
                "genres": ["Drama", "Horror", "Thriller"],
                "platforms": ["Netflix"],
            },
        }

        for title_name, data in title_data.items():
            title = (
                db.query(Title)
                .filter_by(title=title_name)
                .first()
            )

            if title is None:
                print(f"Title not found: {title_name}")
                continue

            for genre_name in data["genres"]:
                genre = genres[genre_name]

                if genre not in title.genres:
                    title.genres.append(genre)

            for platform_name in data["platforms"]:
                platform = platforms[platform_name]

                if platform not in title.platforms:
                    title.platforms.append(platform)

        db.commit()
        print("Sample genres, platforms and relationships added!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
