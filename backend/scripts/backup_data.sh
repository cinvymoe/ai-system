#!/bin/bash
# Backup script for camera database

set -e

# Change to backend directory
cd "$(dirname "$0")/.."

# Create backups directory if it doesn't exist
mkdir -p backups

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/cameras_backup_${TIMESTAMP}.json"

echo "=========================================="
echo "Camera Database Backup"
echo "=========================================="
echo ""
echo "Backing up to: $BACKUP_FILE"
echo ""

# Export data
python src/migrate_data.py --export "$BACKUP_FILE"

echo ""
echo "=========================================="
echo "Backup complete!"
echo "File: $BACKUP_FILE"
echo "=========================================="

# Keep only last 10 backups
echo ""
echo "Cleaning old backups (keeping last 10)..."
ls -t backups/cameras_backup_*.json 2>/dev/null | tail -n +11 | xargs -r rm
echo "Done!"
