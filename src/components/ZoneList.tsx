/**
 * ZoneList Component
 * Dedicated component for zone list management with visibility toggles
 * Requirements: 5.5, 5.4
 */

import React, { useState } from 'react';
import { AlertTriangle, Shield, Trash2, Eye, EyeOff, Square, MapPin, Ruler } from 'lucide-react';
import { Zone } from '../types/zone';
import { Button } from './ui/button';
import { calculateZoneBounds, calculateZoneArea, formatCoordinate } from '../utils/coordinateTransform';
import './ZoneDrawingCanvas.css';

interface ZoneListProps {
  zones: Zone[];
  selectedZoneId: string | null;
  onZoneSelect: (zoneId: string | null) => void;
  onZoneDelete: (zoneId: string) => void;
  onZoneVisibilityToggle: (zoneId: string) => void;
  className?: string;
}

export function ZoneList({
  zones,
  selectedZoneId,
  onZoneSelect,
  onZoneDelete,
  onZoneVisibilityToggle,
  className = ''
}: ZoneListProps) {
  const [showZoneList, setShowZoneList] = useState(true);
  const [expandedZones, setExpandedZones] = useState<Set<string>>(new Set());

  /**
   * Handle zone selection
   * Requirements: 5.5 - Zone list with toggle visibility controls
   */
  const handleZoneSelect = (zoneId: string) => {
    if (selectedZoneId === zoneId) {
      // Deselect if already selected
      onZoneSelect(null);
    } else {
      // Select the zone
      onZoneSelect(zoneId);
    }
  };

  /**
   * Handle zone deletion with confirmation
   * Requirements: 5.5 - Zone list management
   */
  const handleZoneDelete = (zoneId: string) => {
    const zone = zones.find(z => z.id === zoneId);
    if (zone && window.confirm(`确定要删除这个${zone.type === 'warning' ? '警告' : '报警'}区域吗？`)) {
      onZoneDelete(zoneId);
    }
  };

  /**
   * Toggle zone details expansion
   */
  const toggleZoneExpansion = (zoneId: string) => {
    const newExpanded = new Set(expandedZones);
    if (newExpanded.has(zoneId)) {
      newExpanded.delete(zoneId);
    } else {
      newExpanded.add(zoneId);
    }
    setExpandedZones(newExpanded);
  };

  /**
   * Get zone information for display
   * Requirements: 5.4 - Zone information display including area size and position
   */
  const getZoneDisplayInfo = (zone: Zone) => {
    const bounds = calculateZoneBounds(zone.points);
    const area = calculateZoneArea(zone.points);
    
    return {
      bounds,
      area,
      position: {
        x: bounds.minX + bounds.width / 2,
        y: bounds.minY + bounds.height / 2
      }
    };
  };

  const warningZones = zones.filter(zone => zone.type === 'warning');
  const alarmZones = zones.filter(zone => zone.type === 'alarm');

  if (zones.length === 0) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-lg p-4 ${className}`}>
        <div className="text-center py-4 text-slate-400 text-sm">
          <Square className="size-8 mx-auto mb-2 opacity-50" />
          <p>暂无区域</p>
          <p className="text-xs">创建区域后将在此显示</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-lg p-4 ${className}`}>
      {/* Zone List Header */}
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-slate-200 text-sm font-medium flex items-center gap-2">
          <Square className="size-4 text-cyan-500" />
          区域列表 ({zones.length})
        </h4>
        <Button
          onClick={() => setShowZoneList(!showZoneList)}
          variant="ghost"
          size="sm"
          className="text-slate-400 hover:text-slate-200"
          title={showZoneList ? '隐藏列表' : '显示列表'}
        >
          {showZoneList ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
        </Button>
      </div>

      {showZoneList && (
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {/* Warning Zones Section */}
          {warningZones.length > 0 && (
            <div>
              <div className="text-xs text-yellow-400 font-medium mb-2 flex items-center gap-1">
                <AlertTriangle className="size-3" />
                警告区域 ({warningZones.length})
              </div>
              <div className="space-y-2">
                {warningZones.map((zone, index) => {
                  const zoneInfo = getZoneDisplayInfo(zone);
                  const isExpanded = expandedZones.has(zone.id);
                  
                  return (
                    <div
                      key={zone.id}
                      className={`zone-list-item rounded-lg border transition-all duration-200 ${
                        selectedZoneId === zone.id
                          ? 'selected bg-yellow-600/20 border-yellow-600/50 shadow-lg shadow-yellow-600/10'
                          : 'bg-slate-900 border-slate-600 hover:border-yellow-600/30 hover:bg-slate-800/50 hover:shadow-md'
                      }`}
                    >
                      {/* Zone Header */}
                      <div
                        className="p-3 cursor-pointer"
                        onClick={() => handleZoneSelect(zone.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="size-4 text-yellow-500" />
                            <div>
                              <div className="text-sm text-slate-200 font-medium">
                                警告区域 {index + 1}
                              </div>
                              <div className="text-xs text-slate-400">
                                面积: {(zoneInfo.area * 100).toFixed(1)}%
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <Button
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                toggleZoneExpansion(zone.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="p-1 h-auto text-slate-400 hover:text-slate-200"
                              title="查看详情"
                            >
                              <MapPin className="size-3" />
                            </Button>
                            <Button
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                onZoneVisibilityToggle(zone.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="p-1 h-auto text-slate-400 hover:text-slate-200"
                              title={zone.visible ? '隐藏区域' : '显示区域'}
                            >
                              {zone.visible ? (
                                <Eye className="size-3" />
                              ) : (
                                <EyeOff className="size-3" />
                              )}
                            </Button>
                            <Button
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                handleZoneDelete(zone.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="p-1 h-auto text-slate-400 hover:text-red-400"
                              title="删除区域"
                            >
                              <Trash2 className="size-3" />
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Zone Details - Expanded */}
                      {isExpanded && (
                        <div className="px-3 pb-3 border-t border-yellow-600/20">
                          <div className="mt-2 space-y-2 text-xs">
                            {/* Position Information */}
                            <div className="flex items-center gap-2">
                              <MapPin className="size-3 text-slate-400" />
                              <span className="text-slate-400">位置:</span>
                              <span className="text-slate-200">
                                ({formatCoordinate(zoneInfo.bounds.minX)}, {formatCoordinate(zoneInfo.bounds.minY)}) 
                                → ({formatCoordinate(zoneInfo.bounds.maxX)}, {formatCoordinate(zoneInfo.bounds.maxY)})
                              </span>
                            </div>
                            
                            {/* Dimensions */}
                            <div className="flex items-center gap-2">
                              <Ruler className="size-3 text-slate-400" />
                              <span className="text-slate-400">尺寸:</span>
                              <span className="text-slate-200">
                                {formatCoordinate(zoneInfo.bounds.width)} × {formatCoordinate(zoneInfo.bounds.height)}
                              </span>
                            </div>

                            {/* Status */}
                            <div className="flex items-center gap-2">
                              <div className={`size-2 rounded-full ${zone.visible ? 'bg-green-400' : 'bg-slate-500'}`}></div>
                              <span className="text-slate-400">状态:</span>
                              <span className={zone.visible ? 'text-green-400' : 'text-slate-400'}>
                                {zone.visible ? '显示' : '隐藏'}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Alarm Zones Section */}
          {alarmZones.length > 0 && (
            <div>
              <div className="text-xs text-red-400 font-medium mb-2 flex items-center gap-1">
                <Shield className="size-3" />
                报警区域 ({alarmZones.length})
              </div>
              <div className="space-y-2">
                {alarmZones.map((zone, index) => {
                  const zoneInfo = getZoneDisplayInfo(zone);
                  const isExpanded = expandedZones.has(zone.id);
                  
                  return (
                    <div
                      key={zone.id}
                      className={`zone-list-item rounded-lg border transition-all duration-200 ${
                        selectedZoneId === zone.id
                          ? 'selected alarm bg-red-600/20 border-red-600/50 shadow-lg shadow-red-600/10'
                          : 'bg-slate-900 border-slate-600 hover:border-red-600/30 hover:bg-slate-800/50 hover:shadow-md'
                      }`}
                    >
                      {/* Zone Header */}
                      <div
                        className="p-3 cursor-pointer"
                        onClick={() => handleZoneSelect(zone.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Shield className="size-4 text-red-500" />
                            <div>
                              <div className="text-sm text-slate-200 font-medium">
                                报警区域 {index + 1}
                              </div>
                              <div className="text-xs text-slate-400">
                                面积: {(zoneInfo.area * 100).toFixed(1)}%
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <Button
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                toggleZoneExpansion(zone.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="p-1 h-auto text-slate-400 hover:text-slate-200"
                              title="查看详情"
                            >
                              <MapPin className="size-3" />
                            </Button>
                            <Button
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                onZoneVisibilityToggle(zone.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="p-1 h-auto text-slate-400 hover:text-slate-200"
                              title={zone.visible ? '隐藏区域' : '显示区域'}
                            >
                              {zone.visible ? (
                                <Eye className="size-3" />
                              ) : (
                                <EyeOff className="size-3" />
                              )}
                            </Button>
                            <Button
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                handleZoneDelete(zone.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="p-1 h-auto text-slate-400 hover:text-red-400"
                              title="删除区域"
                            >
                              <Trash2 className="size-3" />
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Zone Details - Expanded */}
                      {isExpanded && (
                        <div className="px-3 pb-3 border-t border-red-600/20">
                          <div className="mt-2 space-y-2 text-xs">
                            {/* Position Information */}
                            <div className="flex items-center gap-2">
                              <MapPin className="size-3 text-slate-400" />
                              <span className="text-slate-400">位置:</span>
                              <span className="text-slate-200">
                                ({formatCoordinate(zoneInfo.bounds.minX)}, {formatCoordinate(zoneInfo.bounds.minY)}) 
                                → ({formatCoordinate(zoneInfo.bounds.maxX)}, {formatCoordinate(zoneInfo.bounds.maxY)})
                              </span>
                            </div>
                            
                            {/* Dimensions */}
                            <div className="flex items-center gap-2">
                              <Ruler className="size-3 text-slate-400" />
                              <span className="text-slate-400">尺寸:</span>
                              <span className="text-slate-200">
                                {formatCoordinate(zoneInfo.bounds.width)} × {formatCoordinate(zoneInfo.bounds.height)}
                              </span>
                            </div>

                            {/* Status */}
                            <div className="flex items-center gap-2">
                              <div className={`size-2 rounded-full ${zone.visible ? 'bg-green-400' : 'bg-slate-500'}`}></div>
                              <span className="text-slate-400">状态:</span>
                              <span className={zone.visible ? 'text-green-400' : 'text-slate-400'}>
                                {zone.visible ? '显示' : '隐藏'}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Zone Summary */}
      <div className="mt-3 pt-3 border-t border-slate-600">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-4">
            <span>警告: {warningZones.length}</span>
            <span>报警: {alarmZones.length}</span>
          </div>
          <div>
            可见: {zones.filter(z => z.visible).length}/{zones.length}
          </div>
        </div>
      </div>
    </div>
  );
}