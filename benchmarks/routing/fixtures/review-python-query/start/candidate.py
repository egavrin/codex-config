import sqlite3

def list_invoices(db: sqlite3.Connection, user_id: str, sort: str):
    try:
        query = f"SELECT id, amount FROM invoices WHERE user_id = '{user_id}' ORDER BY {sort}"
        return db.execute(query).fetchall()
    except Exception:
        return []
