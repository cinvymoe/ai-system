/**
 * Coordinate Transformation Utilities
 * Handles conversion between screen coordinates and relative coordinates (0-1)
 */

import { Point } from '../services/aiSettingsService';
import { ZoneBounds } from '../types/zone';

/**
 * Screen coordinate interface
 */
export interface ScreenCoordinate {
  x: number; // pixel coordinate
  y: number; // pixel coordinate
}

/**
 * Canvas dimensions interface
 */
export interface CanvasDimensions {
  width: number;
  height: number;
}

/**
 * Convert screen coordinates to relative coordinates (0-1)
 */
export function screenToRelative(
  screenCoord: ScreenCoordinate,
  canvasDimensions: CanvasDimensions
): Point {
  return {
    x: Math.max(0, Math.min(1, screenCoord.x / canvasDimensions.width)),
    y: Math.max(0, Math.min(1, screenCoord.y / canvasDimensions.height))
  };
}

/**
 * Convert relative coordinates (0-1) to screen coordinates
 */
export function relativeToScreen(
  relativeCoord: Point,
  canvasDimensions: CanvasDimensions
): ScreenCoordinate {
  return {
    x: relativeCoord.x * canvasDimensions.width,
    y: relativeCoord.y * canvasDimensions.height
  };
}

/**
 * Create rectangle points from start and end coordinates
 */
export function createRectanglePoints(startPoint: Point, endPoint: Point): Point[] {
  const minX = Math.min(startPoint.x, endPoint.x);
  const minY = Math.min(startPoint.y, endPoint.y);
  const maxX = Math.max(startPoint.x, endPoint.x);
  const maxY = Math.max(startPoint.y, endPoint.y);

  return [
    { x: minX, y: minY }, // top-left
    { x: maxX, y: minY }, // top-right
    { x: maxX, y: maxY }, // bottom-right
    { x: minX, y: maxY }  // bottom-left
  ];
}

/**
 * Calculate zone bounds from points
 */
export function calculateZoneBounds(points: Point[]): ZoneBounds {
  if (points.length === 0) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 };
  }

  const xs = points.map(p => p.x);
  const ys = points.map(p => p.y);
  
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const maxX = Math.max(...xs);
  const maxY = Math.max(...ys);

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY
  };
}

/**
 * Check if a point is inside a zone
 */
export function isPointInZone(point: Point, zonePoints: Point[]): boolean {
  if (zonePoints.length !== 4) return false;

  const bounds = calculateZoneBounds(zonePoints);
  return (
    point.x >= bounds.minX &&
    point.x <= bounds.maxX &&
    point.y >= bounds.minY &&
    point.y <= bounds.maxY
  );
}

/**
 * Get resize handle at point
 */
export function getResizeHandle(
  point: Point,
  zonePoints: Point[],
  handleSize: number = 0.02
): 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center' | null {
  if (zonePoints.length !== 4) return null;

  const [topLeft, topRight, bottomRight, bottomLeft] = zonePoints;
  // Check corner handles
  if (isPointNearHandle(point, topLeft, handleSize)) return 'top-left';
  if (isPointNearHandle(point, topRight, handleSize)) return 'top-right';
  if (isPointNearHandle(point, bottomRight, handleSize)) return 'bottom-right';
  if (isPointNearHandle(point, bottomLeft, handleSize)) return 'bottom-left';

  // Check center (for moving)
  if (isPointInZone(point, zonePoints)) return 'center';

  return null;
}

/**
 * Check if point is near a handle
 */
function isPointNearHandle(point: Point, handle: Point, handleSize: number): boolean {
  const dx = Math.abs(point.x - handle.x);
  const dy = Math.abs(point.y - handle.y);
  return dx <= handleSize && dy <= handleSize;
}

/**
 * Validate zone coordinates
 */
export function validateZoneCoordinates(points: Point[]): boolean {
  if (points.length !== 4) return false;

  // Check all points are within bounds
  for (const point of points) {
    if (point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) {
      return false;
    }
  }

  // Check minimum size
  const bounds = calculateZoneBounds(points);
  const minSize = 0.01; // 1% minimum size
  return bounds.width >= minSize && bounds.height >= minSize;
}

/**
 * Clamp coordinates to valid range
 */
export function clampCoordinates(point: Point): Point {
  return {
    x: Math.max(0, Math.min(1, point.x)),
    y: Math.max(0, Math.min(1, point.y))
  };
}

/**
 * Calculate distance between two points
 */
export function calculateDistance(point1: Point, point2: Point): number {
  const dx = point2.x - point1.x;
  const dy = point2.y - point1.y;
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Calculate zone area from points (as percentage of total area)
 */
export function calculateZoneArea(points: Point[]): number {
  if (points.length !== 4) return 0;
  
  const bounds = calculateZoneBounds(points);
  return bounds.width * bounds.height;
}

/**
 * Format coordinate value for display
 */
export function formatCoordinate(value: number): string {
  return (value * 100).toFixed(1);
}