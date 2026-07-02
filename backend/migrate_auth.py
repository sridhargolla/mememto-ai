"""
Database migration script for adding authentication support.

This script:
1. Initializes the database (creates tables if they don't exist)
2. Creates the users table
3. Adds user_id columns to memories and conversations tables
4. Creates a default admin user
5. Migrates existing data to the default user
"""

import os
import sqlite3

import bcrypt

from database import init_db

DATABASE_PATH = os.getenv("DATABASE_PATH", "./memento.db")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # bcrypt requires bytes
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def migrate():
    """Run the database migration."""
    # Initialize database first (creates tables if they don't exist)
    print("Initializing database...")
    init_db()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        print("Starting authentication migration...")

        # 1. Create users table
        print("Creating users table...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create index on email
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email)
        """
        )

        # 2. Add user_id column to memories table
        print("Adding user_id to memories table...")
        cursor.execute("PRAGMA table_info(memories)")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in columns:
            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN user_id INTEGER
            """
            )
            cursor.execute(
                """
                CREATE INDEX idx_memories_user_id
                ON memories(user_id)
            """
            )
            print("  - user_id column added to memories")
        else:
            print("  - user_id column already exists in memories")

        # 3. Add user_id column to conversations table
        print("Adding user_id to conversations table...")
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in columns:
            cursor.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN user_id INTEGER
            """
            )
            cursor.execute(
                """
                CREATE INDEX idx_conversations_user_id
                ON conversations(user_id)
            """
            )
            print("  - user_id column added to conversations")
        else:
            print("  - user_id column already exists in conversations")

        # 4. Create default admin user
        print("Creating default admin user...")
        default_password = "admin123"
        password_hash = hash_password(default_password)

        cursor.execute(
            """
            INSERT OR IGNORE INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """,
            ("Admin", "admin@memento.local", password_hash),
        )

        conn.commit()

        # Get the admin user ID
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@memento.local",))
        admin_id = cursor.fetchone()[0]
        print(f"  - Default admin user created (ID: {admin_id})")
        print("  - Email: admin@memento.local")
        print(f"  - Password: {default_password}")
        print("  - IMPORTANT: Change this password after first login!")

        # 5. Migrate existing memories to admin user
        print("Migrating existing memories to admin user...")
        cursor.execute("UPDATE memories SET user_id = ? WHERE user_id IS NULL", (admin_id,))
        memories_updated = cursor.rowcount
        print(f"  - {memories_updated} memories migrated")

        # 6. Migrate existing conversations to admin user
        print("Migrating existing conversations to admin user...")
        cursor.execute("UPDATE conversations SET user_id = ? WHERE user_id IS NULL", (admin_id,))
        conversations_updated = cursor.rowcount
        print(f"  - {conversations_updated} conversations migrated")

        conn.commit()

        print("\n✅ Migration completed successfully!")
        print(f"\nDatabase: {DATABASE_PATH}")
        print(f"Admin user ID: {admin_id}")
        print(f"Memories migrated: {memories_updated}")
        print(f"Conversations migrated: {conversations_updated}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
