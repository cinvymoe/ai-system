/**
 * ZoneControls Component
 * Provides zone management controls including Add Warning/Alarm Zone buttons
 * Requirements: 1.2, 2.1, 3.1
 */

import { AlertTriangle, Shield, Square } from 'lucide-react';
import './ZoneDrawingCanvas.css';
import { Zone, ZoneType } from '../types/zone';
import { Button } from './ui/button';
import { ZoneList } from './ZoneList';

interface ZoneControlsProps {
  zones: Zone[];
  drawingMode: ZoneType | null;
  selectedZoneId: string | null;
  onDrawingModeChange: (mode: ZoneType | null) => void;
  onZoneSelect: (zoneId: string | null) => void;
  onZoneDelete: (zoneId: string) => void;
  onZoneVisibilityToggle: (zoneId: string) => void;
  className?: string;
}

export function ZoneControls({
  zones,
  drawingMode,
  selectedZoneId,
  onDrawingModeChange,
  onZoneSelect,
  onZoneDelete,
  onZoneVisibilityToggle,
  className = ''
}: ZoneControlsProps) {
  /**
   * Handle drawing mode activation
   * Requirements: 1.2, 2.1 - Zone drawing mode activation
   */
  const handleDrawingModeToggle = (type: ZoneType) => {
    if (drawingMode === type) {
      // If already in this drawing mode, turn it off
      onDrawingModeChange(null);
    } else {
      // Activate drawing mode for this zone type
      onDrawingModeChange(type);
      // Clear any selected zone when starting to draw
      onZoneSelect(null);
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Zone Creation Controls */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h3 className="text-slate-100 text-sm font-medium mb-3 flex items-center gap-2">
          <Square className="size-4 text-cyan-500" />
          区域管理
        </h3>
        
        <div className="flex gap-2">
          {/* Add Warning Zone Button with Enhanced Visual Feedback */}
          <Button
            onClick={() => handleDrawingModeToggle('warning')}
            variant={drawingMode === 'warning' ? 'default' : 'outline'}
            size="sm"
            className={`zone-button flex items-center gap-2 transition-all duration-200 ${
              drawingMode === 'warning'
                ? 'bg-yellow-600 hover:bg-yellow-700 text-white border-yellow-600 shadow-lg shadow-yellow-600/25'
                : 'border-yellow-600 text-yellow-600 hover:bg-yellow-600 hover:text-white hover:shadow-lg hover:shadow-yellow-600/25 hover:scale-105'
            }`}
          >
            <AlertTriangle className={`size-4 transition-transform duration-200 ${
              drawingMode === 'warning' ? 'animate-pulse' : ''
            }`} />
            {drawingMode === 'warning' ? '取消绘制' : '添加警告区域'}
          </Button>

          {/* Add Alarm Zone Button with Enhanced Visual Feedback */}
          <Button
            onClick={() => handleDrawingModeToggle('alarm')}
            variant={drawingMode === 'alarm' ? 'default' : 'outline'}
            size="sm"
            className={`zone-button flex items-center gap-2 transition-all duration-200 ${
              drawingMode === 'alarm'
                ? 'bg-red-600 hover:bg-red-700 text-white border-red-600 shadow-lg shadow-red-600/25'
                : 'border-red-600 text-red-600 hover:bg-red-600 hover:text-white hover:shadow-lg hover:shadow-red-600/25 hover:scale-105'
            }`}
          >
            <Shield className={`size-4 transition-transform duration-200 ${
              drawingMode === 'alarm' ? 'animate-pulse' : ''
            }`} />
            {drawingMode === 'alarm' ? '取消绘制' : '添加报警区域'}
          </Button>
        </div>

        {/* Enhanced Drawing Mode Indicator */}
        {drawingMode && (
          <div className={`drawing-mode-indicator mt-3 p-3 rounded-lg text-sm transition-all duration-300 ${
            drawingMode === 'warning'
              ? 'bg-yellow-600/20 text-yellow-300 border border-yellow-600/30 shadow-lg shadow-yellow-600/10'
              : 'bg-red-600/20 text-red-300 border border-red-600/30 shadow-lg shadow-red-600/10'
          }`}>
            <div className="flex items-center gap-3">
              <div className="relative">
                {drawingMode === 'warning' ? (
                  <AlertTriangle className="size-4 animate-pulse" />
                ) : (
                  <Shield className="size-4 animate-pulse" />
                )}
                {/* Pulsing dot indicator */}
                <div className={`absolute -top-1 -right-1 size-2 rounded-full animate-ping ${
                  drawingMode === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                }`}></div>
              </div>
              <div className="flex-1">
                <div className="font-medium">
                  正在绘制{drawingMode === 'warning' ? '警告' : '报警'}区域
                </div>
                <div className="text-xs opacity-80 mt-1">
                  在摄像头画面上拖拽鼠标创建区域
                </div>
              </div>
              {/* Visual cursor indicator */}
              <div className={`size-6 border-2 border-dashed rounded ${
                drawingMode === 'warning' ? 'border-yellow-400' : 'border-red-400'
              } flex items-center justify-center`}>
                <div className={`size-1 rounded-full ${
                  drawingMode === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                } animate-pulse`}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Zone List Component */}
      <ZoneList
        zones={zones}
        selectedZoneId={selectedZoneId}
        onZoneSelect={onZoneSelect}
        onZoneDelete={onZoneDelete}
        onZoneVisibilityToggle={onZoneVisibilityToggle}
      />

      {/* Selected Zone Quick Info */}
      {selectedZoneId && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="text-xs text-slate-400 mb-2">当前选择</div>
          {(() => {
            const selectedZone = zones.find(z => z.id === selectedZoneId);
            if (!selectedZone) return null;
            
            return (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {selectedZone.type === 'warning' ? (
                    <AlertTriangle className="size-4 text-yellow-500" />
                  ) : (
                    <Shield className="size-4 text-red-500" />
                  )}
                  <span className="text-slate-200 text-sm">
                    {selectedZone.type === 'warning' ? '警告区域' : '报警区域'}
                  </span>
                </div>
                <Button
                  onClick={() => onZoneSelect(null)}
                  variant="ghost"
                  size="sm"
                  className="text-slate-400 hover:text-slate-200 p-1 h-auto"
                >
                  取消选择
                </Button>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}