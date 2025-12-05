#!/bin/bash

# Sync backend folder to remote server
# Target: cat@192.168.1.128:/home/cat/

echo "Syncing backend folder to cat@192.168.1.128:/home/cat/"

rsync -avz --progress \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='data/' \
  --exclude='backups/' \
  backend/ cat@192.168.1.128:/home/cat/backend/

echo "Sync completed!"
