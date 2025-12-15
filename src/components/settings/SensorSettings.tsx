import { ArrowLeft, Compass, Activity, RotateCw, CheckCircle2, ArrowUp, ArrowDown, ArrowLeft as ArrowLeftIcon, ArrowRight, Wifi, WifiOff, AlertCircle, Clock } from 'lucide-react';
import { Direction } from '../../App';
import { Switch } from '../ui/switch';
import { useState, useEffect } from 'react';
import { useSensorStream } from '../../hooks/useSensorStream';
import { formatNumber, getMotionLabel, getMotionColorScheme, formatTimestamp } from '../../utils/sensorDataFormatter';
import axios from 'axios';

interface SensorSettingsProps {
  onBack: () => void;
  currentDirection: Direction;
}

export function SensorSettings({ onBack, currentDirection }: SensorSettingsProps) {
  const [calibrationMode, setCalibrationMode] = useState(false);
  const [autoDetect, setAutoDetect] = useState(true);

  // 使用useSensorStream Hook订阅实时数据（自动连接和断开）
  const {
    isConnected,
    connectionStatus,
    sensorData,
    motionCommand,
    error,
    lastUpdateTime,
    isDelayed,
  } = useSensorStream({ autoConnect: true });

  // 组件卸载时关闭串口和停止线程
  useEffect(() => {
    return () => {
      // 清理函数：组件离开时调用后端API停止传感器
      const stopSensor = async () => {
        try {
          await axios.post('http://127.0.0.1:8000/api/sensor/stop');
          console.log('[SensorSettings] 传感器已停止');
        } catch (err) {
          console.error('[SensorSettings] 停止传感器失败:', err);
        }
      };
      stopSensor();
    };
  }, []);

  // 运动方向图标映射
  const directionIcons = {
    forward: ArrowUp,
    backward: ArrowDown,
    turn_left: ArrowLeftIcon,
    turn_right: ArrowRight,
    stationary: Activity,
  };

  // 获取当前运动指令的显示信息
  const currentMotion = motionCommand?.command || 'stationary';
  const motionLabel = getMotionLabel(currentMotion);
  const colorScheme = getMotionColorScheme(currentMotion);
  const DirectionIcon = directionIcons[currentMotion];

  return (
    <div className="h-full bg-slate-900 overflow-y-auto">
      {/* 标题栏 */}
      <div className="bg-slate-950 border-b border-slate-700 px-4 py-4 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="size-5 text-slate-400" />
          </button>
          <Compass className="size-5 text-cyan-500" />
          <h2 className="text-slate-100">9轴传感器设置</h2>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        {/* 连接状态指示器 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isConnected ? (
                <Wifi className="size-5 text-green-500" />
              ) : (
                <WifiOff className="size-5 text-slate-500" />
              )}
              <div>
                <div className="text-slate-200 font-medium">
                  {connectionStatus === 'connected' && '已连接'}
                  {connectionStatus === 'connecting' && '连接中...'}
                  {connectionStatus === 'disconnected' && '已断开'}
                  {connectionStatus === 'error' && '连接错误'}
                </div>
                {lastUpdateTime && (
                  <div className="text-slate-400 text-sm flex items-center gap-2">
                    <Clock className="size-3" />
                    最后更新: {formatTimestamp(lastUpdateTime.toISOString())}
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isDelayed && (
                <div className="flex items-center gap-2 text-yellow-500 text-sm">
                  <AlertCircle className="size-4" />
                  数据延迟
                </div>
              )}
              <div className={`px-3 py-1 rounded-full text-sm ${
                isConnected ? 'bg-green-950 text-green-500' : 'bg-slate-700 text-slate-400'
              }`}>
                {isConnected ? '实时' : '离线'}
              </div>
            </div>
          </div>
        </div>

        {/* 错误消息显示 */}
        {error && (
          <div className="bg-red-950 border border-red-500 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="size-5 text-red-500" />
              <div>
                <div className="text-red-500 font-medium">错误</div>
                <div className="text-red-400 text-sm">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* 当前运动状态 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">当前运动状态</h3>
          <div className={`flex items-center justify-center gap-4 p-8 rounded-lg transition-all ${colorScheme.bg} border-2 ${colorScheme.border}`}>
            <DirectionIcon className={`size-16 ${colorScheme.text}`} />
            <div>
              <div className={`text-3xl ${colorScheme.text}`}>{motionLabel}</div>
              <div className="text-sm opacity-75 mt-1">
                {isConnected ? '实时检测中...' : '等待连接...'}
              </div>
              {motionCommand && (
                <div className="text-sm opacity-75 mt-2 space-y-1">
                  <div>线性强度: {formatNumber(motionCommand.intensity)}</div>
                  <div>角度强度: {formatNumber(motionCommand.angularIntensity)}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 传感器实时数据 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4 flex items-center gap-2">
            <Activity className="size-5 text-cyan-500" />
            实时传感器数据
          </h3>
          {sensorData ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* 加速度 */}
              <div className="bg-slate-900 rounded-lg p-4 transition-all">
                <div className="text-slate-300 mb-3 font-medium">加速度 (g)</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">X轴:</span>
                    <span className="text-green-500 font-mono text-base">
                      {formatNumber(sensorData.acceleration.x)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Y轴:</span>
                    <span className="text-green-500 font-mono text-base">
                      {formatNumber(sensorData.acceleration.y)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Z轴:</span>
                    <span className="text-green-500 font-mono text-base">
                      {formatNumber(sensorData.acceleration.z)}
                    </span>
                  </div>
                </div>
              </div>

              {/* 角速度 */}
              <div className="bg-slate-900 rounded-lg p-4 transition-all">
                <div className="text-slate-300 mb-3 font-medium">角速度 (°/s)</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">X轴:</span>
                    <span className="text-blue-500 font-mono text-base">
                      {formatNumber(sensorData.angularVelocity.x)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Y轴:</span>
                    <span className="text-blue-500 font-mono text-base">
                      {formatNumber(sensorData.angularVelocity.y)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Z轴:</span>
                    <span className="text-blue-500 font-mono text-base">
                      {formatNumber(sensorData.angularVelocity.z)}
                    </span>
                  </div>
                </div>
              </div>

              {/* 角度 */}
              <div className="bg-slate-900 rounded-lg p-4 transition-all">
                <div className="text-slate-300 mb-3 font-medium">角度 (°)</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">X轴:</span>
                    <span className="text-purple-500 font-mono text-base">
                      {formatNumber(sensorData.angles.x)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Y轴:</span>
                    <span className="text-purple-500 font-mono text-base">
                      {formatNumber(sensorData.angles.y)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Z轴:</span>
                    <span className="text-purple-500 font-mono text-base">
                      {formatNumber(sensorData.angles.z)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              {isConnected ? '等待数据...' : '未连接到传感器'}
            </div>
          )}
        </div>

        {/* 方向映射配置 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">方向与摄像头映射</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
              <div className="flex items-center gap-3">
                <ArrowUp className="size-5 text-green-500" />
                <span className="text-slate-200">前进</span>
              </div>
              <span className="text-slate-400">→ 前方摄像头</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
              <div className="flex items-center gap-3">
                <ArrowDown className="size-5 text-yellow-500" />
                <span className="text-slate-200">后退</span>
              </div>
              <span className="text-slate-400">→ 后方摄像头</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
              <div className="flex items-center gap-3">
                <ArrowLeftIcon className="size-5 text-blue-500" />
                <span className="text-slate-200">左转</span>
              </div>
              <span className="text-slate-400">→ 左侧摄像头</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
              <div className="flex items-center gap-3">
                <ArrowRight className="size-5 text-purple-500" />
                <span className="text-slate-200">右转</span>
              </div>
              <span className="text-slate-400">→ 右侧摄像头</span>
            </div>
          </div>
        </div>

        {/* 传感器选项 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">传感器选项</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-slate-200">自动方向检测</div>
                <div className="text-slate-400 text-sm">自动识别运动方向</div>
              </div>
              <Switch checked={autoDetect} onCheckedChange={setAutoDetect} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-slate-200">校准模式</div>
                <div className="text-slate-400 text-sm">启用传感器校准</div>
              </div>
              <Switch checked={calibrationMode} onCheckedChange={setCalibrationMode} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-slate-200">数据平滑</div>
                <div className="text-slate-400 text-sm">减少数据波动</div>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </div>

        {/* 校准按钮 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">传感器校准</h3>
          <p className="text-slate-400 text-sm mb-4">
            定期校准传感器可以提高方向检测的准确性。校准过程需要将设备保持静止约30秒。
          </p>
          <button className="w-full px-4 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2">
            <RotateCw className="size-5" />
            开始校准传感器
          </button>
        </div>

        {/* 保存按钮 */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onBack}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            取消
          </button>
          <button className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors flex items-center gap-2">
            <CheckCircle2 className="size-4" />
            保存设置
          </button>
        </div>
      </div>
    </div>
  );
}
