# Data Migration Quick Reference

## Common Commands

### First Time Setup
```bash
# Import sample data
python src/migrate_data.py --import-sample

# Or use the setup script
./scripts/setup_initial_data.sh
```

### Daily Operations
```bash
# View database stats
python src/migrate_data.py --stats

# Verify data
python verify_data.py

# Create backup
./scripts/backup_data.sh
```

### Import/Export
```bash
# Export current data
python src/migrate_data.py --export my_backup.json

# Import new data (skip existing)
python src/migrate_data.py --import my_data.json

# Import and replace existing
python src/migrate_data.py --import my_data.json --replace
```

### Maintenance
```bash
# Clear all data (with confirmation)
python src/migrate_data.py --clear

# Re-import sample data
python src/migrate_data.py --import-sample
```

## File Locations

| Item | Location |
|------|----------|
| Database | `data/vision_security.db` |
| Migration Script | `src/migrate_data.py` |
| Backups | `backups/` |
| Examples | `examples/` |
| Scripts | `scripts/` |

## JSON Format

```json
[
  {
    "id": "unique-id",
    "name": "Camera Name",
    "url": "rtsp://192.168.1.100:554/stream1",
    "enabled": true,
    "resolution": "1920x1080",
    "fps": 30,
    "brightness": 50,
    "contrast": 50,
    "status": "online",
    "direction": "forward"
  }
]
```

## Field Values

| Field | Type | Values | Default |
|-------|------|--------|---------|
| id | string | Any unique string | Required |
| name | string | Any string | Required |
| url | string | RTSP URL | Required |
| enabled | boolean | true/false | true |
| resolution | string | "WxH" format | "1920x1080" |
| fps | integer | 1-60 | 30 |
| brightness | integer | 0-100 | 50 |
| contrast | integer | 0-100 | 50 |
| status | string | "online"/"offline" | "offline" |
| direction | string | "forward"/"backward"/"left"/"right"/"idle" | Required |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Permission denied | `chmod +x scripts/*.sh` |
| Database locked | Stop FastAPI server |
| Import fails | Check JSON format |
| No data showing | Run `--import-sample` |

## Help

```bash
# Show all options
python src/migrate_data.py --help

# View detailed guide
cat MIGRATION_GUIDE.md

# View test results
cat TEST_RESULTS.md
```

## Quick Links

- [Migration Guide](MIGRATION_GUIDE.md) - Detailed documentation
- [Scripts README](scripts/README.md) - Script documentation
- [Test Results](TEST_RESULTS.md) - Verification results
- [Summary](DATA_MIGRATION_SUMMARY.md) - Implementation overview
