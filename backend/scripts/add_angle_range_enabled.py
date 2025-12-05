#!/usr/bin/env python3
"""
Migration script to add enabled column to angle_ranges table.
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text
from src.database import DATABASE_URL

def main():
    """Add enabled column to angle_ranges table."""
    print("Creating database engine...")
    engine = create_engine(DATABASE_URL)
    
    # Check if table exists
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'angle_ranges' not in existing_tables:
        print("✗ Table 'angle_ranges' does not exist")
        return
    
    # Check if enabled column already exists
    columns = [col['name'] for col in inspector.get_columns('angle_ranges')]
    
    if 'enabled' in columns:
        print("✓ Column 'enabled' already exists in angle_ranges table")
        return
    
    print("Adding 'enabled' column to angle_ranges table...")
    
    with engine.connect() as conn:
        # Add enabled column with default value True
        conn.execute(text("ALTER TABLE angle_ranges ADD COLUMN enabled BOOLEAN DEFAULT 1"))
        conn.commit()
    
    print("✓ Column 'enabled' added successfully")

if __name__ == "__main__":
    main()
