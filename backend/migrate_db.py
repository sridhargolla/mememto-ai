"""
Database migration script to add new fields to Memory table.
Run this script to update existing databases with new columns:
- embedding (BLOB)
- metadata (TEXT)
- source_document (String)
- memory_type (String)
- importance (String)
- entities_people (TEXT)
- entities_organizations (TEXT)
- entities_locations (TEXT)
- entities_skills (TEXT)
- time_start (String)
- time_end (String)
- source_documents (TEXT)
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "./memento.db")


def migrate_database():
    """Add new columns to the memories table if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        if not cursor.fetchone():
            print("Memories table does not exist. Run the application first to create it.")
            return
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(memories)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Add embedding column if it doesn't exist
        if 'embedding' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN embedding BLOB")
            print("Added 'embedding' column")
        else:
            print("'embedding' column already exists")
        
        # Add metadata column if it doesn't exist
        if 'metadata' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN metadata TEXT")
            print("Added 'metadata' column")
        else:
            print("'metadata' column already exists")
        
        # Add source_document column if it doesn't exist
        if 'source_document' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN source_document VARCHAR(500)")
            print("Added 'source_document' column")
        else:
            print("'source_document' column already exists")
        
        # Add memory_type column if it doesn't exist
        if 'memory_type' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN memory_type VARCHAR(50)")
            print("Added 'memory_type' column")
        else:
            print("'memory_type' column already exists")
        
        # Add importance column if it doesn't exist
        if 'importance' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN importance VARCHAR(20)")
            print("Added 'importance' column")
        else:
            print("'importance' column already exists")
        
        # Add entities_people column if it doesn't exist
        if 'entities_people' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN entities_people TEXT")
            print("Added 'entities_people' column")
        else:
            print("'entities_people' column already exists")
        
        # Add entities_organizations column if it doesn't exist
        if 'entities_organizations' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN entities_organizations TEXT")
            print("Added 'entities_organizations' column")
        else:
            print("'entities_organizations' column already exists")
        
        # Add entities_locations column if it doesn't exist
        if 'entities_locations' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN entities_locations TEXT")
            print("Added 'entities_locations' column")
        else:
            print("'entities_locations' column already exists")
        
        # Add entities_skills column if it doesn't exist
        if 'entities_skills' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN entities_skills TEXT")
            print("Added 'entities_skills' column")
        else:
            print("'entities_skills' column already exists")
        
        # Add time_start column if it doesn't exist
        if 'time_start' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN time_start VARCHAR(100)")
            print("Added 'time_start' column")
        else:
            print("'time_start' column already exists")
        
        # Add time_end column if it doesn't exist
        if 'time_end' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN time_end VARCHAR(100)")
            print("Added 'time_end' column")
        else:
            print("'time_end' column already exists")
        
        # Add source_documents column if it doesn't exist
        if 'source_documents' not in existing_columns:
            cursor.execute("ALTER TABLE memories ADD COLUMN source_documents TEXT")
            print("Added 'source_documents' column")
        else:
            print("'source_documents' column already exists")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
