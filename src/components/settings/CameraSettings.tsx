import { ArrowLeft, Camera, Video, ArrowUp, ArrowDown, ArrowLeft as ArrowLeftIcon, ArrowRight, Minus } from 'lucide-react';
import { CameraGroup } from '../../App';

interface CameraSettingsProps {
  onBack: () => void;
  cameraGroups: CameraGroup[];
  activeCameraId: string;
  setActiveCameraId: (id: string) => void;
}

const directionIcons = {
  forward: ArrowUp,
  backward: ArrowDown,
  left: ArrowLeftIcon,
  right: ArrowRight,
  idle: Minus
};

const directionLabels = {
  forward: '前进方向',
  backward: '后退方向',
  left: '左转方向',
  right: '右转方向',
  idle: '静止'
};

export function CameraSettings({ 
  onBack, 
  cameraGroups, 
  activeCameraId, 
  setActiveCameraId
}: CameraSettingsProps) {

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
            <Camera className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">方向摄像头</h2>
          </div>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-6xl mx-auto">
        {/* 按方向分组显示摄像头 */}
        {cameraGroups
          .filter(group => group.direction !== 'idle')
          .map((group) => {
            const DirectionIcon = directionIcons[group.direction];
            
            return (
              <div key={group.direction} className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
                {/* 方向组标题 */}
                <div className="px-6 py-4 bg-slate-700 border-b border-slate-600">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <DirectionIcon className="size-6 text-cyan-400" />
                      <h3 className="text-slate-100 tracking-wide">{directionLabels[group.direction]}</h3>
                      <span className="px-3 py-1 bg-slate-800 text-slate-300 text-sm rounded-full font-mono">
                        {group.cameras.length} 个摄像头
                      </span>
                    </div>
                  </div>
                </div>

                {/* 摄像头列表 */}
                <div className="p-4 space-y-3">
                  {group.cameras.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                      <Camera className="size-12 mx-auto mb-3 opacity-50" />
                      <p>该方向暂无摄像头</p>
                      <p className="text-sm mt-2">请前往"摄像头列表"添加摄像头</p>
                    </div>
                  ) : (
                    group.cameras.map((camera) => (
                      <div
                        key={camera.id}
                        className={`bg-slate-900 border rounded-lg p-4 transition-all ${
                          activeCameraId === camera.id 
                            ? 'border-cyan-500 shadow-lg shadow-cyan-500/20' 
                            : 'border-slate-700'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            {/* 图标 */}
                            <div className={`p-3 rounded-lg ${camera.enabled ? 'bg-cyan-600' : 'bg-slate-700'}`}>
                              {camera.enabled ? (
                                <Video className="size-5 text-white" />
                              ) : (
                                <Video className="size-5 text-slate-500" />
                              )}
                            </div>

                            {/* 信息 */}
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h4 className="text-slate-100 font-mono">{camera.name}</h4>
                                {activeCameraId === camera.id && (
                                  <span className="px-2 py-0.5 bg-cyan-600 text-white text-xs rounded font-mono">
                                    当前显示
                                  </span>
                                )}
                                {!camera.enabled && (
                                  <span className="px-2 py-0.5 bg-slate-700 text-slate-400 text-xs rounded font-mono">
                                    已禁用
                                  </span>
                                )}
                              </div>
                              <p className="text-slate-400 text-sm mt-1 font-mono">{camera.url}</p>
                              <div className="flex items-center gap-4 mt-2 text-sm">
                                <span className="text-slate-500 font-mono">
                                  {camera.resolution} @ {camera.fps}fps
                                </span>
                                <div className="flex items-center gap-1">
                                  <div className={`size-2 rounded-full ${
                                    camera.status === 'online' ? 'bg-green-500 animate-pulse shadow-lg shadow-green-500/50' : 'bg-red-500'
                                  }`}></div>
                                  <span className={`font-mono ${camera.status === 'online' ? 'text-green-500' : 'text-red-500'}`}>
                                    {camera.status === 'online' ? '在线' : '离线'}
                                  </span>
                                </div>
                              </div>

                              {/* 参数信息 */}
                              <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
                                <span className="font-mono">亮度: {camera.brightness}%</span>
                                <span className="font-mono">对比度: {camera.contrast}%</span>
                              </div>
                            </div>
                          </div>

                          {/* 操作按钮 */}
                          {camera.enabled && camera.status === 'online' && activeCameraId !== camera.id && (
                            <button
                              onClick={() => setActiveCameraId(camera.id)}
                              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors text-sm"
                            >
                              切换显示
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}

        {/* 说明信息 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-cyan-400 mb-3 tracking-wide">使用说明</h3>
          <div className="space-y-2 text-slate-300 text-sm">
            <p>• 此界面显示按运动方向分组的摄像头配置信息</p>
            <p>• 系统会根据9轴传感器检测的运动方向自动切换到对应摄像头</p>
            <p>• 如需添加、删除或编辑摄像头，请前往"摄像头列表"界面</p>
            <p>• 点击"切换显示"可以手动切换到指定摄像头查看画面</p>
          </div>
        </div>

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
