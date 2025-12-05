/**
 * Direction Cameras Settings Component
 * 方向摄像头页面 - 展示前进、后退、左转、右转属性的摄像头列表
 */

import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowUp, ArrowDown, ArrowLeftCircle, ArrowRightCircle, Camera, Circle, Wifi, WifiOff, Info, Compass } from 'lucide-react';
import { useCameraStore } from '../../stores/cameraStore';
import { Camera as CameraType } from '../../services/cameraService';

interface DirectionCamerasSettingsProps {
  onBack: () => void;
}

type Direction = 'forward' | 'backward' | 'left' | 'right';

interface DirectionConfig {
  key: Direction;
  label: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  borderColor: string;
}

const directionConfigs: DirectionConfig[] = [
  {
    key: 'forward',
    label: '前进',
    icon: <ArrowUp className="size-6" />,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30'
  },
  {
    key: 'backward',
    label: '后退',
    icon: <ArrowDown className="size-6" />,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30'
  },
  {
    key: 'left',
    label: '左转',
    icon: <ArrowLeftCircle className="size-6" />,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30'
  },
  {
    key: 'right',
    label: '右转',
    icon: <ArrowRightCircle className="size-6" />,
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30'
  }
];

export function DirectionCamerasSettings({ onBack }: DirectionCamerasSettingsProps) {
  const { cameras, loading, error, fetchCameras } = useCameraStore();
  const [selectedDirection, setSelectedDirection] = useState<Direction>('forward');

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  // 按方向分组摄像头
  const getCamerasByDirection = (direction: Direction): CameraType[] => {
    return cameras.filter(camera => 
      camera.directions && camera.directions.includes(direction)
    );
  };

  const selectedConfig = directionConfigs.find(d => d.key === selectedDirection)!;
  const directionCameras = getCamerasByDirection(selectedDirection);

  return (
    <div className="h-full bg-slate-900 overflow-y-auto">
      {/* 标题栏 */}
      <div className="bg-slate-950 border-b border-slate-700 px-4 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="size-5 text-slate-400" />
            </button>
            <Compass className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">方向摄像头</h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Camera className="size-4" />
            <span>共 {cameras.length} 个摄像头</span>
          </div>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
          {/* 方向选择器 */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {directionConfigs.map((config) => {
              const count = getCamerasByDirection(config.key).length;
              const isSelected = selectedDirection === config.key;
              
              return (
                <button
                  key={config.key}
                  onClick={() => setSelectedDirection(config.key)}
                  className={`
                    p-6 rounded-xl border-2 transition-all duration-300
                    ${isSelected 
                      ? `${config.bgColor} ${config.borderColor} shadow-lg` 
                      : 'bg-slate-800/30 border-slate-700/50 hover:bg-slate-800/50'
                    }
                  `}
                >
                  <div className="flex flex-col items-center gap-3">
                    <div className={`${isSelected ? config.color : 'text-slate-400'} transition-colors`}>
                      {config.icon}
                    </div>
                    <div className="text-center">
                      <div className={`font-semibold ${isSelected ? 'text-slate-100' : 'text-slate-300'}`}>
                        {config.label}
                      </div>
                      <div className={`text-sm mt-1 ${isSelected ? config.color : 'text-slate-500'}`}>
                        {count} 个摄像头
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* 摄像头列表 */}
          <div className={`rounded-xl border-2 ${selectedConfig.borderColor} ${selectedConfig.bgColor} p-6`}>
            <div className="flex items-center gap-3 mb-6">
              <div className={selectedConfig.color}>
                {selectedConfig.icon}
              </div>
              <h3 className="text-lg font-semibold text-slate-100">
                {selectedConfig.label}方向摄像头
              </h3>
              <span className={`text-sm ${selectedConfig.color}`}>
                ({directionCameras.length})
              </span>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
                <p className="text-slate-400 mt-4">加载中...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-red-400">{error}</p>
              </div>
            ) : directionCameras.length === 0 ? (
              <div className="text-center py-12">
                <Camera className="size-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">该方向暂无摄像头</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {directionCameras.map((camera) => (
                  <div
                    key={camera.id}
                    className="bg-slate-800/50 rounded-lg border border-slate-700/50 p-4 hover:bg-slate-800/70 transition-all duration-200"
                  >
                    {/* 摄像头状态和名称 */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Camera className="size-5 text-slate-400" />
                        <h4 className="font-medium text-slate-100">{camera.name}</h4>
                      </div>
                      <div className="flex items-center gap-2">
                        {camera.status === 'online' ? (
                          <>
                            <Wifi className="size-4 text-green-400" />
                            <span className="text-xs text-green-400">在线</span>
                          </>
                        ) : (
                          <>
                            <WifiOff className="size-4 text-red-400" />
                            <span className="text-xs text-red-400">离线</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* 摄像头信息 */}
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">地址:</span>
                        <span className="text-slate-300 font-mono">{camera.address}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">码流:</span>
                        <span className="text-slate-300">
                          {camera.stream_type === 'main' ? '主码流' : '子码流'}
                        </span>
                      </div>
                      
                      {/* 方向标签 */}
                      <div className="pt-2 border-t border-slate-700/50">
                        <div className="flex flex-wrap gap-1">
                          {camera.directions.map((dir) => {
                            const dirConfig = directionConfigs.find(d => d.key === dir);
                            if (!dirConfig) return null;
                            
                            return (
                              <span
                                key={dir}
                                className={`
                                  px-2 py-1 rounded text-xs font-medium
                                  ${dirConfig.bgColor} ${dirConfig.color}
                                  border ${dirConfig.borderColor}
                                `}
                              >
                                {dirConfig.label}
                              </span>
                            );
                          })}
                        </div>
                      </div>

                      {/* 启用状态 */}
                      <div className="flex items-center justify-between pt-2">
                        <span className="text-slate-400">状态:</span>
                        <div className="flex items-center gap-2">
                          <Circle 
                            className={`size-2 ${camera.enabled ? 'fill-green-400 text-green-400' : 'fill-slate-500 text-slate-500'}`}
                          />
                          <span className={camera.enabled ? 'text-green-400' : 'text-slate-500'}>
                            {camera.enabled ? '已启用' : '已禁用'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 底部说明信息 */}
          <div style={{ marginTop: '3rem' }} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <Info className="size-5 text-cyan-400 shrink-0 mt-0.5" />
              <div className="space-y-2 text-sm text-slate-300">
                <p className="font-medium text-slate-200">方向摄像头说明：</p>
                <ul className="space-y-1 text-slate-400">
                  <li>• 每个摄像头可以配置多个方向属性（前进、后退、左转、右转）</li>
                  <li>• 系统根据9轴传感器检测到的运动方向，自动切换对应方向的摄像头</li>
                  <li>• 主码流提供高清画质，子码流用于低带宽场景</li>
                  <li>• 只有"已启用"且"在线"的摄像头才会参与自动切换</li>
                </ul>
              </div>
            </div>
          </div>
      </div>
    </div>
  );
}
