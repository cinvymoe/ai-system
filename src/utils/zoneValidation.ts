/**
 * Zone Validation Utilities
 * Provides validation functions for zone data and operations
 */

import { Zone, ZoneValidationResult } from '../types/zone';
import { Point } from '../services/aiSettingsService';
import { calculateZoneBounds } from './coordinateTransform';

/**
 * Minimum zone size (1% of canvas)
 */
export const MIN_ZONE_SIZE = 0.01;

/**
 * Minimum zone dimension (0.5% of canvas) - prevents extremely thin zones
 */
export const MIN_ZONE_DIMENSION = 0.005;

/**
 * Maximum zone size (90% of canvas) - prevents zones that are too large
 */
export const MAX_ZONE_SIZE = 0.9;

/**
 * Maximum number of zones per type
 */
export const MAX_ZONES_PER_TYPE = 1; // Current backend limitation

/**
 * Coordinate precision for validation (6 decimal places)
 */
export const COORDINATE_PRECISION = 6;

/**
 * Validate a single zone
 */
export function validateZone(zone: Zone): ZoneValidationResult {
  const errors: string[] = [];

  // Check zone ID
  if (!zone.id || zone.id.trim() === '') {
    errors.push('Zone must have a valid ID');
  }

  // Check zone type
  if (!zone.type || !['warning', 'alarm'].includes(zone.type)) {
    errors.push('Zone must have a valid type (warning or alarm)');
  }

  // Check points
  if (!zone.points || zone.points.length !== 4) {
    errors.push('Zone must have exactly 4 points');
  } else {
    // Validate each point
    for (let i = 0; i < zone.points.length; i++) {
      const point = zone.points[i];
      if (!isValidPoint(point)) {
        errors.push(`Point ${i + 1} has invalid coordinates`);
      }
    }

    // Check minimum size
    if (!hasMinimumSize(zone.points)) {
      errors.push('Zone is too small (minimum 1% of canvas size)');
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate multiple zones
 */
export function validateZones(zones: Zone[]): ZoneValidationResult {
  const errors: string[] = [];

  // Check for duplicate IDs
  const ids = zones.map(zone => zone.id);
  const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
  if (duplicateIds.length > 0) {
    errors.push(`Duplicate zone IDs found: ${duplicateIds.join(', ')}`);
  }

  // Check zone count limits
  const warningZones = zones.filter(zone => zone.type === 'warning');
  const alarmZones = zones.filter(zone => zone.type === 'alarm');

  if (warningZones.length > MAX_ZONES_PER_TYPE) {
    errors.push(`Too many warning zones (maximum ${MAX_ZONES_PER_TYPE})`);
  }

  if (alarmZones.length > MAX_ZONES_PER_TYPE) {
    errors.push(`Too many alarm zones (maximum ${MAX_ZONES_PER_TYPE})`);
  }

  // Validate each zone
  zones.forEach((zone, index) => {
    const zoneValidation = validateZone(zone);
    if (!zoneValidation.isValid) {
      errors.push(`Zone ${index + 1}: ${zoneValidation.errors.join(', ')}`);
    }
  });

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate a point with enhanced coordinate checking
 */
export function isValidPoint(point: Point): boolean {
  // Check basic type and structure
  if (!point || typeof point !== 'object') {
    return false;
  }

  const { x, y } = point;

  // Check if coordinates are numbers
  if (typeof x !== 'number' || typeof y !== 'number') {
    return false;
  }

  // Check for NaN, Infinity, or invalid numbers
  if (!isFinite(x) || !isFinite(y) || isNaN(x) || isNaN(y)) {
    return false;
  }

  // Check coordinate bounds (0-1 range for relative coordinates)
  if (x < 0 || x > 1 || y < 0 || y > 1) {
    return false;
  }

  // Check coordinate precision (prevent floating point issues)
  const precisionFactor = Math.pow(10, COORDINATE_PRECISION);
  const roundedX = Math.round(x * precisionFactor) / precisionFactor;
  const roundedY = Math.round(y * precisionFactor) / precisionFactor;
  
  if (Math.abs(x - roundedX) > Number.EPSILON || Math.abs(y - roundedY) > Number.EPSILON) {
    return false;
  }

  return true;
}

/**
 * Validate coordinate bounds with enhanced checking
 */
export function validateCoordinateBounds(point: Point): ZoneValidationResult {
  const errors: string[] = [];

  if (!isValidPoint(point)) {
    errors.push('Invalid point coordinates');
    return { isValid: false, errors };
  }

  // Additional bounds checking
  if (point.x < 0) errors.push('X coordinate cannot be negative');
  if (point.x > 1) errors.push('X coordinate cannot exceed 1.0');
  if (point.y < 0) errors.push('Y coordinate cannot be negative');
  if (point.y > 1) errors.push('Y coordinate cannot exceed 1.0');

  // Check for edge cases
  if (point.x === 0 && point.y === 0) {
    errors.push('Point cannot be at origin (0,0) - may cause rendering issues');
  }
  if (point.x === 1 && point.y === 1) {
    errors.push('Point cannot be at maximum bounds (1,1) - may cause rendering issues');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Check if zone has minimum size with enhanced validation
 */
export function hasMinimumSize(points: Point[]): boolean {
  if (points.length !== 4) return false;

  const bounds = calculateZoneBounds(points);
  
  // Check minimum area
  const area = bounds.width * bounds.height;
  if (area < MIN_ZONE_SIZE) return false;

  // Check minimum dimensions (prevent extremely thin zones)
  if (bounds.width < MIN_ZONE_DIMENSION || bounds.height < MIN_ZONE_DIMENSION) {
    return false;
  }

  return true;
}

/**
 * Check if zone exceeds maximum size
 */
export function hasMaximumSize(points: Point[]): boolean {
  if (points.length !== 4) return false;

  const bounds = calculateZoneBounds(points);
  const area = bounds.width * bounds.height;
  
  return area <= MAX_ZONE_SIZE;
}

/**
 * Validate zone dimensions comprehensively
 */
export function validateZoneDimensions(points: Point[]): ZoneValidationResult {
  const errors: string[] = [];

  if (points.length !== 4) {
    errors.push('Zone must have exactly 4 points');
    return { isValid: false, errors };
  }

  const bounds = calculateZoneBounds(points);
  const area = bounds.width * bounds.height;

  // Check minimum area
  if (area < MIN_ZONE_SIZE) {
    errors.push(`Zone area too small (${(area * 100).toFixed(2)}% < ${(MIN_ZONE_SIZE * 100).toFixed(1)}%)`);
  }

  // Check maximum area
  if (area > MAX_ZONE_SIZE) {
    errors.push(`Zone area too large (${(area * 100).toFixed(2)}% > ${(MAX_ZONE_SIZE * 100).toFixed(1)}%)`);
  }

  // Check minimum dimensions
  if (bounds.width < MIN_ZONE_DIMENSION) {
    errors.push(`Zone width too small (${(bounds.width * 100).toFixed(2)}% < ${(MIN_ZONE_DIMENSION * 100).toFixed(2)}%)`);
  }

  if (bounds.height < MIN_ZONE_DIMENSION) {
    errors.push(`Zone height too small (${(bounds.height * 100).toFixed(2)}% < ${(MIN_ZONE_DIMENSION * 100).toFixed(2)}%)`);
  }

  // Check aspect ratio (prevent extremely elongated zones)
  const aspectRatio = Math.max(bounds.width, bounds.height) / Math.min(bounds.width, bounds.height);
  const MAX_ASPECT_RATIO = 20; // Maximum 20:1 aspect ratio
  
  if (aspectRatio > MAX_ASPECT_RATIO) {
    errors.push(`Zone aspect ratio too extreme (${aspectRatio.toFixed(1)}:1 > ${MAX_ASPECT_RATIO}:1)`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate zone coordinates are within canvas bounds
 */
export function areCoordinatesInBounds(points: Point[]): boolean {
  return points.every(point => isValidPoint(point));
}

/**
 * Validate zone coordinates for drawing operations with enhanced checks
 */
export function validateDrawingCoordinates(startPoint: Point, endPoint: Point): ZoneValidationResult {
  const errors: string[] = [];

  // Validate individual points
  const startValidation = validateCoordinateBounds(startPoint);
  if (!startValidation.isValid) {
    errors.push(`Start point: ${startValidation.errors.join(', ')}`);
  }
  
  const endValidation = validateCoordinateBounds(endPoint);
  if (!endValidation.isValid) {
    errors.push(`End point: ${endValidation.errors.join(', ')}`);
  }

  // If points are invalid, return early
  if (errors.length > 0) {
    return { isValid: false, errors };
  }

  // Check if points are the same (no area)
  if (startPoint.x === endPoint.x && startPoint.y === endPoint.y) {
    errors.push('Start and end points cannot be identical');
    return { isValid: false, errors };
  }

  // Calculate rectangle dimensions
  const width = Math.abs(endPoint.x - startPoint.x);
  const height = Math.abs(endPoint.y - startPoint.y);
  const area = width * height;

  // Check minimum area
  if (area < MIN_ZONE_SIZE) {
    errors.push(`Zone area too small (${(area * 100).toFixed(2)}% < ${(MIN_ZONE_SIZE * 100).toFixed(1)}%)`);
  }

  // Check minimum dimensions
  if (width < MIN_ZONE_DIMENSION) {
    errors.push(`Zone width too small (${(width * 100).toFixed(2)}% < ${(MIN_ZONE_DIMENSION * 100).toFixed(2)}%)`);
  }
  
  if (height < MIN_ZONE_DIMENSION) {
    errors.push(`Zone height too small (${(height * 100).toFixed(2)}% < ${(MIN_ZONE_DIMENSION * 100).toFixed(2)}%)`);
  }

  // Check maximum area
  if (area > MAX_ZONE_SIZE) {
    errors.push(`Zone area too large (${(area * 100).toFixed(2)}% > ${(MAX_ZONE_SIZE * 100).toFixed(1)}%)`);
  }

  // Check aspect ratio
  const aspectRatio = Math.max(width, height) / Math.min(width, height);
  const MAX_ASPECT_RATIO = 20;
  
  if (aspectRatio > MAX_ASPECT_RATIO) {
    errors.push(`Zone aspect ratio too extreme (${aspectRatio.toFixed(1)}:1 > ${MAX_ASPECT_RATIO}:1)`);
  }

  // Check minimum distance between points (diagonal)
  const distance = Math.sqrt(width * width + height * height);
  if (distance < MIN_ZONE_DIMENSION * Math.sqrt(2)) {
    errors.push(`Zone diagonal too small (minimum diagonal: ${(MIN_ZONE_DIMENSION * Math.sqrt(2) * 100).toFixed(2)}%)`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate zone before manipulation (resize/move) with comprehensive checks
 */
export function validateZoneManipulation(_zone: Zone, newPoints: Point[]): ZoneValidationResult {
  const errors: string[] = [];

  // Validate new points count
  if (newPoints.length !== 4) {
    errors.push('Zone must have exactly 4 points');
    return { isValid: false, errors };
  }

  // Check all points are valid with detailed validation
  for (let i = 0; i < newPoints.length; i++) {
    const pointValidation = validateCoordinateBounds(newPoints[i]);
    if (!pointValidation.isValid) {
      errors.push(`Point ${i + 1}: ${pointValidation.errors.join(', ')}`);
    }
  }

  // If points are invalid, return early
  if (errors.length > 0) {
    return { isValid: false, errors };
  }

  // Validate zone dimensions
  const dimensionValidation = validateZoneDimensions(newPoints);
  if (!dimensionValidation.isValid) {
    errors.push(...dimensionValidation.errors);
  }

  // Check if zone stays within bounds
  if (!areCoordinatesInBounds(newPoints)) {
    errors.push('Zone extends outside camera feed boundaries');
  }

  // Validate rectangle shape (points should form a proper rectangle)
  const [topLeft, topRight, bottomRight, bottomLeft] = newPoints;
  
  // Check if points form a rectangle (opposite sides should be parallel)
  const topEdgeLength = Math.abs(topRight.x - topLeft.x);
  const bottomEdgeLength = Math.abs(bottomRight.x - bottomLeft.x);
  const leftEdgeLength = Math.abs(bottomLeft.y - topLeft.y);
  const rightEdgeLength = Math.abs(bottomRight.y - topRight.y);
  
  const TOLERANCE = 0.001; // 0.1% tolerance for floating point comparison
  
  if (Math.abs(topEdgeLength - bottomEdgeLength) > TOLERANCE) {
    errors.push('Zone is not a valid rectangle (top and bottom edges must be equal)');
  }
  
  if (Math.abs(leftEdgeLength - rightEdgeLength) > TOLERANCE) {
    errors.push('Zone is not a valid rectangle (left and right edges must be equal)');
  }

  // Check if points are in correct order (clockwise from top-left)
  if (topLeft.x > topRight.x || topLeft.y > bottomLeft.y) {
    errors.push('Zone points are not in correct order');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Check if zones overlap significantly
 */
export function doZonesOverlap(zone1: Zone, zone2: Zone, threshold: number = 0.1): boolean {
  if (zone1.points.length !== 4 || zone2.points.length !== 4) return false;

  const bounds1 = calculateZoneBounds(zone1.points);
  const bounds2 = calculateZoneBounds(zone2.points);

  // Calculate intersection
  const intersectionMinX = Math.max(bounds1.minX, bounds2.minX);
  const intersectionMinY = Math.max(bounds1.minY, bounds2.minY);
  const intersectionMaxX = Math.min(bounds1.maxX, bounds2.maxX);
  const intersectionMaxY = Math.min(bounds1.maxY, bounds2.maxY);

  // Check if there's an intersection
  if (intersectionMinX >= intersectionMaxX || intersectionMinY >= intersectionMaxY) {
    return false;
  }

  // Calculate intersection area
  const intersectionArea = (intersectionMaxX - intersectionMinX) * (intersectionMaxY - intersectionMinY);
  
  // Calculate areas of both zones
  const area1 = bounds1.width * bounds1.height;
  const area2 = bounds2.width * bounds2.height;
  const minArea = Math.min(area1, area2);

  // Check if intersection is significant
  return intersectionArea / minArea > threshold;
}

/**
 * Sanitize zone data with enhanced validation
 */
export function sanitizeZone(zone: Partial<Zone>): Zone | null {
  try {
    // Ensure required fields
    if (!zone.id || !zone.type || !zone.points) {
      return null;
    }

    // Sanitize ID
    const sanitizedId = String(zone.id).trim();
    if (!sanitizedId) {
      return null;
    }

    // Sanitize type
    const sanitizedType = zone.type === 'alarm' ? 'alarm' : 'warning';

    // Sanitize points with enhanced validation
    if (!Array.isArray(zone.points) || zone.points.length === 0) {
      return null;
    }

    const sanitizedPoints = zone.points
      .slice(0, 4) // Ensure max 4 points
      .map((point, index) => {
        if (!point || typeof point !== 'object') {
          console.warn(`Invalid point at index ${index}:`, point);
          return { x: 0, y: 0 };
        }

        const x = Number(point.x);
        const y = Number(point.y);

        // Check for valid numbers
        if (!isFinite(x) || !isFinite(y)) {
          console.warn(`Non-finite coordinates at index ${index}:`, { x: point.x, y: point.y });
          return { x: 0, y: 0 };
        }

        // Clamp to valid range with precision
        const precisionFactor = Math.pow(10, COORDINATE_PRECISION);
        return {
          x: Math.round(Math.max(0, Math.min(1, x)) * precisionFactor) / precisionFactor,
          y: Math.round(Math.max(0, Math.min(1, y)) * precisionFactor) / precisionFactor
        };
      });

    // Ensure we have exactly 4 points
    while (sanitizedPoints.length < 4) {
      sanitizedPoints.push({ x: 0, y: 0 });
    }

    // Sanitize other properties
    const sanitizedZone: Zone = {
      id: sanitizedId,
      type: sanitizedType,
      points: sanitizedPoints,
      visible: Boolean(zone.visible ?? true),
      selected: Boolean(zone.selected ?? false),
      zIndex: Math.max(1, Math.min(1000, Number(zone.zIndex) || 1)) // Clamp z-index
    };

    // Validate the sanitized zone
    const validation = validateZone(sanitizedZone);
    if (!validation.isValid) {
      console.warn('Sanitized zone failed validation:', validation.errors);
      return null;
    }

    return sanitizedZone;
  } catch (error) {
    console.error('Error sanitizing zone:', error);
    return null;
  }
}

/**
 * Validate input data before zone operations
 */
export function validateZoneInput(input: unknown): ZoneValidationResult {
  const errors: string[] = [];

  // Check if input exists
  if (input === null || input === undefined) {
    errors.push('Zone input cannot be null or undefined');
    return { isValid: false, errors };
  }

  // Check if input is an object
  if (typeof input !== 'object') {
    errors.push('Zone input must be an object');
    return { isValid: false, errors };
  }

  // Type assertion for further validation
  const zoneInput = input as Partial<Zone>;

  // Validate required fields
  if (!zoneInput.id) {
    errors.push('Zone ID is required');
  } else if (typeof zoneInput.id !== 'string' || zoneInput.id.trim() === '') {
    errors.push('Zone ID must be a non-empty string');
  }

  if (!zoneInput.type) {
    errors.push('Zone type is required');
  } else if (!['warning', 'alarm'].includes(zoneInput.type)) {
    errors.push('Zone type must be "warning" or "alarm"');
  }

  if (!zoneInput.points) {
    errors.push('Zone points are required');
  } else if (!Array.isArray(zoneInput.points)) {
    errors.push('Zone points must be an array');
  } else if (zoneInput.points.length !== 4) {
    errors.push('Zone must have exactly 4 points');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate zone operation parameters
 */
export function validateZoneOperation(
  operation: 'create' | 'update' | 'delete' | 'move' | 'resize',
  params: unknown
): ZoneValidationResult {
  const errors: string[] = [];

  if (!operation || typeof operation !== 'string') {
    errors.push('Operation type is required');
    return { isValid: false, errors };
  }

  if (!['create', 'update', 'delete', 'move', 'resize'].includes(operation)) {
    errors.push('Invalid operation type');
    return { isValid: false, errors };
  }

  if (params === null || params === undefined) {
    errors.push('Operation parameters are required');
    return { isValid: false, errors };
  }

  // Validate parameters based on operation type
  switch (operation) {
    case 'create':
      if (typeof params !== 'object' || !('type' in params) || !('startPoint' in params) || !('endPoint' in params)) {
        errors.push('Create operation requires type, startPoint, and endPoint');
      }
      break;

    case 'update':
    case 'move':
    case 'resize':
      if (typeof params !== 'object' || !('id' in params)) {
        errors.push(`${operation} operation requires zone ID`);
      }
      break;

    case 'delete':
      if (typeof params !== 'string' && (typeof params !== 'object' || !('id' in params))) {
        errors.push('Delete operation requires zone ID');
      }
      break;
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Create validation error with context
 */
export function createValidationError(
  message: string,
  context?: Record<string, unknown>
): Error {
  const error = new Error(message);
  error.name = 'ZoneValidationError';
  
  if (context) {
    (error as any).context = context;
  }
  
  return error;
}