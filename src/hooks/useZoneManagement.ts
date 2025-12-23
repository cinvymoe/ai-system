/**
 * Zone Management Hook
 * Manages zone state, drawing, and manipulation
 */

import { useState, useCallback } from 'react';
import { Zone, ZoneType, DrawingState, ZoneCreateParams, ZoneUpdateParams, ZoneManipulationMode } from '../types/zone';
import { Point } from '../services/aiSettingsService';
import { createRectanglePoints, validateZoneCoordinates } from '../utils/coordinateTransform';

/**
 * Zone management hook return type
 */
export interface UseZoneManagementReturn {
  // State
  zones: Zone[];
  drawingState: DrawingState;
  manipulationMode: ZoneManipulationMode;
  selectedZoneId: string | null;

  // Zone operations
  createZone: (params: ZoneCreateParams) => Zone | null;
  updateZone: (params: ZoneUpdateParams) => void;
  deleteZone: (zoneId: string) => void;
  selectZone: (zoneId: string | null) => void;
  toggleZoneVisibility: (zoneId: string) => void;
  clearZones: () => void;
  setZones: (zones: Zone[]) => void;
  resizeZone: (zoneId: string, newPoints: Point[]) => void;
  moveZone: (zoneId: string, newPoints: Point[]) => void;
  bringToFront: (zoneId: string) => void;
  sendToBack: (zoneId: string) => void;

  // Drawing operations
  startDrawing: (type: ZoneType, startPoint: Point) => void;
  updateDrawing: (currentPoint: Point) => void;
  finishDrawing: () => Zone | null;
  cancelDrawing: () => void;

  // Mode management
  setManipulationMode: (mode: ZoneManipulationMode) => void;
  
  // Utility
  getZoneById: (zoneId: string) => Zone | undefined;
  getVisibleZones: () => Zone[];
  getZonesByType: (type: ZoneType) => Zone[];
}

/**
 * Zone management hook
 */
