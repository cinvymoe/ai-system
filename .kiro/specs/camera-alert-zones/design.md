# Design Document

## Overview

This feature extends the existing AI Settings interface to provide interactive zone drawing capabilities on camera feeds. Users can define warning zones and alarm zones by drawing rectangles directly on the camera video stream. The system leverages the existing backend API that already supports `danger_zone` and `warning_zone` fields in the AI settings.

## Architecture

The solution integrates with the existing AI Settings system using a layered approach:

- **Presentation Layer**: React components for zone drawing and management
- **Service Layer**: Extends existing `aiSettingsService` for zone operations  
- **Data Layer**: Utilizes existing backend API with Point[] coordinate storage
- **Canvas Layer**: HTML5 Canvas overlay for interactive drawing on video streams

## Components and Interfaces

### Core Components

**ZoneDrawingCanvas**
- Overlays camera feed with interactive drawing surface
- Handles mouse events for zone creation and manipulation
- Renders existing zones with visual distinction
- Manages drawing state and user interactions

**ZoneManager**
- Provides zone creation controls (Add Warning Zone, Add Alarm Zone buttons)
- Displays zone list with visibility toggles
- Handles zone selection, deletion, and modification
- Integrates with existing AI Settings form

**CameraFeedViewer**
- Displays live camera stream as background
- Maintains aspect ratio and responsive sizing
- Provides coordinate system for zone mapping

### Data Interfaces

```typescript
// Extends existing Point interface from aiSettingsService
interface Point {
  x: number; // 0-1 relative coordinate
  y: number; // 0-1 relative coordinate
}

// Zone representation for UI state
interface Zone {
  id: string;
  type: 'warning' | 'alarm';
  points: Point[]; // 4 corners: top-left, top-right, bottom-right, bottom-left
  visible: boolean;
  selected: boolean;
}

// Drawing state management
interface DrawingState {
  isDrawing: boolean;
  drawingType: 'warning' | 'alarm' | null;
  startPoint: Point | null;
  currentPoint: Point | null;
}
```

## Data Models

### Zone Storage Format

Zones are stored using the existing AI Settings schema:
- `warning_zone: Point[] | null` - Array of 4 points defining warning zone rectangle
- `danger_zone: Point[] | null` - Array of 4 points defining alarm zone rectangle

### Coordinate System

- Uses relative coordinates (0-1) for device independence
- Origin (0,0) at top-left corner of video feed
- Point (1,1) at bottom-right corner of video feed
- Rectangle defined by 4 points: [top-left, top-right, bottom-right, bottom-left]

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*
### Pr
operty Reflection

After analyzing the acceptance criteria, several properties can be consolidated to eliminate redundancy:

- Properties 1.3 and 2.2 (drawing behavior) test the same drawing mechanism
- Properties 1.4 and 2.3 (zone creation) test the same creation process for different zone types  
- Properties 1.5 and 2.4 (visual rendering) test the same rendering system with different colors
- Properties 1.2 and 2.1 (mode activation) test the same state change mechanism

### Correctness Properties

Property 1: Zone drawing mode activation
*For any* zone type (warning or alarm), clicking the corresponding "Add Zone" button should enable drawing mode for that zone type
**Validates: Requirements 1.2, 2.1**

Property 2: Real-time drawing feedback
*For any* mouse drag operation on the camera feed while in drawing mode, the system should display a rectangular outline that updates in real-time with mouse movement
**Validates: Requirements 1.3, 2.2**

Property 3: Zone creation from coordinates
*For any* valid rectangular area drawn on the camera feed, releasing the mouse button should create a zone with coordinates matching the drawn rectangle
**Validates: Requirements 1.4, 2.3**

Property 4: Zone visual rendering
*For any* created zone, the system should display the zone with the correct color overlay (yellow for warning zones, red for alarm zones)
**Validates: Requirements 1.5, 2.4**

Property 5: Overlapping zone visibility
*For any* set of overlapping zones, all zones should remain visible with appropriate visual distinction
**Validates: Requirements 2.5**

Property 6: Zone selection and controls
*For any* existing zone, clicking on the zone should highlight it and display zone management controls
**Validates: Requirements 3.1**

