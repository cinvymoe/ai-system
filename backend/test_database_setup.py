#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify database setup is working correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import init_db, get_db, DATABASE_PATH, engine
from sqlalchemy import inspect


def test_database_initialization():
    """Test that database can be initialized."""
    print("Testing database initialization...")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Check database file exists
    assert DATABASE_PATH.exists(), "Database file should exist"
    print(f"✓ Database file exists at: {DATABASE_PATH}")
    
    # Check we can get a database session
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None, "Should be able to get database session"
    db.close()
    print("✓ Database session works")
    
    # Check inspector works
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✓ Database inspector works (tables: {tables})")
    
    print("\n" + "=" * 60)
    print("All database setup tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_database_initialization()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
