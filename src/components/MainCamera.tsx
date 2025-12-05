import { Video, Crosshair, Shield, AlertTriangle } from 'lucide-react';
import { Direction } from '../App';

interface MainCameraProps {
  direction: Direction;
  activeCameraId: string;
}

const directionLabels: Record<Direction, string> = {
  forward: '前进',
  backward: '后退',
  left: '左转',
  right: '右转',
  idle: '静止'
};

const directionColors: Record<Direction, string> = {
  forward: 'bg-cyan-500 shadow-cyan-500/50',
  backward: 'bg-cyan-500 shadow-cyan-500/50',
  left: 'bg-cyan-500 shadow-cyan-500/50',
  right: 'bg-cyan-500 shadow-cyan-500/50',
  idle: 'bg-slate-500 shadow-slate-500/50'
};

export function MainCamera({ direction, activeCameraId }: MainCameraProps) {
  const cameraNames: Record<string, string> = {
    'camera-1': '前方摄像头',
    'camera-2': '后方摄像头',
    'camera-3': '左侧摄像头',
    'camera-4': '右侧摄像头'
  };

  return (
    <div className="h-full w-full bg-slate-900 relative">
      {/* 主摄像头画面 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* 模拟视频画面 */}
        <div className="w-full h-full flex items-center justify-center">
          <Video className="size-32 text-slate-700/50" />
        </div>

        {/* AI检测框示例 */}
        <div className="absolute top-1/4 left-1/3 w-48 h-64 border-2 border-red-500 shadow-lg shadow-red-500/30 animate-pulse">
          <div className="bg-gradient-to-r from-red-600 to-red-500 text-white px-3 py-1.5 text-sm font-mono -mt-8 shadow-lg">
            ⚠️ 人员检测
          </div>
          <div className="absolute top-2 right-2 bg-red-500/90 backdrop-blur-sm text-white px-2 py-1 rounded text-xs font-mono">
            95%
          </div>
        </div>

        <div className="absolute top-1/2 right-1/4 w-32 h-32 border-2 border-green-500 shadow-lg shadow-green-500/30">
          <div className="bg-gradient-to-r from-green-600 to-green-500 text-white px-3 py-1.5 text-sm font-mono -mt-8 shadow-lg">
            🎯 设备追踪
          </div>
          <div className="absolute top-2 right-2 bg-green-500/90 backdrop-blur-sm text-white px-2 py-1 rounded text-xs font-mono">
            87%
          </div>
        </div>

        {/* 网格线 */}
        <svg className="absolute inset-0 w-full h-full opacity-10 pointer-events-none">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-cyan-400"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {/* 十字准线 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <Crosshair className="size-16 text-cyan-500/30" />
        </div>

        {/* 角落装饰 */}
        <div className="absolute top-4 left-4 w-12 h-12 border-l-2 border-t-2 border-cyan-500/50"></div>
        <div className="absolute top-4 right-4 w-12 h-12 border-r-2 border-t-2 border-cyan-500/50"></div>
        <div className="absolute bottom-4 left-4 w-12 h-12 border-l-2 border-b-2 border-cyan-500/50"></div>
        <div className="absolute bottom-4 right-4 w-12 h-12 border-r-2 border-b-2 border-cyan-500/50"></div>
      </div>

      {/* 状态信息叠加层 */}
      <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-start">
        {/* 左侧信息 */}
        <div className="space-y-3">
          {/* 摄像头信息 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <div className="size-3 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/50"></div>
              <span className="text-cyan-400 font-mono">{cameraNames[activeCameraId]}</span>
            </div>
          </div>

          {/* 运动方向 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <div className={`size-3 rounded-full shadow-lg ${directionColors[direction]}`}></div>
              <span className="text-slate-300 font-mono">方向: </span>
              <span className="text-cyan-400 font-mono">{directionLabels[direction]}</span>
            </div>
          </div>

          {/* AI状态 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-green-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <Shield className="size-5 text-green-500 animate-pulse" />
              <span className="text-slate-300 font-mono">AI追踪: </span>
              <span className="text-green-400 font-mono">激活</span>
            </div>
          </div>
        </div>

        {/* 右侧检测统计 - 移除时间显示 */}
        <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 space-y-2 shadow-xl">
          <div className="text-cyan-400 text-sm font-mono mb-2">实时统计</div>
          <div className="flex items-center gap-3 text-sm">
            <div className="size-2 bg-green-500 rounded-full shadow-lg shadow-green-500/50"></div>
            <span className="text-slate-400 font-mono">目标:</span>
            <span className="text-green-400 font-mono">2</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <div className="size-2 bg-red-500 rounded-full shadow-lg shadow-red-500/50"></div>
            <span className="text-slate-400 font-mono">警告:</span>
            <span className="text-red-400 font-mono">1</span>
          </div>
        </div>
      </div>

      {/* 底部信息栏 */}
      <div className="absolute bottom-0 left-0 right-0 p-6">
        <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-6 py-3 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">分辨率:</span>
                <span className="text-cyan-400 font-mono">1920x1080</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">帧率:</span>
                <span className="text-cyan-400 font-mono">30 FPS</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">延迟:</span>
                <span className="text-green-400 font-mono">28ms</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="size-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
              <span className="text-green-400 font-mono">系统运行正常</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}