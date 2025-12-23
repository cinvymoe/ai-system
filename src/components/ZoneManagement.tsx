/**
 * ZoneManagement Component
 * Integrates camera feed viewing, zone drawing, and zone controls
 * Requirements: 1.1, 1.2, 2.1, 3.1
 */

import { useState, useRef, useEffect } from 'react';
import { Camera } from 'lucide-react';
import { CameraFeedViewer } from './CameraFeedViewer';
import { ZoneDrawingCanvas } from './ZoneDrawingCanvas';
import { ZoneControls } from './ZoneControls';
import { ZoneInfoPanel } from './ZoneInfoPanel';
import { ZoneErrorBoundary, CanvasErrorBoundary } from './ErrorBoundary';
import { useZoneManagement } from '../hooks/useZoneManagement';
import { useZonePersistence } from '../hooks/useZonePersistence';
import { ZoneType, Zone } from '../types/zone';
import './ZoneDrawingCanvas.css';
import { Point, aiSettingsService } from '../services/aiSettingsService';
import { CanvasDimensions } from '../utils/coordinateTransform';
import { cameraService, Camera as CameraType } from '../services/cameraService';

interface ZoneManagementProps {
  cameraId: string;
  className?: string;
}

export function ZoneManagement({ cameraId, className = '' }: ZoneManagementProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dimensions, setDimensions] = useState<CanvasDimensions>({ width: 0, height: 0 });
  const [drawingMode, setDrawingMode] = useState<ZoneType | null>(null);
  const [camera, setCamera] = useState<CameraType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [lastFailedOperation, setLastFailedOperation] = useState<(() => Promise<void>) | null>(null);
  const [componentError, setComponentError] = useState<string | null>(null);

  // Zone management hook
  const {
    zones,
    drawingState,
    selectedZoneId,
    selectZone,
    deleteZone,
    toggleZoneVisibility,
    setZones,
    startDrawing,
    updateDrawing,
    finishDrawing,
    cancelDrawing,
    resizeZone,
    moveZone
  } = useZoneManagement();

  // Zone persistence hook
  const { loadZones, saveZones } = useZonePersistence();

  /**
   * Save zones for the current camera
   * Requirements: 4.1, 4.4 - Zone data persistence with camera binding
   */
  const saveZonesForCamera = async (zonesToSave: Zone[]) => {
    if (!cameraId) {
      const errorMsg = 'No camera selected for zone configuration';
      setError(errorMsg);
      throw new Error(errorMsg);
    }

    // Enhanced input validation
    try {
      const { validateZones, validateZoneInput } = await import('../utils/zoneValidation');
      
      // Validate each zone input
      for (let i = 0; i < zonesToSave.length; i++) {
        const inputValidation = validateZoneInput(zonesToSave[i]);
        if (!inputValidation.isValid) {
          const errorMsg = `Zone ${i + 1} input validation failed: ${inputValidation.errors.join(', ')}`;
          setError(errorMsg);
          throw new Error(errorMsg);
        }
      }

      // Validate zones collection
      const validation = validateZones(zonesToSave);
      if (!validation.isValid) {
        const errorMsg = `Invalid zone configuration: ${validation.errors.join(', ')}`;
        setError(errorMsg);
        throw new Error(errorMsg);
      }
    } catch (validationError) {
      const errorMsg = validationError instanceof Error 
        ? `Validation error: ${validationError.message}`
        : 'Unknown validation error occurred';
      setError(errorMsg);
      throw new Error(errorMsg);
    }

    setIsSaving(true);
    setError(null);
    setNetworkError(null);

    try {
      const settings = await aiSettingsService.getSettings();
      
      // Check if AI settings are bound to the current camera
      if (settings.camera_id !== cameraId) {
        // Bind the camera to AI settings first
        await aiSettingsService.bindCamera(settings.id, cameraId);
      }
      
      // Save the zones
      await saveZones(zonesToSave, settings.id);
      
      // Show success message
      // Requirements: 4.5 - Save operation success confirmation
      setSuccessMessage('Zone configuration saved successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Failed to save zones for camera:', cameraId, err);
      
      // Handle different types of errors
      let errorMessage = 'Failed to save zone configuration';
      
      if (err instanceof Error) {
        if (err.message.includes('network') || err.message.includes('fetch')) {
          errorMessage = 'Network error: Unable to connect to server. Please check your connection and try again.';
          setNetworkError(errorMessage);
          // Store the failed operation for retry
          setLastFailedOperation(() => () => saveZonesForCamera(zonesToSave));
        } else if (err.message.includes('timeout')) {
          errorMessage = 'Request timeout: Server is taking too long to respond. Please try again.';
          setNetworkError(errorMessage);
          setLastFailedOperation(() => () => saveZonesForCamera(zonesToSave));
        } else if (err.message.includes('unauthorized') || err.message.includes('403')) {
          errorMessage = 'Authorization error: You do not have permission to save zone configurations.';
        } else if (err.message.includes('validation')) {
          errorMessage = `Validation error: ${err.message}`;
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Load camera and zones when camera ID changes
   * Requirements: 4.2 - Camera-specific zone loading
   */
  useEffect(() => {
    const loadCameraAndZones = async () => {
      if (!cameraId) {
        setCamera(null);
        setZones([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Load camera details
        const cameras = await cameraService.getAllCameras();
        const selectedCamera = cameras.find(c => c.id === cameraId);
        setCamera(selectedCamera || null);

        if (!selectedCamera) {
          setError(`Camera ${cameraId} not found`);
          setZones([]);
          return;
        }

        // Load AI settings to get zones
        const settings = await aiSettingsService.getSettings();
        if (settings.camera_id === cameraId) {
          // Camera matches current AI settings - load zones
          const loadedZones = loadZones(settings);
          setZones(loadedZones);
        } else {
          // Camera doesn't match current AI settings - clear zones
          // In the current design, only one camera can have AI settings at a time
          setZones([]);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load camera data';
        setError(errorMessage);
        setZones([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadCameraAndZones();
  }, [cameraId, loadZones, setZones]);

  /**
   * Handle drawing mode changes
   * Requirements: 1.2, 2.1 - Zone drawing mode activation
   */
  const handleDrawingModeChange = (mode: ZoneType | null) => {
    setDrawingMode(mode);
    if (!mode) {
      // Cancel any active drawing
      cancelDrawing();
    }
  };

  /**
   * Handle drawing start
   * Requirements: 1.3, 2.2 - Real-time drawing feedback
   */
  const handleDrawingStart = (type: ZoneType, startPoint: Point) => {
    startDrawing(type, startPoint);
  };

  /**
   * Handle drawing update
   * Requirements: 1.3, 2.2 - Real-time drawing feedback
   */
  const handleDrawingUpdate = (currentPoint: Point) => {
    updateDrawing(currentPoint);
  };

  /**
   * Handle drawing end with enhanced validation
   * Requirements: 1.4, 2.3 - Zone creation from coordinates
   */
  const handleDrawingEnd = async () => {
    try {
      const newZone = finishDrawing();
      if (!newZone) {
        setError('Failed to create zone: Invalid coordinates or zone too small');
        return;
      }

      // Enhanced validation for the new zone
      const { 
        validateZone, 
        validateZoneInput, 
        validateZoneDimensions,
        MAX_ZONES_PER_TYPE 
      } = await import('../utils/zoneValidation');
      
      // Validate zone input structure
      const inputValidation = validateZoneInput(newZone);
      if (!inputValidation.isValid) {
        setError(`Invalid zone data: ${inputValidation.errors.join(', ')}`);
        return;
      }

      // Validate zone dimensions
      const dimensionValidation = validateZoneDimensions(newZone.points);
      if (!dimensionValidation.isValid) {
        setError(`Invalid zone dimensions: ${dimensionValidation.errors.join(', ')}`);
        return;
      }

      // Validate the complete zone
      const validation = validateZone(newZone);
      if (!validation.isValid) {
        setError(`Cannot create zone: ${validation.errors.join(', ')}`);
        return;
      }

      // Check for zone limits
      const existingZonesOfType = zones.filter(z => z.type === newZone.type);
      if (existingZonesOfType.length >= MAX_ZONES_PER_TYPE) {
        setError(`Cannot create zone: Maximum ${MAX_ZONES_PER_TYPE} ${newZone.type} zone(s) allowed`);
        return;
      }

      // Check for overlapping zones of the same type
      const { doZonesOverlap } = await import('../utils/zoneValidation');
      const overlappingZone = existingZonesOfType.find(existingZone => 
        doZonesOverlap(newZone, existingZone, 0.5) // 50% overlap threshold
      );
      
      if (overlappingZone) {
        setError(`Cannot create zone: Overlaps significantly with existing ${newZone.type} zone`);
        return;
      }

      // Save zones after creating a new one
      const updatedZones = [...zones, newZone];
      await saveZonesForCamera(updatedZones);
      setDrawingMode(null);
    } catch (err) {
      console.error('Failed to save zone:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to save zone';
      setError(errorMsg);
    }
  };

  /**
   * Handle zone click
   * Requirements: 3.1 - Zone selection and highlighting functionality
   */
  const handleZoneClick = (zoneId: string, _point: Point) => {
    selectZone(zoneId);
    setDrawingMode(null); // Exit drawing mode when selecting a zone
  };

  /**
   * Handle zone deletion
   * Requirements: 3.2 - Zone deletion
   */
  const handleZoneDelete = async (zoneId: string) => {
    try {
      const zoneToDelete = zones.find(z => z.id === zoneId);
      if (!zoneToDelete) {
        setError('Zone not found');
        return;
      }

      deleteZone(zoneId);
      const updatedZones = zones.filter(z => z.id !== zoneId);
      await saveZonesForCamera(updatedZones);
      
      setSuccessMessage(`${zoneToDelete.type === 'warning' ? 'Warning' : 'Alarm'} zone deleted successfully`);
      setTimeout(() => setSuccessMessage(null), 2000);
    } catch (err) {
      console.error('Failed to save zones after deletion:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete zone';
      setError(errorMsg);
      
      // Reload zones to restore state if save failed
      if (cameraId) {
        try {
          const settings = await aiSettingsService.getSettings();
          if (settings.camera_id === cameraId) {
            const loadedZones = loadZones(settings);
            setZones(loadedZones);
          }
        } catch (reloadErr) {
          console.error('Failed to reload zones after delete error:', reloadErr);
        }
      }
    }
  };

  /**
   * Handle zone resize
   * Requirements: 3.3, 3.5 - Zone resizing with corner handles and immediate state updates
   */
  const handleZoneResize = (zoneId: string, newPoints: Point[]) => {
    // Immediate state update for real-time feedback
    resizeZone(zoneId, newPoints);
  };

  /**
   * Handle zone move
   * Requirements: 3.4, 3.5 - Zone movement by dragging center and immediate state updates
   */
  const handleZoneMove = (zoneId: string, newPoints: Point[]) => {
    // Immediate state update for real-time feedback
    moveZone(zoneId, newPoints);
  };

  /**
   * Handle zone manipulation end (save to backend)
   * Requirements: 4.1 - Zone data persistence
   */
  const handleZoneManipulationEnd = async () => {
    try {
      await saveZonesForCamera(zones);
      setSuccessMessage('Zone changes saved');
      setTimeout(() => setSuccessMessage(null), 2000);
    } catch (err) {
      console.error('Failed to save zone changes:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to save changes';
      setError(errorMsg);
      
      // Reload zones to restore previous state if save failed
      if (cameraId) {
        try {
          const settings = await aiSettingsService.getSettings();
          if (settings.camera_id === cameraId) {
            const loadedZones = loadZones(settings);
            setZones(loadedZones);
            setSuccessMessage('Zone state restored from server');
            setTimeout(() => setSuccessMessage(null), 2000);
          }
        } catch (reloadErr) {
          console.error('Failed to reload zones after manipulation error:', reloadErr);
          setError('Failed to restore zone state. Please refresh the page.');
        }
      }
    }
  };

  /**
   * Handle zone visibility toggle
   */
  const handleZoneVisibilityToggle = async (zoneId: string) => {
    toggleZoneVisibility(zoneId);
    // Note: Visibility is UI-only state, we don't need to save it to backend
    // The backend only stores zone coordinates and type
  };

  /**
   * Retry the last failed operation
   */
  const handleRetryOperation = async () => {
    if (!lastFailedOperation) return;
    
    try {
      setNetworkError(null);
      setError(null);
      await lastFailedOperation();
      setLastFailedOperation(null);
    } catch (err) {
      console.error('Retry operation failed:', err);
      const errorMsg = err instanceof Error ? err.message : 'Retry failed';
      setError(errorMsg);
    }
  };

  /**
   * Handle canvas ready
   */
  const handleCanvasReady = (canvas: HTMLCanvasElement, newDimensions: CanvasDimensions) => {
    canvasRef.current = canvas;
    setDimensions(newDimensions);
  };

  /**
   * Handle zone-related errors from error boundaries
   */
  const handleZoneError = (error: Error) => {
    console.error('Zone component error:', error);
    setComponentError(`Zone management error: ${error.message}`);
    
    // Reset drawing state on error
    setDrawingMode(null);
    cancelDrawing();
  };

  /**
   * Handle canvas-related errors from error boundaries
   */
  const handleCanvasError = (error: Error) => {
    console.error('Canvas component error:', error);
    setComponentError(`Drawing canvas error: ${error.message}`);
    
    // Reset canvas-related state
    setDrawingMode(null);
    cancelDrawing();
  };

  if (isLoading) {
    return (
      <div className={`bg-slate-900 border border-slate-600 rounded-lg p-8 text-center ${className}`}>
        <div className="animate-spin size-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-400">加载区域数据中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-slate-900 border border-slate-600 rounded-lg p-8 text-center ${className}`}>
        <Camera className="size-8 mx-auto mb-4 text-red-500 opacity-50" />
        <p className="text-red-400 mb-2">加载失败</p>
        <p className="text-slate-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <ZoneErrorBoundary onZoneError={handleZoneError} cameraId={cameraId}>
      <div className={`space-y-4 ${className}`}>
        {/* Component Error Message */}
        {componentError && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 flex items-center gap-3">
            <div className="size-5 rounded-full bg-red-500 flex items-center justify-center">
              <svg className="size-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-red-400 text-sm font-medium">{componentError}</p>
              <button 
                onClick={() => setComponentError(null)}
                className="text-red-400 text-xs underline hover:text-red-300 mt-2 transition-colors duration-200"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Enhanced Success Message */}
        {successMessage && (
        <div className="feedback-message zone-operation-success bg-green-900/20 border border-green-500/30 rounded-lg p-3 flex items-center gap-3 shadow-lg shadow-green-500/10">
          <div className="size-5 rounded-full bg-green-500 flex items-center justify-center animate-pulse">
            <svg className="size-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-green-400 text-sm font-medium">{successMessage}</p>
            <div className="w-full bg-green-900/30 rounded-full h-1 mt-2">
              <div className="bg-green-500 h-1 rounded-full animate-pulse" style={{ width: '100%' }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Network Error Message */}
      {networkError && (
        <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <div className="size-4 rounded-full bg-orange-500 flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="size-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-orange-400 text-sm font-medium">Network Connection Issue</p>
              <p className="text-orange-300 text-xs mt-1">{networkError}</p>
              <div className="flex gap-2 mt-2">
                {lastFailedOperation && (
                  <button 
                    onClick={handleRetryOperation}
                    disabled={isSaving}
                    className="text-orange-400 text-xs px-2 py-1 bg-orange-500/10 rounded hover:bg-orange-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSaving ? 'Retrying...' : 'Retry'}
                  </button>
                )}
                <button 
                  onClick={() => {
                    setNetworkError(null);
                    setLastFailedOperation(null);
                  }}
                  className="text-orange-400 text-xs px-2 py-1 hover:underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Error Message */}
      {error && !networkError && (
        <div className="feedback-message bg-red-900/20 border border-red-500/30 rounded-lg p-3 flex items-center gap-3 shadow-lg shadow-red-500/10">
          <div className="size-5 rounded-full bg-red-500 flex items-center justify-center">
            <svg className="size-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-red-400 text-sm font-medium">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="zone-button text-red-400 text-xs underline hover:text-red-300 mt-2 transition-colors duration-200"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Enhanced Saving Indicator */}
      {isSaving && (
        <div className="feedback-message bg-blue-900/20 border border-blue-500/30 rounded-lg p-3 flex items-center gap-3 shadow-lg shadow-blue-500/10">
          <div className="loading-spinner size-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <div className="flex-1">
            <p className="text-blue-400 text-sm font-medium">Saving zone configuration...</p>
            <div className="w-full bg-blue-900/30 rounded-full h-1 mt-2">
              <div className="bg-blue-500 h-1 rounded-full animate-pulse" style={{ width: '70%' }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Camera Feed with Zone Drawing - Takes 2/3 width on large screens */}
        <div className="lg:col-span-2">
          <div className="bg-slate-900 border border-slate-600 rounded-lg overflow-hidden">
            <div className="relative">
              <CameraFeedViewer
                camera={camera}
                onCanvasReady={handleCanvasReady}
                className="w-full"
              />
              
              {/* Zone Drawing Canvas Overlay with Error Boundary */}
              <CanvasErrorBoundary onCanvasError={handleCanvasError}>
                <ZoneDrawingCanvas
                  canvas={canvasRef.current}
                  dimensions={dimensions}
                  zones={zones}
                  drawingState={drawingState}
                  drawingMode={drawingMode}
                  onDrawingStart={handleDrawingStart}
                  onDrawingUpdate={handleDrawingUpdate}
                  onDrawingEnd={handleDrawingEnd}
                  onZoneClick={handleZoneClick}
                  onZoneResize={handleZoneResize}
                  onZoneMove={handleZoneMove}
                  onZoneDelete={handleZoneDelete}
                  onManipulationEnd={handleZoneManipulationEnd}
                />
              </CanvasErrorBoundary>
            </div>

            {/* Camera Info */}
            <div className="p-3 bg-slate-800 border-t border-slate-600">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-slate-400">
                  <Camera className="size-4" />
                  <span>摄像头 ID: {cameraId}</span>
                </div>
                <div className="text-slate-400">
                  {zones.length > 0 ? `${zones.length} 个区域` : '无区域'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Zone Info and Controls */}
        <div className="space-y-4">
          {/* Real-time Zone Information Panel */}
          <ZoneInfoPanel
            selectedZone={zones.find(z => z.id === selectedZoneId)}
            drawingState={drawingState}
          />

          {/* Zone Controls and List */}
          <ZoneControls
            zones={zones}
            drawingMode={drawingMode}
            selectedZoneId={selectedZoneId}
            onDrawingModeChange={handleDrawingModeChange}
            onZoneSelect={selectZone}
            onZoneDelete={handleZoneDelete}
            onZoneVisibilityToggle={handleZoneVisibilityToggle}
          />
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-slate-900 border border-slate-600 rounded-lg p-4">
        <h4 className="text-slate-200 text-sm font-medium mb-2">使用说明</h4>
        <ul className="text-slate-400 text-sm space-y-1">
          <li>• 点击"添加警告区域"或"添加报警区域"按钮进入绘制模式</li>
          <li>• 在摄像头画面上拖拽鼠标绘制矩形区域</li>
          <li>• 右侧面板实时显示区域坐标、尺寸和面积信息</li>
          <li>• 点击已创建的区域可以选中并查看详情</li>
          <li>• 选中区域后，拖拽角落手柄可以调整大小</li>
          <li>• 选中区域后，拖拽区域中心可以移动位置</li>
          <li>• 点击选中区域右上角的 X 按钮可以删除区域</li>
          <li>• 使用区域列表中的按钮可以隐藏/显示区域</li>
          <li>• 警告区域（黄色）用于一般监控，报警区域（红色）用于重要区域监控</li>
        </ul>
      </div>
      </div>
    </ZoneErrorBoundary>
  );
}