---
inclusion: always
---

# Project Structure

## Root Level

```
.
├── backend/              # Python FastAPI backend
├── src/                  # React frontend source
├── electron/             # Electron main process & preload
├── datahandler/          # Sensor data processing utilities
├── doc/                  # Documentation (Chinese)
├── release/              # Built Electron distributions
├── package.json          # Frontend dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Vite build config
└── electron-builder.yml  # Electron packaging config
```

## Backend Structure (`backend/src/`)

```
backend/src/
├── main.py              # FastAPI application entry point
├── database.py          # SQLAlchemy setup & session management
├── config.py            # Configuration & environment variables
├── init_database.py     # Database initialization script
├── migrate_data.py      # Data migration utilities
│
├── api/                 # API route handlers
│   ├── cameras.py       # Camera CRUD endpoints
│   ├── sensors.py       # Sensor data endpoints
│   ├── angle_ranges.py  # Angle range management
│   ├── ai_settings.py   # AI configuration endpoints
│   ├── broker.py        # Message broker WebSocket
│   └── rtsp.py          # RTSP streaming endpoints
│
├── models/              # SQLAlchemy ORM models
│   ├── camera.py        # Camera model
│   ├── ai_settings.py   # AI settings model
│   └── angle_range.py   # Angle range model
│
├── schemas/             # Pydantic request/response schemas
│   ├── camera.py
│   ├── ai_settings.py
│   └── angle_range.py
│
├── services/            # Business logic layer
│   ├── camera_service.py
│   ├── ai_settings_service.py
│   └── rtsp_service.py
│
├── repositories/        # Data access layer
│   ├── camera_repository.py
│   └── ai_settings_repository.py
│
├── broker/              # Message broker system
│   ├── broker.py        # Main broker class
│   ├── handlers.py      # Message type handlers
│   ├── mapper.py        # Camera mapper for broker
│   ├── models.py        # Broker data models
│   ├── errors.py        # Custom exceptions
│   └── logging_config.py
│
├── collectors/          # Sensor data collection
│   ├── models.py        # Data models
│   ├── enums.py         # Enumerations
│   ├── mocks.py         # Mock implementations
│   ├── sensors/         # Sensor implementations
│   └── processors/      # Data processors
│
└── scheduler/           # Background tasks
    └── camera_monitor.py # Periodic camera status checks
```

## Frontend Structure (`src/`)

```
src/
├── main.tsx             # React entry point
├── App.tsx              # Main app component
├── index.css            # Global styles
│
├── components/
│   ├── MainCamera.tsx   # Main camera display
│   ├── Sidebar.tsx      # Navigation sidebar
│   ├── AlertPanel.tsx   # Alert notifications
│   ├── LoginDialog.tsx  # Authentication
│   │
│   ├── settings/        # Settings pages
│   │   ├── CameraSettings.tsx
│   │   ├── SensorSettings.tsx
│   │   ├── AISettings.tsx
│   │   ├── AngleRangeSettings.tsx
│   │   ├── DirectionCamerasSettings.tsx
│   │   ├── AddCameraSettings.tsx
│   │   ├── CameraListSettings.tsx
│   │   ├── EditCameraSettings.tsx
│   │   ├── AlarmLogSettings.tsx
│   │   ├── AdminManagement.tsx
│   │   └── AboutSettings.tsx
│   │
│   ├── ui/              # Shadcn/Radix UI components
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── tabs.tsx
│   │   └── ... (40+ UI components)
│   │
│   └── figma/           # Figma-generated components
│       └── ImageWithFallback.tsx
│
├── services/            # API client services
│   ├── cameraService.ts
│   ├── aiSettingsService.ts
│   └── angleRangeService.ts
│
├── stores/              # Zustand state management
│   ├── cameraStore.ts
│   └── angleRangeStore.ts
│
├── hooks/               # Custom React hooks
│   └── useSensorStream.ts
│
├── types/               # TypeScript type definitions
│   └── sensor.ts
│
├── utils/               # Utility functions
│   ├── sensorDataFormatter.ts
│   └── websocketDiagnostics.ts
│
└── styles/              # Global styles
    └── globals.css
```

## Electron Structure (`electron/`)

