"""
Migration script to add preferred_language field to users table.
This script adds the preferred_language column with default value 'en'.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "memento.db"


def migrate():
    """Add preferred_language column to users table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if preferred_language column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if "preferred_language" in columns:
            print("Column 'preferred_language' already exists in users table.")
            return

        # Add the preferred_language column
        alter_query = """
            ALTER TABLE users
            ADD COLUMN preferred_language VARCHAR(10) NOT NULL DEFAULT 'en'
        """
        cursor.execute(alter_query)
        conn.commit()
        print("Successfully added 'preferred_language' column to users table.")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
