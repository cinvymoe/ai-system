#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data migration script for camera database.

This script provides functionality to:
- Import initial sample camera data
- Export camera data to JSON
- Import camera data from JSON
- Migrate data from legacy formats

Usage:
    # Import sample data
    python migrate_data.py --import-sample
    
    # Export current data
    python migrate_data.py --export cameras_backup.json
    
    # Import from JSON file
    python migrate_data.py --import cameras_backup.json
    
    # Clear all data
    python migrate_data.py --clear
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_db
from models.camera import Camera
from sqlalchemy.exc import IntegrityError


# Sample initial camera data based on the original App.tsx structure
SAMPLE_CAMERAS = [
    {
        "id": "camera-forward-1",
        "name": "前方主摄像头",
        "url": "rtsp://192.168.1.101:554/stream1",
        "enabled": True,
        "resolution": "1920x1080",
        "fps": 30,
        "brightness": 50,
        "contrast": 50,
        "status": "online",
        "direction": "forward"
    },
    {
        "id": "camera-forward-2",
        "name": "前方辅助摄像头",
        "url": "rtsp://192.168.1.102:554/stream1",
        "enabled": True,
        "resolution": "1920x1080",
        "fps": 25,
        "brightness": 55,
        "contrast": 48,
        "status": "online",
        "direction": "forward"
    },
    {
        "id": "camera-backward-1",
        "name": "后方摄像头",
        "url": "rtsp://192.168.1.103:554/stream1",
        "enabled": True,
        "resolution": "1280x720",
        "fps": 25,
        "brightness": 50,
        "contrast": 50,
        "status": "offline",
        "direction": "backward"
    },
    {
        "id": "camera-left-1",
        "name": "左侧摄像头",
        "url": "rtsp://192.168.1.104:554/stream1",
        "enabled": True,
        "resolution": "1920x1080",
        "fps": 30,
        "brightness": 52,
        "contrast": 52,
        "status": "online",
        "direction": "left"
    },
    {
        "id": "camera-right-1",
        "name": "右侧摄像头",
        "url": "rtsp://192.168.1.105:554/stream1",
        "enabled": False,
        "resolution": "1920x1080",
        "fps": 30,
        "brightness": 50,
        "contrast": 50,
        "status": "offline",
        "direction": "right"
    },
    {
        "id": "camera-idle-1",
        "name": "备用摄像头",
        "url": "rtsp://192.168.1.106:554/stream1",
        "enabled": False,
        "resolution": "1280x720",
        "fps": 20,
        "brightness": 50,
        "contrast": 50,
        "status": "offline",
        "direction": "idle"
    }
]


def import_sample_data(db_session) -> int:
    """Import sample camera data into the database.
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        Number of cameras imported
    """
    print("\n→ Importing sample camera data...")
    imported_count = 0
    skipped_count = 0
    
    for camera_data in SAMPLE_CAMERAS:
        try:
            # Check if camera already exists
            existing = db_session.query(Camera).filter(
                Camera.id == camera_data["id"]
            ).first()
            
            if existing:
                print(f"  ⊘ Skipped: {camera_data['name']} (already exists)")
                skipped_count += 1
                continue
            
            # Create new camera
            camera = Camera(**camera_data)
            db_session.add(camera)
            db_session.commit()
            
            print(f"  ✓ Imported: {camera_data['name']}")
            imported_count += 1
            
        except IntegrityError as e:
            db_session.rollback()
            print(f"  ✗ Error importing {camera_data['name']}: {e}")
            skipped_count += 1
        except Exception as e:
            db_session.rollback()
            print(f"  ✗ Unexpected error importing {camera_data['name']}: {e}")
            skipped_count += 1
    
    print(f"\n✓ Import complete: {imported_count} imported, {skipped_count} skipped")
    return imported_count


def export_data(db_session, output_file: Path) -> int:
    """Export all camera data to a JSON file.
    
    Args:
        db_session: SQLAlchemy database session
        output_file: Path to output JSON file
        
    Returns:
        Number of cameras exported
    """
    print(f"\n→ Exporting camera data to {output_file}...")
    
    try:
        cameras = db_session.query(Camera).all()
        
        if not cameras:
            print("  ! No cameras found in database")
            return 0
        
        # Convert cameras to dict format
        cameras_data = []
        for camera in cameras:
            camera_dict = {
                "id": camera.id,
                "name": camera.name,
                "url": camera.url,
                "enabled": camera.enabled,
                "resolution": camera.resolution,
                "fps": camera.fps,
                "brightness": camera.brightness,
                "contrast": camera.contrast,
                "status": camera.status,
                "direction": camera.direction,
                "created_at": camera.created_at.isoformat() if camera.created_at else None,
                "updated_at": camera.updated_at.isoformat() if camera.updated_at else None
            }
            cameras_data.append(camera_dict)
        
        # Write to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cameras_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Exported {len(cameras_data)} cameras to {output_file}")
        return len(cameras_data)
        
    except Exception as e:
        print(f"✗ Error exporting data: {e}")
        return 0


