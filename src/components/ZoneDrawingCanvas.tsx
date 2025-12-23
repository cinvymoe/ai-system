/**
 * ZoneDrawingCanvas Component
 * Handles interactive zone drawing with mouse events and real-time feedback
 * Requirements: 1.3, 2.2
 */

import { useRef, useEffect, useCallback } from 'react';
import './ZoneDrawingCanvas.css';
import { Zone, ZoneType, DrawingState } from '../types/zone';
import { Point } from '../services/aiSettingsService';
import { 
  screenToRelative, 
  relativeToScreen, 
  CanvasDimensions,
  calculateZoneBounds,
  getResizeHandle,
  clampCoordinates,
  createRectanglePoints
} from '../utils/coordinateTransform';

interface ZoneDrawingCanvasProps {
  canvas: HTMLCanvasElement | null;
  dimensions: CanvasDimensions;
  zones: Zone[];
  drawingState: DrawingState;
  drawingMode?: ZoneType | null;
  onDrawingStart?: (type: ZoneType, startPoint: Point) => void;
  onDrawingUpdate?: (currentPoint: Point) => void;
  onDrawingEnd?: () => void;
  onZoneClick?: (zoneId: string, point: Point) => void;
  onZoneResize?: (zoneId: string, newPoints: Point[]) => void;
  onZoneMove?: (zoneId: string, newPoints: Point[]) => void;
  onZoneDelete?: (zoneId: string) => void;
  onManipulationEnd?: () => void;
}

