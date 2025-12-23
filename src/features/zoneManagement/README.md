# Zone Management Infrastructure

This directory contains the core infrastructure for camera alert zone management functionality.

## Overview

The zone management system allows users to draw warning and alarm zones on camera feeds. It provides:

- Interactive zone drawing with mouse/touch input
- Zone manipulation (resize, move, delete)
- Coordinate transformation between screen and relative coordinates
- Zone persistence through the AI Settings API
- Validation and error handling

## Architecture

### Types (`src/types/zone.ts`)
- `Zone`: Core zone interface with ID, type, points, visibility, and selection state
- `ZoneType`: Enumeration for 'warning' and 'alarm' zones
- `DrawingState`: State management for active drawing operations
- `ZoneManipulationMode`: Different interaction modes (drawing, selecting, resizing, moving)

### Hooks

#### `useZoneManagement` (`src/hooks/useZoneManagement.ts`)
Main hook for zone state management:
- Zone CRUD operations (create, update, delete)
- Drawing state management
- Zone selection and visibility controls
- Utility functions for zone queries

#### `useZonePersistence` (`src/hooks/useZonePersistence.ts`)
Handles backend integration:
- Save zones to AI Settings API
- Load zones from AI Settings
- Convert between UI and API formats

### Utilities

#### Coordinate Transformation (`src/utils/coordinateTransform.ts`)
- Convert between screen pixels and relative coordinates (0-1)
- Create rectangle points from drawing coordinates
- Calculate zone bounds and intersections
- Handle resize handles and point-in-zone detection

#### Zone Validation (`src/utils/zoneValidation.ts`)
- Validate zone data integrity
- Check coordinate bounds and minimum sizes
- Detect zone overlaps
- Sanitize zone data

## Usage

```typescript
import { useZoneManagement, useZonePersistence } from './features/zoneManagement';

function ZoneDrawingComponent() {
  const {
    zones,
    drawingState,
    createZone,
    startDrawing,
    finishDrawing
  } = useZoneManagement();

  const { saveZones, loadZones } = useZonePersistence();

  // Drawing workflow
  const handleMouseDown = (point) => {
    startDrawing('warning', point);
  };

  const handleMouseUp = () => {
    const newZone = finishDrawing();
    if (newZone) {
      // Zone created successfully
    }
  };
}
```

## Coordinate System

The system uses relative coordinates (0-1) for device independence:
- Origin (0,0) at top-left corner
- Point (1,1) at bottom-right corner
- Rectangles defined by 4 points: [top-left, top-right, bottom-right, bottom-left]

## Backend Integration

Zones are stored in the AI Settings table:
- `warning_zone`: Point[] for warning zone coordinates
- `danger_zone`: Point[] for alarm zone coordinates

Current limitation: One zone per type (backend schema constraint)

## Testing

Basic test structure is provided in `src/utils/__tests__/`. Tests cover:
- Coordinate transformations
- Zone validation
- Utility functions

Property-based testing can be added using fast-check library for comprehensive input validation.

## Future Enhancements

1. Multiple zones per type (requires backend schema changes)
2. Complex polygon shapes (currently rectangles only)
3. Zone templates and presets
4. Undo/redo functionality
5. Zone grouping and layers