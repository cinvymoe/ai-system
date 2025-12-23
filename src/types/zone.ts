/**
 * Zone Management Types and Interfaces
 * Core types for camera alert zone functionality
 */

import { Point } from '../services/aiSettingsService';

/**
 * Zone type enumeration
 */
export type ZoneType = 'warning' | 'alarm';

/**
 * Zone interface for UI state management
 */
export interface Zone {
  id: string;
  type: ZoneType;
  points: Point[]; // 4 corners: top-left, top-right, bottom-right, bottom-left
  visible: boolean;
  selected: boolean;
  zIndex: number; // Layer order for overlapping zones (higher values render on top)
}

/**
 * Drawing state management interface
 */
export interface DrawingState {
  isDrawing: boolean;
  drawingType: ZoneType | null;
  startPoint: Point | null;
  currentPoint: Point | null;
}

/**
 * Zone creation parameters
 */
export interface ZoneCreateParams {
  type: ZoneType;
  startPoint: Point;
  endPoint: Point;
}

/**
 * Zone update parameters
 */
export interface ZoneUpdateParams {
  id: string;
  points?: Point[];
  visible?: boolean;
  selected?: boolean;
  zIndex?: number;
}

/**
 * Zone manipulation mode
 */
export type ZoneManipulationMode = 'none' | 'drawing' | 'selecting' | 'resizing' | 'moving';

/**
 * Zone interaction event
 */
export interface ZoneInteractionEvent {
  type: 'click' | 'drag' | 'resize' | 'delete';
  zoneId: string;
  point?: Point;
  handle?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
}

/**
 * Zone validation result
 */
export interface ZoneValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Zone bounds interface
 */
export interface ZoneBounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  width: number;
  height: number;
}