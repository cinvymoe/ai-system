#!/bin/bash
# Quick setup script to initialize database with sample data

set -e

echo "=========================================="
echo "Camera Database Initial Setup"
echo "=========================================="
echo ""

# Change to backend directory
cd "$(dirname "$0")/.."

# Check if database already has data
if python -c "from src.database import SessionLocal; from src.models.camera import Camera; db = SessionLocal(); count = db.query(Camera).count(); db.close(); exit(0 if count > 0 else 1)" 2>/dev/null; then
    echo "⚠️  Database already contains camera data."
    echo ""
    read -p "Do you want to clear existing data and import sample data? (yes/no): " response
    if [ "$response" != "yes" ]; then
        echo "Operation cancelled."
        exit 0
    fi
    echo ""
    python src/migrate_data.py --clear
fi

# Import sample data
echo ""
echo "Importing sample camera data..."
python src/migrate_data.py --import-sample

# Show statistics
echo ""
python src/migrate_data.py --stats

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
