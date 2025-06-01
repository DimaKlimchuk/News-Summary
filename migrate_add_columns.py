import sqlite3

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def add_column_if_missing(cursor, table, column, column_type, default_value="''"):
    if not column_exists(cursor, table, column):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type} DEFAULT {default_value}")
        print(f"✅ Додано колонку {column}")
    else:
        print(f"ℹ️ Колонка {column} вже існує")

if __name__ == "__main__":
    conn = sqlite3.connect("news_db.sqlite")
    cursor = conn.cursor()
    add_column_if_missing(cursor, "news", "Link", "TEXT", "''")  # додаємо колонку Link

    conn.commit()
    conn.close()
    print("🔄 Міграція завершена.")
