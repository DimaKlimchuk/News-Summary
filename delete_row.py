from datetime import date
from db.database import SessionLocal
from db.models import News

def delete_news_by_date(target_date):
    session = SessionLocal()
    try:
        deleted_rows = session.query(News).filter(News.Date == target_date).delete()
        session.commit()
        print(f"🗑️ Видалено {deleted_rows} записів за {target_date}")
    except Exception as e:
        session.rollback()
        print("Помилка під час видалення:", e)
    finally:
        session.close()

delete_news_by_date(date(2025, 6, 1))
