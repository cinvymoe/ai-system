/**
 * Zone Management Feature - Main Export
 * Provides a centralized export for all zone management functionality
 */

// Types
export type {
  Zone,
  ZoneType,
  DrawingState,
  ZoneCreateParams,
  ZoneUpdateParams,
  ZoneManipulationMode,
  ZoneInteractionEvent,
  ZoneValidationResult,
  ZoneBounds
} from '../../types/zone';

// Hooks
export { useZoneManagement } from '../../hooks/useZoneManagement';
export { useZonePersistence } from '../../hooks/useZonePersistence';

// Utilities
export {
  screenToRelative,
  relativeToScreen,
  createRectanglePoints,
  calculateZoneBounds,
  isPointInZone,
  getResizeHandle,
  validateZoneCoordinates,
  clampCoordinates,
  calculateDistance
} from '../../utils/coordinateTransform';

export {
  validateZone,
  validateZones,
  isValidPoint,
  hasMinimumSize,
  areCoordinatesInBounds,
  doZonesOverlap,
  sanitizeZone,
  MIN_ZONE_SIZE,
  MAX_ZONES_PER_TYPE
} from '../../utils/zoneValidation';

// Re-export Point interface from AI Settings service
export type { Point } from '../../services/aiSettingsService';