export function useZoneManagement(): UseZoneManagementReturn {
  const [zones, setZones] = useState<Zone[]>([]);
  const [drawingState, setDrawingState] = useState<DrawingState>({
    isDrawing: false,
    drawingType: null,
    startPoint: null,
    currentPoint: null
  });
  const [manipulationMode, setManipulationMode] = useState<ZoneManipulationMode>('none');
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);

  /**
   * Generate unique zone ID
   */
  const generateZoneId = useCallback((): string => {
    return `zone-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }, []);

  /**
   * Get next z-index for new zones
   */
  const getNextZIndex = useCallback((): number => {
    if (zones.length === 0) return 1;
    return Math.max(...zones.map(zone => zone.zIndex)) + 1;
  }, [zones]);

  /**
   * Create a new zone with enhanced validation
   */
  const createZone = useCallback((params: ZoneCreateParams): Zone | null => {
    try {
      // Validate input parameters
      if (!params || typeof params !== 'object') {
        console.error('Invalid zone creation parameters:', params);
        return null;
      }

      const { type, startPoint, endPoint } = params;
      
      // Validate zone type
      if (!type || !['warning', 'alarm'].includes(type)) {
        console.error('Invalid zone type:', type);
        return null;
      }

      // Validate points exist
      if (!startPoint || !endPoint) {
        console.error('Missing start or end point:', { startPoint, endPoint });
        return null;
      }

      // Enhanced coordinate validation
      const { 
        validateDrawingCoordinates, 
        validateCoordinateBounds,
        validateZoneInput 
      } = require('../utils/zoneValidation');
      
      // Validate individual points
      const startValidation = validateCoordinateBounds(startPoint);
      if (!startValidation.isValid) {
        console.warn('Invalid start point:', startValidation.errors);
        return null;
      }

      const endValidation = validateCoordinateBounds(endPoint);
      if (!endValidation.isValid) {
        console.warn('Invalid end point:', endValidation.errors);
        return null;
      }

      // Validate drawing coordinates
      const validation = validateDrawingCoordinates(startPoint, endPoint);
      if (!validation.isValid) {
        console.warn('Invalid zone coordinates:', validation.errors);
        return null;
      }
      
      // Create rectangle points
      const points = createRectanglePoints(startPoint, endPoint);
      
      // Double-check with coordinate validation
      if (!validateZoneCoordinates(points)) {
        console.warn('Invalid zone coordinates after point creation');
        return null;
      }

      // Create new zone object
      const newZone: Zone = {
        id: generateZoneId(),
        type,
        points,
        visible: true,
        selected: false,
        zIndex: getNextZIndex()
      };

      // Validate the complete zone object
      const zoneValidation = validateZoneInput(newZone);
      if (!zoneValidation.isValid) {
        console.error('Created zone failed validation:', zoneValidation.errors);
        return null;
      }

      setZones((prev: Zone[]) => [...prev, newZone]);
      return newZone;
    } catch (error) {
      console.error('Error creating zone:', error);
      return null;
    }
  }, [generateZoneId, getNextZIndex]);

  /**
   * Update an existing zone with enhanced validation
   */
  const updateZone = useCallback((params: ZoneUpdateParams): void => {
    try {
      // Validate input parameters
      if (!params || typeof params !== 'object' || !params.id) {
        console.error('Invalid zone update parameters:', params);
        return;
      }

      const { id, points, visible, selected, zIndex } = params;
      
      // Validate zone ID
      if (typeof id !== 'string' || id.trim() === '') {
        console.error('Invalid zone ID for update:', id);
        return;
      }

      setZones((prev: Zone[]) => prev.map((zone: Zone) => {
        if (zone.id !== id) return zone;
        
        const updates: Partial<Zone> = {};
        
        // Validate and update points if provided
        if (points !== undefined) {
          // Enhanced validation for new points
          const { 
            validateZoneManipulation, 
            validateZoneDimensions,
            validateCoordinateBounds 
          } = require('../utils/zoneValidation');
          
          // Validate points array
          if (!Array.isArray(points) || points.length !== 4) {
            console.warn('Invalid points array for zone update:', points);
            return zone; // Don't update if points are invalid
          }

          // Validate each point
          for (let i = 0; i < points.length; i++) {
            const pointValidation = validateCoordinateBounds(points[i]);
            if (!pointValidation.isValid) {
              console.warn(`Invalid point ${i} in zone update:`, pointValidation.errors);
              return zone; // Don't update if any point is invalid
            }
          }

          // Validate zone dimensions
          const dimensionValidation = validateZoneDimensions(points);
          if (!dimensionValidation.isValid) {
            console.warn('Zone dimension validation failed:', dimensionValidation.errors);
            return zone; // Don't update if dimensions are invalid
          }

          // Validate manipulation
          const validation = validateZoneManipulation(zone, points);
          if (validation.isValid) {
            updates.points = points;
          } else {
            console.warn('Zone manipulation validation failed:', validation.errors);
            return zone; // Don't update points if validation fails
          }
        }
        
        // Validate and update other properties
        if (visible !== undefined) {
          if (typeof visible === 'boolean') {
            updates.visible = visible;
          } else {
            console.warn('Invalid visible value for zone update:', visible);
          }
        }
        
        if (selected !== undefined) {
          if (typeof selected === 'boolean') {
            updates.selected = selected;
          } else {
            console.warn('Invalid selected value for zone update:', selected);
          }
        }
        
        if (zIndex !== undefined) {
          if (typeof zIndex === 'number' && isFinite(zIndex) && zIndex >= 1) {
            updates.zIndex = Math.max(1, Math.min(1000, Math.floor(zIndex))); // Clamp and round
          } else {
            console.warn('Invalid zIndex value for zone update:', zIndex);
          }
        }
        
        return { ...zone, ...updates };
      }));
    } catch (error) {
      console.error('Error updating zone:', error);
    }
  }, []);

  /**
   * Delete a zone
   */
  const deleteZone = useCallback((zoneId: string): void => {
    setZones((prev: Zone[]) => prev.filter((zone: Zone) => zone.id !== zoneId));
    if (selectedZoneId === zoneId) {
      setSelectedZoneId(null);
    }
  }, [selectedZoneId]);

  /**
   * Select a zone
   */
  const selectZone = useCallback((zoneId: string | null): void => {
    setSelectedZoneId(zoneId);
    
    // Update selected state for all zones
    setZones((prev: Zone[]) => prev.map((zone: Zone) => ({
      ...zone,
      selected: zone.id === zoneId
    })));

    // Bring selected zone to front for better visibility and interaction
    if (zoneId) {
      const maxZIndex = Math.max(...zones.map(zone => zone.zIndex));
      updateZone({ id: zoneId, zIndex: maxZIndex + 1 });
    }
  }, [zones, updateZone]);

  /**
   * Toggle zone visibility
   */
  const toggleZoneVisibility = useCallback((zoneId: string): void => {
    setZones((prev: Zone[]) => prev.map((zone: Zone) => 
      zone.id === zoneId ? { ...zone, visible: !zone.visible } : zone
    ));
  }, []);

  /**
   * Clear all zones
   */
  const clearZones = useCallback((): void => {
    setZones([]);
    setSelectedZoneId(null);
  }, []);

  /**
   * Set zones (for loading from external source)
   */
  const setZonesExternal = useCallback((newZones: Zone[]): void => {
    setZones(newZones);
    setSelectedZoneId(null);
  }, []);

  /**
   * Start drawing a new zone
   */
  const startDrawing = useCallback((type: ZoneType, startPoint: Point): void => {
    setDrawingState({
      isDrawing: true,
      drawingType: type,
      startPoint,
      currentPoint: startPoint
    });
    setManipulationMode('drawing');
  }, []);

  /**
   * Update drawing with current mouse position
   */
  const updateDrawing = useCallback((currentPoint: Point): void => {
    setDrawingState((prev: DrawingState) => {
      if (!prev.isDrawing) return prev;
      return { ...prev, currentPoint };
    });
  }, []);

  /**
   * Finish drawing and create zone
   */
  const finishDrawing = useCallback((): Zone | null => {
    if (!drawingState.isDrawing || !drawingState.startPoint || !drawingState.currentPoint || !drawingState.drawingType) {
      return null;
    }

    const zone = createZone({
      type: drawingState.drawingType,
      startPoint: drawingState.startPoint,
      endPoint: drawingState.currentPoint
    });

    // Reset drawing state
    setDrawingState({
      isDrawing: false,
      drawingType: null,
      startPoint: null,
      currentPoint: null
    });
    setManipulationMode('none');

    return zone;
  }, [drawingState, createZone]);

  /**
   * Cancel drawing
   */
  const cancelDrawing = useCallback((): void => {
    setDrawingState({
      isDrawing: false,
      drawingType: null,
      startPoint: null,
      currentPoint: null
    });
    setManipulationMode('none');
  }, []);

  /**
   * Get zone by ID
   */
  const getZoneById = useCallback((zoneId: string): Zone | undefined => {
    return zones.find((zone: Zone) => zone.id === zoneId);
  }, [zones]);

  /**
   * Get visible zones
   */
  const getVisibleZones = useCallback((): Zone[] => {
    return zones.filter((zone: Zone) => zone.visible);
  }, [zones]);

  /**
   * Get zones by type
   */
  const getZonesByType = useCallback((type: ZoneType): Zone[] => {
    return zones.filter((zone: Zone) => zone.type === type);
  }, [zones]);

  /**
   * Resize a zone
   */
  const resizeZone = useCallback((zoneId: string, newPoints: Point[]): void => {
    updateZone({ id: zoneId, points: newPoints });
  }, [updateZone]);

  /**
   * Move a zone
   */
  const moveZone = useCallback((zoneId: string, newPoints: Point[]): void => {
    updateZone({ id: zoneId, points: newPoints });
  }, [updateZone]);

  /**
   * Bring zone to front (highest z-index)
   */
  const bringToFront = useCallback((zoneId: string): void => {
    const maxZIndex = Math.max(...zones.map(zone => zone.zIndex));
    updateZone({ id: zoneId, zIndex: maxZIndex + 1 });
  }, [zones, updateZone]);

  /**
   * Send zone to back (lowest z-index)
   */
  const sendToBack = useCallback((zoneId: string): void => {
    const minZIndex = Math.min(...zones.map(zone => zone.zIndex));
    updateZone({ id: zoneId, zIndex: minZIndex - 1 });
  }, [zones, updateZone]);

  return {
    // State
    zones,
    drawingState,
    manipulationMode,
    selectedZoneId,

    // Zone operations
    createZone,
    updateZone,
    deleteZone,
    selectZone,
    toggleZoneVisibility,
    clearZones,
    setZones: setZonesExternal,
    resizeZone,
    moveZone,
    bringToFront,
    sendToBack,

    // Drawing operations
    startDrawing,
    updateDrawing,
    finishDrawing,
    cancelDrawing,

    // Mode management
    setManipulationMode,

    // Utility
    getZoneById,
    getVisibleZones,
    getZonesByType
  };
}