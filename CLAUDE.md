# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Vision Security Monitoring System (视觉安全监控系统) - an Electron-based desktop application with a Python FastAPI backend for monitoring cameras, detecting intrusions, and managing security alerts. The system is designed for industrial monitoring, particularly crane/gantry operations (龙门吊).

### Architecture

**Frontend (Electron + React + TypeScript):**
- Main application: Electron wrapper around a React/Vite frontend
- UI: React with Tailwind CSS, Radix UI components, and Zustand for state management
- Styling: Dark theme with cyan accents, professional security monitoring aesthetic

**Backend (Python FastAPI):**
- API: FastAPI with SQLAlchemy ORM for database operations
- Database: SQLite with camera, angle ranges, and monitoring data
- Camera monitoring: OpenCV-based camera connectivity checking with APScheduler
- Auto-monitoring: Background service that checks camera status every 5 minutes

## Common Development Commands

### Frontend Development
```bash
# Install dependencies
npm i

# Start development server (both Vite and Electron)
npm run dev

# Start only Vite dev server
npm run dev:vite

# Build application
npm run build

# Build for distribution
npm run dist

# Build for Linux ARM64
npm run dist:arm64
```

### Backend Development
```bash
cd backend

# Setup environment (requires Python 3.10+ and uv)
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install dependencies
uv sync
# or with specific packages: uv pip install fastapi uvicorn opencv-python apscheduler

# Start development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/
```

## Key Architecture Patterns

### Backend Architecture
- **FastAPI application** (`backend/src/main.py`) with lifespan management for database initialization and camera monitoring
- **Layered architecture**: API routes → Services → Repositories → Database
- **Database models**: SQLAlchemy models in `backend/src/models/`
- **API schemas**: Pydantic models in `backend/src/schemas/` for request/response validation
- **Business logic**: Service layer in `backend/src/services/`
- **Data access**: Repository pattern in `backend/src/repositories/`

### Frontend Architecture
- **Electron main process** (`electron/main.ts`) handles IPC communication and window management
- **React application** with component-based architecture
- **State management**: Zustand stores for cameras and angle ranges
- **Navigation**: Sidebar-based settings navigation with role-based access control
- **UI components**: Radix UI primitives with custom styling in `src/components/ui/`

### Camera Management System
- **Camera CRUD operations**: Full REST API with automatic online/offline status checking
- **Direction-based grouping**: Cameras organized by movement directions (forward, backward, left, right, idle)
- **Auto-monitoring**: Background scheduler checks camera connectivity and updates status
- **Angle range support**: Configure directional monitoring zones for cameras

## Database Schema

### Core Tables
- **cameras**: Stores camera configuration (id, name, url, direction, status, enabled)
- **angle_ranges**: Directional monitoring zones for cameras
- Auto-initialization on first run with `src/database.py`

## Testing

### Backend Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src tests/

# Camera online status tests
uv run pytest tests/test_camera_online_check.py
```

### Frontend Testing
Camera connectivity testing is available through the built-in BackendTest component.

## Important File Locations

### Backend Core Files
- `backend/src/main.py` - FastAPI application entry point
- `backend/src/api/cameras.py` - Camera API endpoints
- `backend/src/services/camera_service.py` - Camera business logic
- `backend/src/models/camera.py` - Camera database model
- `backend/src/scheduler/camera_monitor.py` - Auto-monitoring service

### Frontend Core Files
- `src/App.tsx` - Main React application with routing and state
- `electron/main.ts` - Electron main process and IPC handlers
- `src/components/settings/CameraListSettings.tsx` - Camera management UI
- `src/stores/cameraStore.ts` - Camera state management
- `src/services/cameraService.ts` - API service layer

## Configuration

### Environment Variables (Backend)
- `CAMERA_CHECK_INTERVAL_MINUTES=5` - Auto-check interval
- `CAMERA_CHECK_TIMEOUT_SECONDS=5` - Connection timeout
- `ENABLE_AUTO_MONITORING=true` - Enable background monitoring
- `LOG_LEVEL=INFO` - Logging level

### CORS Configuration
Backend configured to accept requests from frontend development server and production origins.

## Development Guidelines

### Backend Development
- Follow the repository pattern for data access
- Use Pydantic schemas for all API inputs/outputs
- Implement proper error handling with HTTP status codes
- Add comprehensive logging for camera operations
- Use SQLAlchemy models with proper relationships

### Frontend Development
- Use TypeScript interfaces for all data structures
- Implement proper loading states and error handling
- Follow the established dark theme styling patterns
- Use Radix UI components for accessibility
- Store state in Zustand stores for cross-component data sharing

### Camera Integration
- Always check camera connectivity before adding to database
- Handle both RTSP and HTTP camera streams
- Implement proper timeout handling for camera connections
- Update camera status automatically through the monitoring service

## API Endpoints Reference

### Camera Management
- `GET /api/cameras/` - List all cameras
- `POST /api/cameras/` - Create camera (with online check)
- `GET /api/cameras/{id}` - Get camera details
- `PATCH /api/cameras/{id}` - Update camera
- `DELETE /api/cameras/{id}` - Delete camera
- `POST /api/cameras/{id}/check-status` - Check camera status
- `POST /api/cameras/check-all-status` - Check all cameras
- `GET /api/cameras/monitor/status` - Get monitoring service status

### Angle Ranges
- `GET /api/angle-ranges/` - List all angle ranges
- `POST /api/angle-ranges/` - Create angle range
- `GET /api/angle-ranges/{id}` - Get angle range details
- `PATCH /api/angle-ranges/{id}` - Update angle range
- `DELETE /api/angle-ranges/{id}` - Delete angle range

## IPC Communication (Electron)
The main process provides camera API access through IPC handlers:
- `camera:getAll` - Get all cameras
- `camera:create` - Create new camera
- `camera:update` - Update camera
- `camera:delete` - Delete camera
- `camera:getById` - Get specific camera
- `camera:getByDirection` - Get cameras by direction

All IPC handlers include error handling, retry logic, and timeout management.