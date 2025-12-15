# Technology Stack & Build System

## Frontend Stack

- **Framework**: React 18.3.1 with TypeScript 5.9.3
- **Build Tool**: Vite 6.3.5
- **Desktop**: Electron 39.2.3 with electron-builder 26.0.12
- **UI Components**: Radix UI (comprehensive component library)
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: Zustand 5.0.9
- **HTTP Client**: Axios 1.13.2
- **Forms**: React Hook Form 7.55.0
- **Charts**: Recharts 2.15.2
- **Notifications**: Sonner 2.0.3

## Backend Stack

- **Language**: Python >=3.10
- **Framework**: FastAPI >=0.104.0
- **Server**: Uvicorn >=0.24.0
- **Database**: SQLite with SQLAlchemy >=2.0.0
- **Validation**: Pydantic >=2.0.0
- **Package Manager**: uv (Python package manager)
- **Task Scheduling**: APScheduler >=3.10.0
- **Serial Communication**: PySerial >=3.5
- **Computer Vision**: OpenCV >=4.8.0
- **Testing**: Pytest >=7.4.0, pytest-asyncio >=1.3.0
- **Code Quality**: Black, Ruff

## Build & Development Commands

### Frontend

```bash
# Install dependencies
npm i

# Development server (Vite + Electron)
npm run dev
npm run dev:vite      # Vite only
npm run dev:electron  # Electron only

# Build
npm run build
npm run build:vite    # Build React app
npm run build:electron # Build Electron main process

# Packaging
npm run pack          # Package for current platform
npm run pack:linux    # Package for Linux
npm run pack:arm64    # Package for ARM64
npm run dist          # Create distribution
npm run dist:linux    # Distribution for Linux
npm run dist:arm64    # Distribution for ARM64
```

### Backend

```bash
# Setup virtual environment
cd backend
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows

# Install dependencies
uv sync
uv pip install -e ".[dev]"

# Run development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Testing
uv run pytest
uv run pytest --cov=src tests/

# Code quality
uv run black src/ tests/
uv run ruff check src/ tests/

# Database
python src/init_database.py
python src/migrate_data.py --import-sample
```

## Key Configuration Files

- **Frontend**: `vite.config.ts`, `tsconfig.json`, `electron-builder.yml`
- **Backend**: `backend/pyproject.toml`, `backend/.env.example`
- **Database**: `backend/src/database.py` (SQLite at `backend/data/vision_security.db`)

## Environment Variables

### Backend (.env)

```
LOG_LEVEL=INFO
ENABLE_AUTO_MONITORING=true
CAMERA_CHECK_INTERVAL_MINUTES=5
CAMERA_CHECK_TIMEOUT_SECONDS=5
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Development Workflow

1. **Frontend**: Vite dev server runs on `http://localhost:3000` or `http://localhost:5173`
2. **Backend**: FastAPI runs on `http://localhost:8000`
3. **Electron**: Connects to both frontend and backend
4. **WebSocket**: Real-time communication at `ws://localhost:8000/api/broker/stream`

## Testing

- **Frontend**: Component testing with React Testing Library (if configured)
- **Backend**: Unit and integration tests with Pytest
- **Manual Testing**: HTML test pages available at `/test` endpoint