def import_data(db_session, input_file: Path, replace: bool = False) -> int:
    """Import camera data from a JSON file.
    
    Args:
        db_session: SQLAlchemy database session
        input_file: Path to input JSON file
        replace: If True, replace existing cameras with same ID
        
    Returns:
        Number of cameras imported
    """
    print(f"\n→ Importing camera data from {input_file}...")
    
    if not input_file.exists():
        print(f"✗ File not found: {input_file}")
        return 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            cameras_data = json.load(f)
        
        if not isinstance(cameras_data, list):
            print("✗ Invalid file format: expected a list of cameras")
            return 0
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        for camera_data in cameras_data:
            try:
                # Remove timestamp fields if present (will be auto-generated)
                camera_data.pop('created_at', None)
                camera_data.pop('updated_at', None)
                
                # Check if camera exists
                existing = db_session.query(Camera).filter(
                    Camera.id == camera_data["id"]
                ).first()
                
                if existing:
                    if replace:
                        # Update existing camera
                        for key, value in camera_data.items():
                            if key != 'id':
                                setattr(existing, key, value)
                        db_session.commit()
                        print(f"  ↻ Updated: {camera_data['name']}")
                        updated_count += 1
                    else:
                        print(f"  ⊘ Skipped: {camera_data['name']} (already exists)")
                        skipped_count += 1
                else:
                    # Create new camera
                    camera = Camera(**camera_data)
                    db_session.add(camera)
                    db_session.commit()
                    print(f"  ✓ Imported: {camera_data['name']}")
                    imported_count += 1
                    
            except IntegrityError as e:
                db_session.rollback()
                print(f"  ✗ Error importing {camera_data.get('name', 'unknown')}: {e}")
                skipped_count += 1
            except Exception as e:
                db_session.rollback()
                print(f"  ✗ Unexpected error: {e}")
                skipped_count += 1
        
        print(f"\n✓ Import complete: {imported_count} new, {updated_count} updated, {skipped_count} skipped")
        return imported_count + updated_count
        
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON file: {e}")
        return 0
    except Exception as e:
        print(f"✗ Error importing data: {e}")
        return 0


def clear_data(db_session) -> int:
    """Clear all camera data from the database.
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        Number of cameras deleted
    """
    print("\n→ Clearing all camera data...")
    
    try:
        count = db_session.query(Camera).count()
        
        if count == 0:
            print("  ! Database is already empty")
            return 0
        
        # Confirm deletion
        response = input(f"  ⚠ This will delete {count} cameras. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("  ⊘ Operation cancelled")
            return 0
        
        db_session.query(Camera).delete()
        db_session.commit()
        
        print(f"✓ Deleted {count} cameras")
        return count
        
    except Exception as e:
        db_session.rollback()
        print(f"✗ Error clearing data: {e}")
        return 0


def show_stats(db_session):
    """Display database statistics.
    
    Args:
        db_session: SQLAlchemy database session
    """
    print("\n" + "=" * 60)
    print("Database Statistics")
    print("=" * 60)
    
    try:
        total = db_session.query(Camera).count()
        enabled = db_session.query(Camera).filter(Camera.enabled == True).count()
        online = db_session.query(Camera).filter(Camera.status == 'online').count()
        
        print(f"\nTotal cameras: {total}")
        print(f"Enabled cameras: {enabled}")
        print(f"Online cameras: {online}")
        
        # Count by direction
        print("\nCameras by direction:")
        for direction in ['forward', 'backward', 'left', 'right', 'idle']:
            count = db_session.query(Camera).filter(
                Camera.direction == direction
            ).count()
            print(f"  {direction}: {count}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"✗ Error getting statistics: {e}")


def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Camera database migration tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import sample data
  python migrate_data.py --import-sample
  
  # Export current data
  python migrate_data.py --export cameras_backup.json
  
  # Import from JSON file
  python migrate_data.py --import cameras_backup.json
  
  # Import and replace existing cameras
  python migrate_data.py --import cameras_backup.json --replace
  
  # Clear all data
  python migrate_data.py --clear
  
  # Show statistics
  python migrate_data.py --stats
        """
    )
    
    parser.add_argument(
        '--import-sample',
        action='store_true',
        help='Import sample camera data'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export camera data to JSON file'
    )
    
    parser.add_argument(
        '--import',
        type=str,
        metavar='FILE',
        dest='import_file',
        help='Import camera data from JSON file'
    )
    
    parser.add_argument(
        '--replace',
        action='store_true',
        help='Replace existing cameras when importing (use with --import)'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all camera data (requires confirmation)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    
    args = parser.parse_args()
    
    # Check if any action is specified
    if not any([args.import_sample, args.export, args.import_file, args.clear, args.stats]):
        parser.print_help()
        return
    
    print("=" * 60)
    print("Camera Database Migration Tool")
    print("=" * 60)
    
    # Initialize database
    print("\n→ Initializing database...")
    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Execute requested operations
        if args.import_sample:
            import_sample_data(db)
        
        if args.export:
            export_data(db, Path(args.export))
        
        if args.import_file:
            import_data(db, Path(args.import_file), replace=args.replace)
        
        if args.clear:
            clear_data(db)
        
        if args.stats or not any([args.import_sample, args.export, args.import_file, args.clear]):
            show_stats(db)
        
        print("\n" + "=" * 60)
        print("Operation completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
