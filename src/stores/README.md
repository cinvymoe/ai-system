# Camera Store Usage Guide

This document provides examples of how to use the Zustand camera store in your React components.

## Basic Usage

### Import the store

```typescript
import { useCameraStore } from '../stores/cameraStore';
```

### Using in a Component

```typescript
function CameraList() {
  // Select specific state and actions
  const { cameras, loading, error, fetchCameras, clearError } = useCameraStore();
  
  // Fetch cameras on mount
  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error} <button onClick={clearError}>Dismiss</button></div>;
  
  return (
    <div>
      {cameras.map(camera => (
        <div key={camera.id}>{camera.name}</div>
      ))}
    </div>
  );
}
```

## Available Actions

### Fetch All Cameras
```typescript
const fetchCameras = useCameraStore(state => state.fetchCameras);
await fetchCameras();
```

### Fetch Cameras by Direction
```typescript
const fetchCamerasByDirection = useCameraStore(state => state.fetchCamerasByDirection);
await fetchCamerasByDirection('forward');
```

### Add a Camera
```typescript
const addCamera = useCameraStore(state => state.addCamera);

try {
  await addCamera({
    name: 'Front Camera',
    url: 'rtsp://example.com/stream',
    direction: 'forward',
    enabled: true,
  });
  // Success - camera added
} catch (error) {
  // Handle error (e.g., duplicate name)
  console.error('Failed to add camera:', error);
}
```

### Update a Camera
```typescript
const updateCamera = useCameraStore(state => state.updateCamera);

try {
  await updateCamera('camera-id', {
    name: 'Updated Name',
    brightness: 75,
  });
  // Success - camera updated
} catch (error) {
  // Handle error - state automatically rolled back
  console.error('Failed to update camera:', error);
}
```

### Delete a Camera
```typescript
const deleteCamera = useCameraStore(state => state.deleteCamera);

try {
  await deleteCamera('camera-id');
  // Success - camera deleted
} catch (error) {
  // Handle error - camera restored in state
  console.error('Failed to delete camera:', error);
}
```

### Toggle Camera Enabled Status
```typescript
const toggleCameraEnabled = useCameraStore(state => state.toggleCameraEnabled);
await toggleCameraEnabled('camera-id');
// Automatically handles optimistic update and rollback
```

### Update Camera Status
```typescript
const updateCameraStatus = useCameraStore(state => state.updateCameraStatus);
await updateCameraStatus('camera-id', 'online');
```

## Optimistic Updates

The store implements optimistic updates for better UX:

- **Update Camera**: UI updates immediately, rolls back on failure
- **Delete Camera**: Camera removed immediately, restored on failure
- **Toggle Enabled**: Status changes immediately, reverts on failure

## Error Handling

```typescript
function CameraComponent() {
  const { error, clearError } = useCameraStore();
  
  return (
    <>
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}
      {/* Rest of component */}
    </>
  );
}
```

## Performance Optimization

Use selectors to prevent unnecessary re-renders:

```typescript
// Only re-render when cameras change
const cameras = useCameraStore(state => state.cameras);

// Only re-render when loading changes
const loading = useCameraStore(state => state.loading);

// Multiple selectors
const { cameras, loading } = useCameraStore(state => ({
  cameras: state.cameras,
  loading: state.loading,
}));
```

## Integration with Components

The store is designed to work with the following components:

- **CameraListSettings**: Display and manage camera list
- **AddCameraSettings**: Create new cameras
- **EditCameraSettings**: Update existing cameras

See the task list for implementation details of these component integrations.