Property 7: Zone deletion
*For any* selected zone, clicking the delete button should remove the zone from both the display and the underlying data
**Validates: Requirements 3.2**

Property 8: Zone resizing
*For any* zone with corner handles, dragging a corner handle should resize the zone boundaries while maintaining the rectangular shape
**Validates: Requirements 3.3**

Property 9: Zone movement
*For any* zone, dragging the zone center should move the entire zone to the new position
**Validates: Requirements 3.4**

Property 10: Real-time parameter updates
*For any* zone modification (resize or move), the zone parameters should update immediately in the system state
**Validates: Requirements 3.5**

Property 11: Zone data persistence
*For any* zone creation or modification, the zone parameters should be saved to the backend database with correct camera_id, zone_type, and coordinates
**Validates: Requirements 4.1, 4.4**

Property 12: Camera-specific zone loading
*For any* camera selection, the system should load and display only the zones associated with that specific camera
**Validates: Requirements 4.2**

Property 13: Save operation feedback
*For any* successful save operation, the system should display a confirmation message to the user
**Validates: Requirements 4.5**

Property 14: Drawing cursor indication
*For any* drawing mode activation, the cursor should change to indicate drawing capability when hovering over the camera feed
**Validates: Requirements 5.1**

Property 15: Coordinate information display
*For any* active drawing operation, the system should display real-time coordinate information and rectangle dimensions
**Validates: Requirements 5.2, 5.3**

Property 16: Zone information display
*For any* completed zone, the system should display zone information including area size and position
**Validates: Requirements 5.4**

Property 17: Zone list management
*For any* camera with existing zones, the system should provide a zone list with visibility toggle controls for each zone
**Validates: Requirements 5.5**

## Error Handling

### Input Validation
- Validate zone coordinates are within camera feed boundaries (0-1 range)
- Ensure minimum zone size to prevent accidental tiny zones
- Prevent zone creation outside camera feed area

### Network Error Handling
- Handle backend API failures gracefully with user feedback
- Implement retry logic for save operations
- Maintain local state during temporary network issues

### User Experience Errors
- Prevent overlapping zones of the same type in the same location
- Handle camera feed loading failures
- Provide clear error messages for invalid operations

## Testing Strategy

### Unit Testing Approach
Unit tests will focus on:
- Zone coordinate calculations and transformations
- State management for drawing operations
- Data validation and error handling
- Component rendering with different zone configurations

### Property-Based Testing Approach
Property-based tests will use **fast-check** library for JavaScript/TypeScript to verify:
- Zone creation with random coordinates within valid ranges
- Zone manipulation operations (resize, move) preserve data integrity
- Coordinate system transformations between screen and relative coordinates
- Zone persistence and loading across different camera configurations

Each property-based test will run a minimum of 100 iterations to ensure comprehensive coverage of the input space.

### Testing Framework
- **Jest** for unit testing framework
- **React Testing Library** for component testing
- **fast-check** for property-based testing
- **MSW (Mock Service Worker)** for API mocking

### Test Data Generation
Smart generators will be implemented to:
- Generate valid zone coordinates within camera boundaries
- Create realistic camera feed dimensions and aspect ratios
- Generate edge cases like very small zones, boundary zones, and overlapping scenarios
- Simulate various mouse interaction patterns

## Implementation Architecture

### Component Hierarchy
```
AISettings (existing)
├── CameraSelection (existing)
├── ZoneManagement (new)
│   ├── CameraFeedViewer (new)
│   ├── ZoneDrawingCanvas (new)
│   ├── ZoneControls (new)
│   └── ZoneList (new)
└── AIParameters (existing)
```

### State Management
- Extend existing AI Settings state to include zone management
- Use React hooks for local drawing state
- Integrate with existing `aiSettingsService` for persistence

### Canvas Implementation
- HTML5 Canvas overlay on video element
- Mouse event handling for drawing interactions
- Coordinate transformation between screen and relative coordinates
- Zone rendering with appropriate visual styling

### Integration Points
- Extends existing `AISettings` component
- Uses existing `aiSettingsService` for backend communication
- Leverages existing camera selection and management
- Maintains consistency with existing UI patterns and styling