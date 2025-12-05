# Backend Scripts

This directory contains utility scripts for managing the camera database.

## Available Scripts

### setup_initial_data.sh

Initializes the database with sample camera data.

**Usage:**
```bash
./scripts/setup_initial_data.sh
```

**What it does:**
- Checks if database already has data
- Prompts for confirmation if data exists
- Optionally clears existing data
- Imports sample camera data
- Shows database statistics

**When to use:**
- First-time setup
- Development environment initialization
- After database reset

### backup_data.sh

Creates a timestamped backup of all camera data.

**Usage:**
```bash
./scripts/backup_data.sh
```

**What it does:**
- Creates `backups/` directory if it doesn't exist
- Exports all camera data to JSON with timestamp
- Keeps only the last 10 backups (auto-cleanup)

**Backup file format:**
```
backups/cameras_backup_YYYYMMDD_HHMMSS.json
```

**When to use:**
- Before major changes
- Regular scheduled backups
- Before database migrations
- Before system updates

## Automation

### Scheduled Backups (Linux/macOS)

Add to crontab for daily backups at 2 AM:

```bash
crontab -e
```

Add this line:
```
0 2 * * * cd /path/to/backend && ./scripts/backup_data.sh >> logs/backup.log 2>&1
```

### Scheduled Backups (Windows)

Use Task Scheduler to run the backup script:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 2 AM)
4. Action: Start a program
5. Program: `bash.exe`
6. Arguments: `/path/to/backend/scripts/backup_data.sh`

## Manual Operations

For more advanced operations, use the migration script directly:

```bash
# See all options
python src/migrate_data.py --help

# Export to specific file
python src/migrate_data.py --export my_backup.json

# Import from specific file
python src/migrate_data.py --import my_backup.json

# Import and replace existing data
python src/migrate_data.py --import my_backup.json --replace

# Clear all data
python src/migrate_data.py --clear

# Show statistics
python src/migrate_data.py --stats
```

## Troubleshooting

### Permission Denied

If you get permission errors:

```bash
chmod +x scripts/*.sh
```

### Script Not Found

Make sure you're in the backend directory:

```bash
cd backend
./scripts/setup_initial_data.sh
```

### Database Locked

If you get "database is locked" errors:
1. Stop the FastAPI server
2. Close any database connections
3. Try the operation again

## Best Practices

1. **Backup before changes** - Always backup before major operations
2. **Test imports** - Test imports in development before production
3. **Keep backups** - The backup script keeps 10 backups automatically
4. **Document changes** - Keep notes on what data was imported/exported
5. **Version control** - Consider versioning your backup files

## Related Documentation

- [Migration Guide](../MIGRATION_GUIDE.md) - Detailed migration documentation
- [Backend README](../README.md) - General backend documentation
- [Design Document](../../.kiro/specs/camera-database-integration/design.md) - System design
