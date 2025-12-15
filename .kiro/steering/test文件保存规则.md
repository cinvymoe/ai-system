---
inclusion: always
---

# Test File Organization Rules

## General Principles

- Test files should be organized close to the code they test
- Each module should have its own `test/` folder for module-specific tests
- Create test folders if they don't exist when adding new tests

## Backend Test Organization

### Main Test Directory (`backend/tests/`)

- Use for integration tests and cross-module tests
- Test files follow naming pattern: `test_<module_name>.py`
- Examples: `test_api_cameras.py`, `test_camera_service.py`

### Module-Level Test Directories

- Each backend submodule should have its own `test/` folder
- Place unit tests specific to that module in its local `test/` folder
- Example: `backend/src/broker/test/` for broker-specific tests

### Test File Placement Rules

1. **Integration tests** → `backend/tests/`
2. **Module unit tests** → `backend/src/<module>/test/`
3. **Quick verification scripts** → `backend/test_*.py` (root level, for manual testing)

## Frontend Test Organization

- Frontend tests should be placed adjacent to components: `src/components/__tests__/`
- Or use a centralized test directory if preferred: `src/__tests__/`

## Naming Conventions

- Python test files: `test_<feature>.py`
- Test classes: `Test<FeatureName>`
- Test functions: `test_<specific_behavior>()`

## Examples

```
backend/
├── tests/                          # Integration tests
│   ├── test_api_cameras.py
│   └── test_camera_service.py
├── src/
│   └── broker/
│       └── test/                   # Broker module tests
│           └── test_handlers.py
└── test_broker_websocket.py        # Manual verification script
```