from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, News
import os

DB_PATH = os.getenv("SQLITE_DB_PATH", "news_db.sqlite")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def create_database():
    Base.metadata.create_all(bind=engine)

def insert_news_batch(df):
    session = SessionLocal()
    try:
        for _, row in df.iterrows():
            title = row.get("Title")
            date = row.get("Date")

            exists = session.query(News).filter_by(Title=title, Date=date).first()
            if exists:
                continue 

            news_item = News(
                Source=row.get("Source"),
                Title=title,
                Text=row.get("Text"),
                Date=date,
                Cluster=row.get("Cluster"),
                Theme=row.get("Theme"),
                Sentiment=row.get("Sentiment"),
                Summary=row.get("Summary"),
                Category=row.get("Category"),
                Verificated=row.get("Verificated", False), 
                Sources=row.get("Sources", ""),
                Link=row.get("Link") 
            )
            session.add(news_item)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Помилка при збереженні:", e)
    finally:
        session.close()
