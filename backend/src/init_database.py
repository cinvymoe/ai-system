#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Database initialization script.

This script can be run independently to initialize the database
and create all necessary tables. It's useful for:
- Initial setup
- Database migrations
- Testing and development

Usage:
    python init_database.py
"""

import sys
from pathlib import Path

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, DATABASE_PATH, engine
from sqlalchemy import inspect


def check_database_exists():
    """Check if database file exists."""
    return DATABASE_PATH.exists()


def get_existing_tables():
    """Get list of existing tables in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def main():
    """Main initialization function."""
    print("=" * 60)
    print("Vision Security Database Initialization")
    print("=" * 60)
    
    db_exists = check_database_exists()
    
    if db_exists:
        print(f"\n✓ Database file found at: {DATABASE_PATH}")
        existing_tables = get_existing_tables()
        if existing_tables:
            print(f"✓ Existing tables: {', '.join(existing_tables)}")
        else:
            print("! No tables found in database")
    else:
        print(f"\n→ Creating new database at: {DATABASE_PATH}")
    
    print("\n→ Initializing database schema...")
    
    try:
        init_db()
        print("✓ Database initialization completed successfully!")
        
        # Show created tables
        tables = get_existing_tables()
        if tables:
            print(f"\n✓ Available tables: {', '.join(tables)}")
        else:
            print("\n! No tables were created. Make sure models are imported.")
        
        print("\n" + "=" * 60)
        print("Database is ready for use!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
