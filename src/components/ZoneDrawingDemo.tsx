/**
 * ZoneDrawingDemo Component
 * Demonstrates the integration of CameraFeedViewer with ZoneDrawingCanvas
 * This shows how the zone drawing functionality works in practice
 */

import { useState, useCallback } from 'react';
import { CameraFeedViewer } from './CameraFeedViewer';
import { ZoneDrawingCanvas } from './ZoneDrawingCanvas';
import { useZoneManagement } from '../hooks/useZoneManagement';
import { Camera } from '../services/cameraService';
import { ZoneType } from '../types/zone';
import { CanvasDimensions } from '../utils/coordinateTransform';

interface ZoneDrawingDemoProps {
  camera: Camera | null;
}

export function ZoneDrawingDemo({ camera }: ZoneDrawingDemoProps) {
  const [canvas, setCanvas] = useState<HTMLCanvasElement | null>(null);
  const [dimensions, setDimensions] = useState<CanvasDimensions>({ width: 0, height: 0 });
  const [drawingMode, setDrawingMode] = useState<ZoneType | null>(null);

  const {
    zones,
    drawingState,
    startDrawing,
    updateDrawing,
    finishDrawing,
    selectZone,
    deleteZone,
    toggleZoneVisibility
  } = useZoneManagement();

  /**
   * Handle canvas ready from CameraFeedViewer
   */
  const handleCanvasReady = useCallback((canvasElement: HTMLCanvasElement, canvasDimensions: CanvasDimensions) => {
    setCanvas(canvasElement);
    setDimensions(canvasDimensions);
  }, []);

  /**
   * Handle drawing start
   */
  const handleDrawingStart = useCallback((type: ZoneType, startPoint: any) => {
    startDrawing(type, startPoint);
  }, [startDrawing]);

  /**
   * Handle drawing update
   */
  const handleDrawingUpdate = useCallback((currentPoint: any) => {
    updateDrawing(currentPoint);
  }, [updateDrawing]);

  /**
   * Handle drawing end
   */
  const handleDrawingEnd = useCallback(() => {
    const newZone = finishDrawing();
    if (newZone) {
      console.log('Zone created:', newZone);
      setDrawingMode(null); // Exit drawing mode after creating zone
    }
  }, [finishDrawing]);

  /**
   * Handle zone click
   */
  const handleZoneClick = useCallback((zoneId: string, point: any) => {
    selectZone(zoneId);
    console.log('Zone clicked:', zoneId, 'at point:', point);
  }, [selectZone]);

  /**
   * Start drawing warning zone
   */
  const startWarningZone = useCallback(() => {
    setDrawingMode('warning');
  }, []);

  /**
   * Start drawing alarm zone
   */
  const startAlarmZone = useCallback(() => {
    setDrawingMode('alarm');
  }, []);

  /**
   * Cancel drawing
   */
  const cancelDrawing = useCallback(() => {
    setDrawingMode(null);
  }, []);

  return (
    <div className="space-y-4">
      {/* Zone Controls */}
      <div className="flex gap-2 p-4 bg-slate-800 rounded-lg">
        <button
          onClick={startWarningZone}
          disabled={!camera || drawingState.isDrawing}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            drawingMode === 'warning'
              ? 'bg-yellow-600 text-white'
              : 'bg-yellow-500 hover:bg-yellow-600 text-white disabled:bg-slate-600 disabled:text-slate-400'
          }`}
        >
          {drawingMode === 'warning' ? 'Drawing Warning Zone...' : 'Add Warning Zone'}
        </button>
        
        <button
          onClick={startAlarmZone}
          disabled={!camera || drawingState.isDrawing}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            drawingMode === 'alarm'
              ? 'bg-red-600 text-white'
              : 'bg-red-500 hover:bg-red-600 text-white disabled:bg-slate-600 disabled:text-slate-400'
          }`}
        >
          {drawingMode === 'alarm' ? 'Drawing Alarm Zone...' : 'Add Alarm Zone'}
        </button>

        {drawingMode && (
          <button
            onClick={cancelDrawing}
            className="px-4 py-2 rounded text-sm font-medium bg-slate-600 hover:bg-slate-700 text-white"
          >
            Cancel
          </button>
        )}

        <div className="flex-1" />

        <div className="text-sm text-slate-400">
          Zones: {zones.length} | Drawing: {drawingState.isDrawing ? 'Yes' : 'No'}
        </div>
      </div>

      {/* Camera Feed with Zone Drawing */}
      <div className="relative">
        <CameraFeedViewer
          camera={camera}
          onCanvasReady={handleCanvasReady}
          className="w-full h-96"
        />
        
        {canvas && (
          <ZoneDrawingCanvas
            canvas={canvas}
            dimensions={dimensions}
            zones={zones}
            drawingState={drawingState}
            drawingMode={drawingMode}
            onDrawingStart={handleDrawingStart}
            onDrawingUpdate={handleDrawingUpdate}
            onDrawingEnd={handleDrawingEnd}
            onZoneClick={handleZoneClick}
          />
        )}
      </div>

      {/* Zone List */}
      {zones.length > 0 && (
        <div className="p-4 bg-slate-800 rounded-lg">
          <h3 className="text-lg font-medium text-white mb-3">Zones</h3>
          <div className="space-y-2">
            {zones.map((zone) => (
              <div
                key={zone.id}
                className={`flex items-center justify-between p-3 rounded ${
                  zone.selected ? 'bg-slate-600' : 'bg-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-4 h-4 rounded ${
                      zone.type === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                  />
                  <span className="text-white font-medium">
                    {zone.type.charAt(0).toUpperCase() + zone.type.slice(1)} Zone
                  </span>
                  <span className="text-slate-400 text-sm">
                    {zone.id.slice(-8)}
                  </span>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleZoneVisibility(zone.id)}
                    className={`px-2 py-1 rounded text-xs ${
                      zone.visible
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-slate-600 hover:bg-slate-700 text-slate-300'
                    }`}
                  >
                    {zone.visible ? 'Visible' : 'Hidden'}
                  </button>
                  
                  <button
                    onClick={() => selectZone(zone.selected ? null : zone.id)}
                    className="px-2 py-1 rounded text-xs bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {zone.selected ? 'Deselect' : 'Select'}
                  </button>
                  
                  <button
                    onClick={() => deleteZone(zone.id)}
                    className="px-2 py-1 rounded text-xs bg-red-600 hover:bg-red-700 text-white"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="p-4 bg-slate-800 rounded-lg">
        <h3 className="text-lg font-medium text-white mb-2">Instructions</h3>
        <ul className="text-slate-300 text-sm space-y-1">
          <li>• Click "Add Warning Zone" or "Add Alarm Zone" to start drawing</li>
          <li>• Click and drag on the camera feed to draw a rectangle</li>
          <li>• Release the mouse to create the zone</li>
          <li>• Click on existing zones to select them</li>
          <li>• Use the zone list to manage visibility and delete zones</li>
        </ul>
      </div>
    </div>
  );
}