#!/usr/bin/env python3
"""
Migration script to add angle_ranges table to the database.
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from src.database import Base, DATABASE_URL
from src.models.angle_range import AngleRange

def main():
    """Add angle_ranges table to the database."""
    print("Creating database engine...")
    engine = create_engine(DATABASE_URL)
    
    # Check if table already exists
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'angle_ranges' in existing_tables:
        print("✓ Table 'angle_ranges' already exists")
        return
    
    print("Creating angle_ranges table...")
    Base.metadata.create_all(engine, tables=[AngleRange.__table__])
    print("✓ Table 'angle_ranges' created successfully")

if __name__ == "__main__":
    main()
