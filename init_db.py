from config.database import engine
from models.news import Base


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("SQLite база даних створена (news.db)")