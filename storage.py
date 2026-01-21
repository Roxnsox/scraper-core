import sqlite3
from typing import List, Dict, Any

DB_FILENAME = "realgm_stats.db"
TABLE_NAME = "realgm_stats"

def create_table_if_not_exists(conn: sqlite3.Connection, sample_row: Dict[str, Any]) -> None:
    """
    Create a table in the database with columns based on the keys of the sample_row dictionary.
    If the table already exists, this function does nothing.

    Args:
        conn: The SQLite connection object.
        sample_row: A dictionary representing a normalized data row.
    """
    def get_column_type(value: Any) -> str:
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        else:
            return "TEXT"

    columns = ", ".join(f'"{key}" {get_column_type(value)}' for key, value in sample_row.items())
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {columns}
    );
    """
    conn.execute(create_table_sql)
    conn.commit()

def insert_rows(rows: List[Dict[str, Any]]) -> None:
    """
    Insert multiple normalized rows into the database.

    Args:
        rows: A list of dictionaries, each representing a normalized data row.
    """
    if not rows:
        return

    conn = sqlite3.connect(DB_FILENAME)
    try:
        create_table_if_not_exists(conn, rows[0])

        keys = rows[0].keys()
        placeholders = ", ".join("?" for _ in keys)
        columns = ", ".join(f'"{key}"' for key in keys)
        insert_sql = f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})"

        values = [tuple(str(row[key]) if row[key] is not None else None for key in keys) for row in rows]
        conn.executemany(insert_sql, values)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    # Debug entry point to test inserting sample data
    sample_data = [
        {"player": "John Doe", "team": "Lakers", "points": "25", "assists": "5"},
        {"player": "Jane Smith", "team": "Heat", "points": "30", "assists": "7"},
    ]
    insert_rows(sample_data)
    print(f"Inserted {len(sample_data)} rows into {DB_FILENAME}.")
