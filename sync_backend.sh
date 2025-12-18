#!/bin/bash

# Sync backend folder to remote server
# Targets: 
#   - cat@192.168.1.128:/home/cat/
#   - /data/project/npm/ai-system/release/linux-arm64-unpacked

echo "Syncing backend folder to multiple targets..."

# Target 1: Original remote server
echo "1. Syncing to cat@192.168.1.128:/home/cat/"
rsync -avz --progress \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='data/' \
  --exclude='backups/' \
  --exclude='.python-version' \
  --exclude='.pyproject.toml' \
  backend/ cat@192.168.1.128:/home/cat/backend/

echo "2.      "
rsync -avz --progress \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='data/' \
  datahandler/ cat@192.168.1.128:/home/cat/datahandler/

# Target 2: Local release folder
echo "3. Syncing to /data/project/npm/ai-system/release/linux-arm64-unpacked/"
rsync -avz --progress \
  /data/project/npm/ai-system/release/linux-arm64-unpacked/ cat@192.168.1.128:/home/cat/linux-arm64-unpacked

echo "All syncs completed!"
