import sqlite3
import os

# -----------------------------------------
# CREATE SAFE DATABASE LOCATION (AppData)
# -----------------------------------------

APP_NAME = "E-Diary"

app_folder = os.path.join(os.getenv("LOCALAPPDATA"), APP_NAME)

if not os.path.exists(app_folder):
    os.makedirs(app_folder)

db_path = os.path.join(app_folder, "mini_diary.db")


# -----------------------------------------
# CONNECT DATABASE
# -----------------------------------------

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()


# -----------------------------------------
# CREATE TABLES
# -----------------------------------------

def create_tables():

    # Diary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary (
            date TEXT PRIMARY KEY,
            content TEXT
        )
    """)

    # To-Do table (linked with date)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            date TEXT,
            priority TEXT,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()


create_tables()


# =========================================
# DIARY FUNCTIONS
# =========================================

def save_entry(date, content):
    cursor.execute("""
        INSERT INTO diary(date, content)
        VALUES (?, ?)
        ON CONFLICT(date)
        DO UPDATE SET content=excluded.content
    """, (date, content))

    conn.commit()


def get_entry(date):
    cursor.execute("SELECT content FROM diary WHERE date=?", (date,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return ""


# =========================================
# TODO FUNCTIONS (DATE SPECIFIC)
# =========================================

def add_task_with_date(task, date, priority="Medium"):
    cursor.execute("""
        INSERT INTO todo(task, date, priority)
        VALUES (?, ?, ?)
    """, (task, date, priority))

    conn.commit()


def get_tasks_by_date(date):
    cursor.execute("""
        SELECT id, task, priority, completed
        FROM todo
        WHERE date=?
        ORDER BY completed, id DESC
    """, (date,))

    return cursor.fetchall()


def complete_task(task_id):
    cursor.execute("""
        UPDATE todo
        SET completed = 1
        WHERE id=?
    """, (task_id,))

    conn.commit()


def delete_task(task_id):
    cursor.execute("""
        DELETE FROM todo
        WHERE id=?
    """, (task_id,))

    conn.commit()