export function ZoneDrawingCanvas({
  canvas,
  dimensions,
  zones,
  drawingState,
  drawingMode = null,
  onDrawingStart,
  onDrawingUpdate,
  onDrawingEnd,
  onZoneClick,
  onZoneResize,
  onZoneMove,
  onZoneDelete,
  onManipulationEnd
}: ZoneDrawingCanvasProps) {
  const animationFrameRef = useRef<number | undefined>(undefined);
  
  // State for zone manipulation
  const manipulationStateRef = useRef<{
    isManipulating: boolean;
    manipulationType: 'resize' | 'move' | null;
    targetZoneId: string | null;
    handle: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center' | null;
    startPoint: Point | null;
    originalPoints: Point[] | null;
  }>({
    isManipulating: false,
    manipulationType: null,
    targetZoneId: null,
    handle: null,
    startPoint: null,
    originalPoints: null
  });

  /**
   * Get mouse position relative to canvas
   */
  const getMousePosition = useCallback((event: MouseEvent): Point | null => {
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    const screenCoord = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };

    return screenToRelative(screenCoord, dimensions);
  }, [canvas, dimensions]);

  /**
   * Check if point is on delete button
   */
  const isPointOnDeleteButton = useCallback((point: Point, zone: Zone): boolean => {
    if (!zone.selected) return false;
    
    const bounds = calculateZoneBounds(zone.points);
    const deleteButtonCenter = { x: bounds.maxX, y: bounds.minY };
    const buttonSize = 0.02; // Relative size
    
    return Math.abs(point.x - deleteButtonCenter.x) <= buttonSize && 
           Math.abs(point.y - deleteButtonCenter.y) <= buttonSize;
  }, []);

  /**
   * Resize zone based on handle and new position
   */
  const resizeZone = useCallback((
    originalPoints: Point[], 
    handle: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right',
    newPosition: Point
  ): Point[] => {
    const [topLeft, topRight, bottomRight, bottomLeft] = originalPoints;
    const clampedPos = clampCoordinates(newPosition);
    
    switch (handle) {
      case 'top-left':
        return createRectanglePoints(clampedPos, bottomRight);
      case 'top-right':
        return createRectanglePoints({ x: clampedPos.x, y: clampedPos.y }, { x: bottomLeft.x, y: bottomRight.y });
      case 'bottom-right':
        return createRectanglePoints(topLeft, clampedPos);
      case 'bottom-left':
        return createRectanglePoints({ x: clampedPos.x, y: topLeft.y }, { x: topRight.x, y: clampedPos.y });
      default:
        return originalPoints;
    }
  }, []);

  /**
   * Move zone by offset
   */
  const moveZone = useCallback((
    originalPoints: Point[],
    startPoint: Point,
    currentPoint: Point
  ): Point[] => {
    const deltaX = currentPoint.x - startPoint.x;
    const deltaY = currentPoint.y - startPoint.y;
    
    return originalPoints.map(point => clampCoordinates({
      x: point.x + deltaX,
      y: point.y + deltaY
    }));
  }, []);

  /**
   * Draw a zone on the canvas with enhanced visual feedback
   */
  const drawZone = useCallback((ctx: CanvasRenderingContext2D, zone: Zone) => {
    if (!zone.visible || zone.points.length !== 4) return;

    const [topLeft, , bottomRight] = zone.points;
    
    // Convert relative coordinates to screen coordinates
    const screenTopLeft = relativeToScreen(topLeft, dimensions);
    const screenBottomRight = relativeToScreen(bottomRight, dimensions);

    // Enhanced zone colors with better visual feedback
    const isWarning = zone.type === 'warning';
    const baseOpacity = zone.selected ? 0.35 : 0.2;
    const strokeOpacity = zone.selected ? 1.0 : 0.8;
    
    // Enhanced color scheme with better contrast
    const fillColor = isWarning 
      ? `rgba(255, 193, 7, ${baseOpacity})` 
      : `rgba(220, 53, 69, ${baseOpacity})`;
    const strokeColor = isWarning 
      ? `rgba(255, 193, 7, ${strokeOpacity})` 
      : `rgba(220, 53, 69, ${strokeOpacity})`;
    const selectedStrokeColor = isWarning 
      ? 'rgba(255, 193, 7, 1)' 
      : 'rgba(220, 53, 69, 1)';

    const width = screenBottomRight.x - screenTopLeft.x;
    const height = screenBottomRight.y - screenTopLeft.y;

    // Enhanced zone rectangle with subtle shadow for depth
    if (zone.selected) {
      // Add subtle shadow for selected zones
      ctx.shadowColor = isWarning ? 'rgba(255, 193, 7, 0.5)' : 'rgba(220, 53, 69, 0.5)';
      ctx.shadowBlur = 8;
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
    }

    // Draw zone rectangle with enhanced visual feedback
    ctx.fillStyle = fillColor;
    ctx.fillRect(screenTopLeft.x, screenTopLeft.y, width, height);

    // Reset shadow
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;

    // Enhanced border with animated effect for selected zones
    if (zone.selected) {
      // Animated border effect using time-based opacity
      const time = Date.now() / 1000;
      const pulseOpacity = 0.7 + 0.3 * Math.sin(time * 3);
      
      ctx.strokeStyle = isWarning 
        ? `rgba(255, 193, 7, ${pulseOpacity})` 
        : `rgba(220, 53, 69, ${pulseOpacity})`;
      ctx.lineWidth = 4;
      ctx.strokeRect(screenTopLeft.x - 1, screenTopLeft.y - 1, width + 2, height + 2);
      
      // Inner border for definition
      ctx.strokeStyle = selectedStrokeColor;
      ctx.lineWidth = 2;
      ctx.strokeRect(screenTopLeft.x, screenTopLeft.y, width, height);
    } else {
      // Standard border for non-selected zones
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 2;
      ctx.strokeRect(screenTopLeft.x, screenTopLeft.y, width, height);
    }

    // Add subtle inner border for better distinction in overlapping zones
    if (!zone.selected) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1;
      ctx.strokeRect(screenTopLeft.x + 1, screenTopLeft.y + 1, width - 2, height - 2);
    }

    // Enhanced selection handles with better visual feedback
    if (zone.selected) {
      const handleSize = 8;
      const time = Date.now() / 1000;
      
      // Enhanced corner handles with glow effect
      zone.points.forEach(point => {
        const screenPoint = relativeToScreen(point, dimensions);
        
        // Glow effect for handles
        ctx.shadowColor = selectedStrokeColor;
        ctx.shadowBlur = 6;
        
        // Handle background (white)
        ctx.fillStyle = 'white';
        ctx.fillRect(
          screenPoint.x - handleSize / 2,
          screenPoint.y - handleSize / 2,
          handleSize,
          handleSize
        );
        
        // Handle border with zone color
        ctx.strokeStyle = selectedStrokeColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(
          screenPoint.x - handleSize / 2,
          screenPoint.y - handleSize / 2,
          handleSize,
          handleSize
        );
        
        // Reset shadow
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
      });

      // Enhanced delete button with hover animation
      const bounds = calculateZoneBounds(zone.points);
      const deleteButtonPos = relativeToScreen({ x: bounds.maxX, y: bounds.minY }, dimensions);
      const buttonSize = 18;
      const pulseScale = 1 + 0.1 * Math.sin(time * 4);
      const scaledSize = buttonSize * pulseScale;
      
      // Delete button shadow
      ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
      ctx.shadowBlur = 4;
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
      
      // Delete button background with enhanced styling
      ctx.fillStyle = 'rgba(220, 53, 69, 0.95)';
      ctx.fillRect(
        deleteButtonPos.x - scaledSize / 2,
        deleteButtonPos.y - scaledSize / 2,
        scaledSize,
        scaledSize
      );
      
      // Delete button border
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.lineWidth = 1;
      ctx.stroke();
      
      // Reset shadow
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
      
      // Enhanced delete button X with better visibility
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      const offset = 5;
      ctx.beginPath();
      ctx.moveTo(deleteButtonPos.x - offset, deleteButtonPos.y - offset);
      ctx.lineTo(deleteButtonPos.x + offset, deleteButtonPos.y + offset);
      ctx.moveTo(deleteButtonPos.x + offset, deleteButtonPos.y - offset);
      ctx.lineTo(deleteButtonPos.x - offset, deleteButtonPos.y + offset);
      ctx.stroke();
      ctx.lineCap = 'butt'; // Reset line cap
    }

    // Draw zone label
    if (zone.selected || zone.type === 'alarm') {
      const bounds = calculateZoneBounds(zone.points);
      const centerScreen = relativeToScreen(
        { x: bounds.minX + bounds.width / 2, y: bounds.minY + bounds.height / 2 },
        dimensions
      );

      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.font = '12px Arial';
      const text = zone.type.toUpperCase();
      const textMetrics = ctx.measureText(text);
      const textWidth = textMetrics.width;
      const textHeight = 12;

      // Draw background for text
      ctx.fillRect(
        centerScreen.x - textWidth / 2 - 4,
        centerScreen.y - textHeight / 2 - 2,
        textWidth + 8,
        textHeight + 4
      );

      // Draw text
      ctx.fillStyle = 'white';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, centerScreen.x, centerScreen.y);
    }
  }, [dimensions]);

  /**
   * Draw the current drawing rectangle with enhanced visual feedback
   */
  const drawCurrentDrawing = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!drawingState.isDrawing || !drawingState.startPoint || !drawingState.currentPoint) {
      return;
    }

    const startScreen = relativeToScreen(drawingState.startPoint, dimensions);
    const currentScreen = relativeToScreen(drawingState.currentPoint, dimensions);

    // Calculate rectangle bounds
    const minX = Math.min(startScreen.x, currentScreen.x);
    const minY = Math.min(startScreen.y, currentScreen.y);
    const width = Math.abs(currentScreen.x - startScreen.x);
    const height = Math.abs(currentScreen.y - startScreen.y);

    // Enhanced drawing colors with animation
    const isWarning = drawingState.drawingType === 'warning';
    const time = Date.now() / 1000;
    const pulseOpacity = 0.7 + 0.3 * Math.sin(time * 4);
    
    const strokeColor = isWarning 
      ? `rgba(255, 193, 7, ${pulseOpacity})` 
      : `rgba(220, 53, 69, ${pulseOpacity})`;
    const fillColor = isWarning 
      ? 'rgba(255, 193, 7, 0.15)' 
      : 'rgba(220, 53, 69, 0.15)';

    // Enhanced drawing rectangle with glow effect
    ctx.shadowColor = isWarning ? 'rgba(255, 193, 7, 0.4)' : 'rgba(220, 53, 69, 0.4)';
    ctx.shadowBlur = 8;

    // Draw filled rectangle
    ctx.fillStyle = fillColor;
    ctx.fillRect(minX, minY, width, height);

    // Reset shadow for border
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;

    // Enhanced animated border
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 3;
    
    // Animated dashed line with moving pattern
    const dashOffset = (time * 20) % 20;
    ctx.setLineDash([10, 10]);
    ctx.lineDashOffset = -dashOffset;
    
    ctx.strokeRect(minX, minY, width, height);

    // Add corner indicators for better visual feedback
    const cornerSize = 12;
    ctx.strokeStyle = isWarning ? 'rgba(255, 193, 7, 1)' : 'rgba(220, 53, 69, 1)';
    ctx.lineWidth = 2;
    ctx.setLineDash([]); // Solid lines for corners
    
    // Draw corner indicators
    const corners = [
      { x: minX, y: minY }, // top-left
      { x: minX + width, y: minY }, // top-right
      { x: minX + width, y: minY + height }, // bottom-right
      { x: minX, y: minY + height } // bottom-left
    ];
    
    corners.forEach(corner => {
      // Horizontal line
      ctx.beginPath();
      ctx.moveTo(corner.x - cornerSize / 2, corner.y);
      ctx.lineTo(corner.x + cornerSize / 2, corner.y);
      ctx.stroke();
      
      // Vertical line
      ctx.beginPath();
      ctx.moveTo(corner.x, corner.y - cornerSize / 2);
      ctx.lineTo(corner.x, corner.y + cornerSize / 2);
      ctx.stroke();
    });

    // Reset line dash
    ctx.setLineDash([]);
    ctx.lineDashOffset = 0;

    // Draw dimensions and coordinates text
    ctx.font = '11px Arial';
    
    // Calculate relative dimensions for display
    const relativeWidth = (width / dimensions.width);
    const relativeHeight = (height / dimensions.height);
    const area = relativeWidth * relativeHeight;
    
    // Dimension text
    const dimensionText = `${(relativeWidth * 100).toFixed(1)}% × ${(relativeHeight * 100).toFixed(1)}%`;
    const areaText = `面积: ${(area * 100).toFixed(2)}%`;
    
    // Coordinate text
    const startRelative = drawingState.startPoint;
    const currentRelative = drawingState.currentPoint;
    const coordText = `(${(startRelative.x * 100).toFixed(1)}, ${(startRelative.y * 100).toFixed(1)}) → (${(currentRelative.x * 100).toFixed(1)}, ${(currentRelative.y * 100).toFixed(1)})`;
    
    // Draw dimension text above rectangle
    const textX = minX + width / 2;
    const textY = minY - 35;
    
    // Background for dimension text
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    const dimMetrics = ctx.measureText(dimensionText);
    ctx.fillRect(textX - dimMetrics.width / 2 - 4, textY - 12, dimMetrics.width + 8, 14);
    
    // Dimension text
    ctx.fillStyle = 'white';
    ctx.textAlign = 'center';
    ctx.fillText(dimensionText, textX, textY);
    
    // Area text
    const areaY = textY + 16;
    const areaMetrics = ctx.measureText(areaText);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(textX - areaMetrics.width / 2 - 4, areaY - 12, areaMetrics.width + 8, 14);
    ctx.fillStyle = 'white';
    ctx.fillText(areaText, textX, areaY);
    
    // Coordinate text below rectangle
    const coordY = minY + height + 20;
    const coordMetrics = ctx.measureText(coordText);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(textX - coordMetrics.width / 2 - 4, coordY - 12, coordMetrics.width + 8, 14);
    ctx.fillStyle = 'white';
    ctx.fillText(coordText, textX, coordY);
  }, [drawingState, dimensions]);

  /**
   * Render all zones and drawing state
   */
  const render = useCallback(() => {
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, dimensions.width, dimensions.height);

    // Sort zones by z-index (lower z-index renders first, higher z-index on top)
    const sortedZones = [...zones].sort((a, b) => a.zIndex - b.zIndex);

    // Draw existing zones in z-index order
    sortedZones.forEach(zone => drawZone(ctx, zone));

    // Draw current drawing if in progress (always on top)
    drawCurrentDrawing(ctx);
  }, [canvas, dimensions, zones, drawZone, drawCurrentDrawing]);

  /**
   * Handle mouse down event
   */
  const handleMouseDown = useCallback((event: MouseEvent) => {
    event.preventDefault();
    const mousePos = getMousePosition(event);
    if (!mousePos) return;

    // Sort zones by z-index (highest first) to handle overlapping zones properly
    const sortedZones = [...zones]
      .filter(zone => zone.visible)
      .sort((a, b) => b.zIndex - a.zIndex);

    // Check for zone interactions, starting with topmost zones
    for (const zone of sortedZones) {
      // Check delete button click (only for selected zones)
      if (zone.selected && isPointOnDeleteButton(mousePos, zone)) {
        if (onZoneDelete) {
          onZoneDelete(zone.id);
        }
        return;
      }

      // Check resize handles (only for selected zones)
      if (zone.selected) {
        const handle = getResizeHandle(mousePos, zone.points, 0.02);
        if (handle && handle !== 'center') {
          manipulationStateRef.current = {
            isManipulating: true,
            manipulationType: 'resize',
            targetZoneId: zone.id,
            handle,
            startPoint: mousePos,
            originalPoints: [...zone.points]
          };
          return;
        }
      }

      // Check for zone area click
      const bounds = calculateZoneBounds(zone.points);
      if (mousePos.x >= bounds.minX && mousePos.x <= bounds.maxX &&
          mousePos.y >= bounds.minY && mousePos.y <= bounds.maxY) {
        
        if (zone.selected) {
          // Start moving the selected zone
          manipulationStateRef.current = {
            isManipulating: true,
            manipulationType: 'move',
            targetZoneId: zone.id,
            handle: 'center',
            startPoint: mousePos,
            originalPoints: [...zone.points]
          };
        } else {
          // Select the topmost zone at this position
          if (onZoneClick) {
            onZoneClick(zone.id, mousePos);
          }
        }
        return;
      }
    }

    // Start drawing if we have a drawing type set and no zone was clicked
    if (drawingMode && onDrawingStart) {
      onDrawingStart(drawingMode, mousePos);
    }
  }, [getMousePosition, zones, drawingMode, onDrawingStart, onZoneClick, onZoneDelete, isPointOnDeleteButton]);

  /**
   * Handle mouse move event
   */
  const handleMouseMove = useCallback((event: MouseEvent) => {
    const mousePos = getMousePosition(event);
    if (!mousePos) return;

    const manipulation = manipulationStateRef.current;

    // Handle zone manipulation
    if (manipulation.isManipulating && manipulation.targetZoneId && manipulation.originalPoints) {
      if (manipulation.manipulationType === 'resize' && manipulation.handle && manipulation.handle !== 'center') {
        const newPoints = resizeZone(manipulation.originalPoints, manipulation.handle, mousePos);
        if (onZoneResize) {
          onZoneResize(manipulation.targetZoneId, newPoints);
        }
      } else if (manipulation.manipulationType === 'move' && manipulation.startPoint) {
        const newPoints = moveZone(manipulation.originalPoints, manipulation.startPoint, mousePos);
        if (onZoneMove) {
          onZoneMove(manipulation.targetZoneId, newPoints);
        }
      }
      return;
    }

    // Update drawing if in progress
    if (drawingState.isDrawing && onDrawingUpdate) {
      onDrawingUpdate(mousePos);
      return;
    }

    // Update cursor based on hover state with enhanced visual feedback
    if (canvas) {
      let cursor = 'default';
      let canvasClass = '';

      if (drawingMode) {
        // Enhanced cursor for drawing mode with visual indication
        cursor = 'crosshair';
        canvasClass = 'zone-drawing-active';
        
        // Add subtle glow effect to indicate drawing mode
        canvas.style.boxShadow = drawingMode === 'warning' 
          ? '0 0 20px rgba(255, 193, 7, 0.3)' 
          : '0 0 20px rgba(220, 53, 69, 0.3)';
      } else {
        // Remove drawing mode effects
        canvas.style.boxShadow = 'none';
        
        // Check for zone interactions, prioritizing topmost zones
        const sortedZones = [...zones]
          .filter(zone => zone.visible)
          .sort((a, b) => b.zIndex - a.zIndex);

        for (const zone of sortedZones) {
          // Check delete button (highest priority)
          if (zone.selected && isPointOnDeleteButton(mousePos, zone)) {
            cursor = 'pointer';
            canvasClass = 'zone-delete-hover';
            break;
          }

          // Check resize handles (second priority) with enhanced cursors
          if (zone.selected) {
            const handle = getResizeHandle(mousePos, zone.points, 0.02);
            if (handle && handle !== 'center') {
              // More precise resize cursors
              switch (handle) {
                case 'top-left':
                case 'bottom-right':
                  cursor = 'nw-resize';
                  break;
                case 'top-right':
                case 'bottom-left':
                  cursor = 'ne-resize';
                  break;
                default:
                  cursor = 'default';
              }
              canvasClass = 'zone-resize-hover';
              break;
            }
          }

          // Check zone area (lowest priority) with enhanced feedback
          const bounds = calculateZoneBounds(zone.points);
          if (mousePos.x >= bounds.minX && mousePos.x <= bounds.maxX &&
              mousePos.y >= bounds.minY && mousePos.y <= bounds.maxY) {
            cursor = zone.selected ? 'move' : 'pointer';
            canvasClass = zone.selected ? 'zone-move-hover' : 'zone-select-hover';
            break;
          }
        }
      }

      // Apply cursor and visual feedback classes
      canvas.style.cursor = cursor;
      canvas.className = `zone-canvas ${canvasClass}`;
    }
  }, [getMousePosition, drawingState.isDrawing, onDrawingUpdate, canvas, zones, drawingMode, 
      resizeZone, moveZone, onZoneResize, onZoneMove, isPointOnDeleteButton]);

  /**
   * Handle mouse up event
   */
  const handleMouseUp = useCallback((event: MouseEvent) => {
    event.preventDefault();

    // Finish manipulation if in progress
    if (manipulationStateRef.current.isManipulating) {
      manipulationStateRef.current = {
        isManipulating: false,
        manipulationType: null,
        targetZoneId: null,
        handle: null,
        startPoint: null,
        originalPoints: null
      };
      
      // Notify parent that manipulation ended (for persistence)
      if (onManipulationEnd) {
        onManipulationEnd();
      }
      return;
    }

    // Finish drawing if in progress
    if (drawingState.isDrawing && onDrawingEnd) {
      onDrawingEnd();
    }
  }, [drawingState.isDrawing, onDrawingEnd, onManipulationEnd]);

  /**
   * Update cursor based on drawing mode
   */
  useEffect(() => {
    if (canvas) {
      canvas.style.cursor = drawingMode ? 'crosshair' : 'default';
    }
  }, [canvas, drawingMode]);

  /**
   * Animation loop for smooth rendering
   */
  useEffect(() => {
    const animate = () => {
      render();
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    if (canvas && dimensions.width > 0 && dimensions.height > 0) {
      animate();
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [canvas, dimensions, render]);

  /**
   * Set up mouse event listeners
   */
  useEffect(() => {
    if (!canvas) return;

    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);

    // Global mouse up to handle mouse release outside canvas
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [canvas, handleMouseDown, handleMouseMove, handleMouseUp]);

  return null; // This component doesn't render anything directly
}