```
electron/
├── main.ts              # Electron main process
├── preload.ts           # IPC preload script
├── types.ts             # TypeScript types
└── tsconfig.json        # TypeScript config
```

## Key Directories

- **`backend/data/`**: SQLite database file
- **`backend/backups/`**: Database backups
- **`backend/scripts/`**: Utility scripts for setup and migration
- **`backend/tests/`**: Unit tests
- **`backend/examples/`**: Example configurations and data
- **`.kiro/`**: Kiro IDE configuration and steering files

## Database Schema

The SQLite database (`backend/data/vision_security.db`) contains:

- **cameras**: Camera configurations and status
- **ai_settings**: AI detection parameters
- **angle_ranges**: Directional control ranges

## API Endpoints Structure

```
/api/
├── /cameras              # Camera management
├── /sensors              # Sensor data
├── /angle-ranges         # Angle configuration
├── /ai-settings          # AI settings
├── /broker/stream        # WebSocket message broker
└── /rtsp                 # RTSP streaming

/test/                    # Testing pages
├── /websocket
├── /broker-websocket
└── /
```

## Code Organization Principles

1. **Layered Architecture**: API → Services → Repositories → Database
2. **Separation of Concerns**: Models, schemas, and business logic are separate
3. **Reusable Components**: UI components in `components/ui/`, settings in `components/settings/`
4. **Type Safety**: Strong TypeScript typing throughout frontend, Pydantic validation in backend
5. **Configuration**: Environment-based configuration with sensible defaults

## Backend Development Guidelines

### Adding New Features

- **API Endpoints**: Add route handlers in `backend/src/api/`
- **Business Logic**: Implement in `backend/src/services/`
- **Data Access**: Use repositories in `backend/src/repositories/`
- **Database Models**: Define in `backend/src/models/` with corresponding Pydantic schemas in `backend/src/schemas/`
- **Validation**: Use Pydantic models for request/response validation

### Naming Conventions

- **Files**: snake_case (e.g., `camera_service.py`)
- **Classes**: PascalCase (e.g., `CameraService`)
- **Functions/Methods**: snake_case (e.g., `get_camera_by_id()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)

### Testing

- Unit tests in `backend/tests/` mirror the source structure
- Integration tests for API endpoints and services
- Use pytest fixtures for database and mock data
- Test files follow pattern: `test_<module_name>.py`

## Frontend Development Guidelines

### Adding New Features

- **Pages/Sections**: Create settings components in `src/components/settings/`
- **Reusable UI**: Use existing components from `src/components/ui/` (shadcn/Radix)
- **State Management**: Use Zustand stores in `src/stores/` for shared state
- **API Integration**: Create service files in `src/services/` for backend communication
- **Custom Logic**: Implement hooks in `src/hooks/` for reusable component logic

### Naming Conventions

- **Files**: PascalCase for components (e.g., `CameraSettings.tsx`), camelCase for utilities (e.g., `sensorDataFormatter.ts`)
- **Components**: PascalCase (e.g., `MainCamera`)
- **Functions/Hooks**: camelCase (e.g., `useSensorStream`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)

### Component Structure

- Keep components focused and single-responsibility
- Use TypeScript interfaces for props
- Leverage shadcn/ui components for consistency
- Implement error boundaries for critical sections

## Message Broker Architecture

The broker system (`backend/src/broker/`) handles real-time communication:

- **broker.py**: Main broker class managing WebSocket connections
- **handlers.py**: Message type handlers (camera updates, sensor data, etc.)
- **mapper.py**: Maps camera data for broker distribution
- **models.py**: Data models for broker messages
- **errors.py**: Custom exceptions for broker operations

When adding new message types, update handlers and models accordingly.

## Sensor Data Collection

The collectors system (`backend/src/collectors/`) manages sensor integration:

- **sensors/**: Implementations for specific sensor types (e.g., JY901S)
- **processors/**: Data processing and transformation logic
- **mocks.py**: Mock implementations for testing without hardware
- **enums.py**: Sensor-related enumerations

## Database Considerations

- SQLite database at `backend/data/vision_security.db`
- Use SQLAlchemy ORM for all database operations
- Migrations handled via scripts in `backend/scripts/`
- Backup files stored in `backend/backups/`
- Always validate data at schema level before persistence
