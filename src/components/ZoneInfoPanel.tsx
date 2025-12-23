/**
 * ZoneInfoPanel Component
 * Displays real-time zone information including coordinates, dimensions, and area
 * Requirements: 5.2, 5.3, 5.4
 */

import { Zone, DrawingState } from '../types/zone';
import { calculateZoneBounds, calculateZoneArea, formatCoordinate } from '../utils/coordinateTransform';
import { Ruler, Move, Square } from 'lucide-react';

interface ZoneInfoPanelProps {
  selectedZone?: Zone;
  drawingState?: DrawingState;
  className?: string;
}

export function ZoneInfoPanel({ 
  selectedZone, 
  drawingState, 
  className = '' 
}: ZoneInfoPanelProps) {
  
  /**
   * Calculate real-time drawing dimensions
   * Requirements: 5.2, 5.3 - Coordinate and dimension display during drawing
   */
  const getDrawingInfo = () => {
    if (!drawingState?.isDrawing || !drawingState.startPoint || !drawingState.currentPoint) {
      return null;
    }

    const { startPoint, currentPoint, drawingType } = drawingState;
    
    // Calculate rectangle bounds
    const minX = Math.min(startPoint.x, currentPoint.x);
    const minY = Math.min(startPoint.y, currentPoint.y);
    const maxX = Math.max(startPoint.x, currentPoint.x);
    const maxY = Math.max(startPoint.y, currentPoint.y);
    
    const width = maxX - minX;
    const height = maxY - minY;
    const area = width * height;

    return {
      type: drawingType,
      startPoint,
      currentPoint,
      bounds: { minX, minY, maxX, maxY, width, height },
      area,
      isDrawing: true
    };
  };

  /**
   * Get zone information for selected zone
   * Requirements: 5.4 - Zone information display including area size and position
   */
  const getZoneInfo = () => {
    if (!selectedZone) return null;

    const bounds = calculateZoneBounds(selectedZone.points);
    const area = calculateZoneArea(selectedZone.points);

    return {
      type: selectedZone.type,
      id: selectedZone.id,
      bounds,
      area,
      points: selectedZone.points,
      visible: selectedZone.visible,
      isDrawing: false
    };
  };

  const drawingInfo = getDrawingInfo();
  const zoneInfo = getZoneInfo();
  const displayInfo = drawingInfo || zoneInfo;

  if (!displayInfo) {
    return (
      <div className={`bg-slate-900 border border-slate-600 rounded-lg p-4 ${className}`}>
        <div className="text-center text-slate-400">
          <Square className="size-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">选择区域或开始绘制以查看详细信息</p>
        </div>
      </div>
    );
  }

  const { type, bounds, area, isDrawing } = displayInfo;
  const typeLabel = type === 'warning' ? '警告区域' : '报警区域';
  const typeColor = type === 'warning' ? 'text-yellow-400' : 'text-red-400';
  const typeBorderColor = type === 'warning' ? 'border-yellow-600/30' : 'border-red-600/30';

  return (
    <div className={`bg-slate-900 border border-slate-600 rounded-lg p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Square className={`size-4 ${typeColor}`} />
        <h3 className="text-slate-100 text-sm font-medium">
          {isDrawing ? `正在绘制${typeLabel}` : `${typeLabel}信息`}
        </h3>
        {isDrawing && (
          <span className="text-xs bg-cyan-600/20 text-cyan-300 px-2 py-1 rounded border border-cyan-600/30">
            实时
          </span>
        )}
      </div>

      {/* Zone Type Indicator */}
      <div className={`mb-4 p-3 rounded border ${typeBorderColor} ${
        type === 'warning' ? 'bg-yellow-600/10' : 'bg-red-600/10'
      }`}>
        <div className="flex items-center justify-between">
          <span className={`text-sm font-medium ${typeColor}`}>
            {typeLabel}
          </span>
          {!isDrawing && zoneInfo && (
            <span className="text-xs text-slate-400">
              ID: {zoneInfo.id.split('-').pop()}
            </span>
          )}
        </div>
      </div>

      {/* Coordinates Section */}
      <div className="space-y-3">
        {/* Position Information */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Move className="size-3 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">位置坐标</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-800 p-2 rounded">
              <div className="text-slate-500 mb-1">左上角</div>
              <div className="text-slate-200">
                ({formatCoordinate(bounds.minX)}, {formatCoordinate(bounds.minY)})
              </div>
            </div>
            <div className="bg-slate-800 p-2 rounded">
              <div className="text-slate-500 mb-1">右下角</div>
              <div className="text-slate-200">
                ({formatCoordinate(bounds.maxX)}, {formatCoordinate(bounds.maxY)})
              </div>
            </div>
          </div>
        </div>

        {/* Dimensions Section */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Ruler className="size-3 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">尺寸信息</span>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="bg-slate-800 p-2 rounded">
              <div className="text-slate-500 mb-1">宽度</div>
              <div className="text-slate-200">
                {formatCoordinate(bounds.width)}
              </div>
            </div>
            <div className="bg-slate-800 p-2 rounded">
              <div className="text-slate-500 mb-1">高度</div>
              <div className="text-slate-200">
                {formatCoordinate(bounds.height)}
              </div>
            </div>
            <div className="bg-slate-800 p-2 rounded">
              <div className="text-slate-500 mb-1">面积</div>
              <div className="text-slate-200">
                {(area * 100).toFixed(2)}%
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Drawing Coordinates */}
        {isDrawing && drawingInfo && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="size-2 bg-cyan-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-cyan-400 font-medium">实时坐标</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-800 p-2 rounded border border-cyan-600/30">
                <div className="text-slate-500 mb-1">起始点</div>
                <div className="text-cyan-300">
                  ({formatCoordinate(drawingInfo.startPoint.x)}, {formatCoordinate(drawingInfo.startPoint.y)})
                </div>
              </div>
              <div className="bg-slate-800 p-2 rounded border border-cyan-600/30">
                <div className="text-slate-500 mb-1">当前点</div>
                <div className="text-cyan-300">
                  ({formatCoordinate(drawingInfo.currentPoint.x)}, {formatCoordinate(drawingInfo.currentPoint.y)})
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Zone Status */}
        {!isDrawing && zoneInfo && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className={`size-2 rounded-full ${zoneInfo.visible ? 'bg-green-400' : 'bg-slate-500'}`}></div>
              <span className="text-xs text-slate-400 font-medium">状态</span>
            </div>
            <div className="bg-slate-800 p-2 rounded text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-500">可见性</span>
                <span className={zoneInfo.visible ? 'text-green-400' : 'text-slate-400'}>
                  {zoneInfo.visible ? '显示' : '隐藏'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      {isDrawing && (
        <div className="mt-4 p-3 bg-cyan-600/10 border border-cyan-600/30 rounded text-xs">
          <div className="text-cyan-300 mb-1">绘制提示</div>
          <div className="text-slate-400">
            拖拽鼠标创建矩形区域，松开鼠标完成绘制
          </div>
        </div>
      )}
    </div>
  );
}