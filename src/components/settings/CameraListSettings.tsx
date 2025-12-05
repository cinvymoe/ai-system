import { ArrowLeft, Camera, Video, Trash2, List, AlertCircle, Settings, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Switch } from '../ui/switch';
import { useCameraStore } from '../../stores/cameraStore';

interface CameraListSettingsProps {
  onBack: () => void;
  onNavigateToAddCamera: () => void;
  onNavigateToEditCamera: (cameraId: string) => void;
}

const directionLabels: Record<string, string> = {
  forward: '前进',
  backward: '后退',
  left: '左转',
  right: '右转',
  idle: '静止'
};

export function CameraListSettings({ 
  onBack, 
  onNavigateToAddCamera,
  onNavigateToEditCamera
}: CameraListSettingsProps) {
  const [filter, setFilter] = useState<'all' | 'online' | 'offline'>('all');
  
  // 从 store 获取数据和操作
  const { cameras, loading, error, fetchCameras, deleteCamera, toggleCameraEnabled, clearError } = useCameraStore();

  // 组件挂载时加载摄像头数据
  useEffect(() => {
    console.log('[CameraListSettings] Component mounted, fetching cameras...');
    fetchCameras().then(() => {
      console.log('[CameraListSettings] Cameras fetched successfully');
    }).catch((err) => {
      console.error('[CameraListSettings] Failed to fetch cameras:', err);
    });
  }, [fetchCameras]);

  // 调试：监听 cameras 变化
  useEffect(() => {
    console.log('[CameraListSettings] Cameras updated:', cameras);
    console.log('[CameraListSettings] Loading state:', loading);
    console.log('[CameraListSettings] Error state:', error);
  }, [cameras, loading, error]);

  // 过滤摄像头
  const filteredCameras = cameras.filter(camera => {
    if (filter === 'all') return true;
    return camera.status === filter;
  });

  const onlineCameras = cameras.filter(c => c.status === 'online').length;
  const offlineCameras = cameras.filter(c => c.status === 'offline').length;

  // 调试：输出过滤结果
  console.log('[CameraListSettings] Filter:', filter);
  console.log('[CameraListSettings] Total cameras:', cameras.length);
  console.log('[CameraListSettings] Filtered cameras:', filteredCameras.length);
  console.log('[CameraListSettings] Online cameras:', onlineCameras);
  console.log('[CameraListSettings] Offline cameras:', offlineCameras);

  // 处理删除操作
  const handleDeleteCamera = async (cameraId: string, cameraName: string) => {
    if (confirm(`确定要删除摄像头"${cameraName}"吗？\n\n此操作不可恢复。`)) {
      try {
        await deleteCamera(cameraId);
      } catch (error) {
        // 错误已经在 store 中处理
      }
    }
  };

  // 处理启用/禁用切换
  const handleToggleEnabled = async (cameraId: string) => {
    try {
      await toggleCameraEnabled(cameraId);
    } catch (error) {
      // 错误已经在 store 中处理
    }
  };

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
            <List className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">摄像头列表</h2>
          </div>
          <button
            onClick={onNavigateToAddCamera}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/30 border border-cyan-400/50"
          >
            <Camera className="size-4" />
            添加摄像头
          </button>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-6xl mx-auto">
        {/* 错误提示 */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="size-5 text-red-500 shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="text-red-400 font-semibold mb-1">加载失败</div>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
            <button
              onClick={() => {
                clearError();
                fetchCameras();
              }}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
            >
              重试
            </button>
          </div>
        )}

        {/* 统计信息 */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">总数</div>
            <div className="text-2xl text-slate-100 font-mono">{cameras.length}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">在线</div>
            <div className="text-2xl text-green-500 font-mono">{onlineCameras}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">离线</div>
            <div className="text-2xl text-red-500 font-mono">{offlineCameras}</div>
          </div>
        </div>

        {/* 过滤器 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <span className="text-slate-400 text-sm">筛选:</span>
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                filter === 'all'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              全部 ({cameras.length})
            </button>
            <button
              onClick={() => setFilter('online')}
              className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                filter === 'online'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              在线 ({onlineCameras})
            </button>
            <button
              onClick={() => setFilter('offline')}
              className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                filter === 'offline'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              离线 ({offlineCameras})
            </button>
          </div>
        </div>

        {/* 摄像头列表 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
          {loading ? (
            <div className="text-center py-12 text-slate-500">
              <Loader2 className="size-16 mx-auto mb-4 opacity-30 animate-spin" />
              <p>加载中...</p>
            </div>
          ) : filteredCameras.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Camera className="size-16 mx-auto mb-4 opacity-30" />
              <p>没有找到摄像头</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-700">
              {filteredCameras.map((camera) => (
                <div key={camera.id} className="p-4 hover:bg-slate-750 transition-colors">
                  <div className="flex items-start gap-4">
                    {/* 左侧图标 */}
                    <div className={`p-3 rounded-lg shrink-0 ${
                      camera.enabled ? 'bg-cyan-600' : 'bg-slate-700'
                    }`}>
                      <Video className={`size-5 ${
                        camera.enabled ? 'text-white' : 'text-slate-500'
                      }`} />
                    </div>

                    {/* 中间信息 */}
                    <div className="flex-1 min-w-0">
                      {/* 第一行：名称和标签 */}
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="text-slate-100 font-mono truncate">{camera.name}</h4>
                        {/* 显示所有方向标签 */}
                        {camera.directions && camera.directions.map((dir) => (
                          <span key={dir} className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded font-mono shrink-0">
                            {directionLabels[dir]}
                          </span>
                        ))}
                        <div className="flex items-center gap-1.5 shrink-0">
                          <div className={`size-2 rounded-full ${
                            camera.status === 'online' 
                              ? 'bg-green-500 animate-pulse shadow-lg shadow-green-500/50' 
                              : 'bg-red-500'
                          }`}></div>
                          <span className={`text-xs font-mono ${
                            camera.status === 'online' ? 'text-green-500' : 'text-red-500'
                          }`}>
                            {camera.status === 'online' ? '在线' : '离线'}
                          </span>
                        </div>
                      </div>

                      {/* 第二行：地址 */}
                      <p className="text-slate-400 text-sm font-mono mb-2 truncate">
                        {camera.url}
                      </p>

                      {/* 第三行：参数 */}
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="font-mono">{camera.resolution}</span>
                        <span className="font-mono">{camera.fps} FPS</span>
                        <span className="font-mono">亮度: {camera.brightness}%</span>
                        <span className="font-mono">对比度: {camera.contrast}%</span>
                      </div>
                    </div>

                    {/* 右侧操作 */}
                    <div className="flex items-center gap-3 shrink-0">
                      <Switch
                        checked={camera.enabled}
                        onCheckedChange={() => handleToggleEnabled(camera.id)}
                        disabled={loading}
                      />
                      <button
                        onClick={() => handleDeleteCamera(camera.id, camera.name)}
                        className="p-2 hover:bg-red-600/20 rounded-lg transition-colors group disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={loading}
                      >
                        <Trash2 className="size-4 text-slate-400 group-hover:text-red-500" />
                      </button>
                      <button
                        onClick={() => onNavigateToEditCamera(camera.id)}
                        className="p-2 hover:bg-cyan-600/20 rounded-lg transition-colors group disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={loading}
                      >
                        <Settings className="size-4 text-slate-400 group-hover:text-cyan-500" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 提示信息 */}
        {offlineCameras > 0 && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="size-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <div className="text-red-400 font-semibold mb-1">检测到离线摄像头</div>
              <p className="text-red-300 text-sm">
                系统检测到 {offlineCameras} 个摄像头处于离线状态，请检查网络连接和设备电源。
              </p>
            </div>
          </div>
        )}

        {/* 返回按钮 */}
        <div className="flex justify-end">
          <button
            onClick={onBack}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            返回
          </button>
        </div>
      </div>
    </div>
  );
}