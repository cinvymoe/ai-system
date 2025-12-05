import { ArrowLeft, Camera, Save, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';
import { useCameraStore } from '../../stores/cameraStore';
import type { CameraUpdate } from '../../services/cameraService';

type Direction = 'forward' | 'backward' | 'left' | 'right' | 'idle';

interface EditCameraSettingsProps {
  onBack: () => void;
  editingCameraId: string | null;
  setEditingCameraId: (id: string | null) => void;
}

const directionLabels: Record<Direction, string> = {
  forward: '前进',
  backward: '后退',
  left: '左转',
  right: '右转',
  idle: '静止'
};

const directionOptions = [
  { value: 'forward', label: '前进方向' },
  { value: 'backward', label: '后退方向' },
  { value: 'left', label: '左转方向' },
  { value: 'right', label: '右转方向' },
  { value: 'idle', label: '空闲' },
];

export function EditCameraSettings({ onBack, editingCameraId, setEditingCameraId }: EditCameraSettingsProps) {
  const { cameras, loading, error, updateCamera, clearError } = useCameraStore();
  
  // 查找摄像头
  const camera = cameras.find(cam => cam.id === editingCameraId);
  
  const [name, setName] = useState(camera?.name || '');
  const [address, setAddress] = useState(camera?.address || '');
  const [username, setUsername] = useState(camera?.username || '');
  const [password, setPassword] = useState(camera?.password || '');
  const [channel, setChannel] = useState(camera?.channel || 1);
  const [streamType, setStreamType] = useState<'main' | 'sub'>(camera?.stream_type || 'main');
  const [directions, setDirections] = useState<Direction[]>(camera?.directions || ['forward']);
  const [hasChanges, setHasChanges] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');

  // 当摄像头数据加载后，更新表单状态
  useEffect(() => {
    if (camera) {
      setName(camera.name);
      setAddress(camera.address);
      setUsername(camera.username);
      setPassword(camera.password);
      setChannel(camera.channel);
      setStreamType(camera.stream_type);
      setDirections(camera.directions);
    }
  }, [camera]);

  useEffect(() => {
    if (camera) {
      const changed = 
        name !== camera.name ||
        address !== camera.address ||
        username !== camera.username ||
        password !== camera.password ||
        channel !== camera.channel ||
        streamType !== camera.stream_type ||
        JSON.stringify(directions) !== JSON.stringify(camera.directions);
      setHasChanges(changed);
    }
  }, [name, address, username, password, channel, streamType, directions, camera]);

  const toggleDirection = (direction: Direction) => {
    setDirections(prev => 
      prev.includes(direction)
        ? prev.filter(d => d !== direction)
        : [...prev, direction]
    );
  };

  const handleSave = async () => {
    if (!camera) return;
    
    setSuccessMessage('');
    clearError();
    
    try {
      const updates: CameraUpdate = {
        name,
        address,
        username,
        password,
        channel,
        stream_type: streamType,
        directions
      };
      
      await updateCamera(camera.id, updates);
      setHasChanges(false);
      setSuccessMessage('设置已保存！');
      
      // 延迟返回，让用户看到成功消息
      setTimeout(() => {
        onBack();
      }, 1500);
    } catch (err) {
      // 错误已经在 store 中处理
    }
  };

  const handleReset = () => {
    if (camera) {
      setName(camera.name);
      setAddress(camera.address);
      setUsername(camera.username);
      setPassword(camera.password);
      setChannel(camera.channel);
      setStreamType(camera.stream_type);
      setDirections(camera.directions);
      setHasChanges(false);
    }
  };

  // 生成URL预览
  const generateUrlPreview = () => {
    if (address && username && password) {
      const streamSuffix = streamType === 'main' ? '01' : '02';
      return `rtsp://${username}:${password}@${address}/Streaming/Channels/${channel}${streamSuffix}`;
    }
    return camera?.url || '';
  };

  if (!camera) {
    return (
      <div className="h-full bg-slate-900 flex items-center justify-center">
        <div className="text-center text-slate-500">
          <AlertCircle className="size-16 mx-auto mb-4 opacity-30" />
          <p>未找到摄像头</p>
        </div>
      </div>
    );
  }

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
            <div>
              <h2 className="text-slate-100">摄像头设置</h2>
              {camera && (
                <p className="text-xs text-slate-400 mt-0.5">
                  方向: {camera.directions.map(d => directionLabels[d]).join(', ')}
                </p>
              )}
            </div>
          </div>
          {hasChanges && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                重置
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/30 border border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="size-4" />
                    保存更改
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        {/* 成功消息 */}
        {successMessage && (
          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 flex items-start gap-3">
            <CheckCircle2 className="size-5 text-green-500 shrink-0 mt-0.5" />
            <div>
              <div className="text-green-400 font-semibold">{successMessage}</div>
            </div>
          </div>
        )}

        {/* 错误消息 */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="size-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <div className="text-red-400 font-semibold mb-1">更新失败</div>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}
        {/* 基本信息 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-cyan-400 mb-4 tracking-wide">基本信息</h3>
          <div className="space-y-4">
            {/* 摄像头名称 */}
            <div>
              <label className="text-slate-300 text-sm mb-2 block">摄像头名称</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例如：前方主摄像头"
                className="bg-slate-900 border-slate-700 text-slate-200"
              />
            </div>

            {/* IP地址 */}
            <div>
              <label className="text-slate-300 text-sm mb-2 block">IP地址</label>
              <Input
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="192.168.1.254"
                className="bg-slate-900 border-slate-700 text-slate-200 font-mono"
              />
            </div>

            {/* 用户名和密码 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-slate-300 text-sm mb-2 block">用户名</label>
                <Input
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  className="bg-slate-900 border-slate-700 text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-300 text-sm mb-2 block">密码</label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="bg-slate-900 border-slate-700 text-slate-200"
                />
              </div>
            </div>

            {/* 通道号和码流类型 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-slate-300 text-sm mb-2 block">通道号</label>
                <Input
                  type="number"
                  min="1"
                  max="999"
                  value={channel}
                  onChange={(e) => setChannel(parseInt(e.target.value) || 1)}
                  className="bg-slate-900 border-slate-700 text-slate-200"
                />
              </div>
              <div>
                <label className="text-slate-300 text-sm mb-2 block">码流类型</label>
                <Select
                  value={streamType}
                  onValueChange={(value: 'main' | 'sub') => setStreamType(value)}
                >
                  <SelectTrigger className="bg-slate-900 border-slate-700 text-slate-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="main">主码流</SelectItem>
                    <SelectItem value="sub">子码流</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* 所属方向（多选） */}
            <div>
              <label className="text-slate-300 text-sm mb-2 block">所属方向</label>
              <div className="grid grid-cols-2 gap-3">
                {directionOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`flex items-center gap-2 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                      directions.includes(option.value as Direction)
                        ? 'bg-cyan-900/30 border-cyan-500/50'
                        : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                    }`}
                    onClick={() => toggleDirection(option.value as Direction)}
                  >
                    <Checkbox
                      checked={directions.includes(option.value as Direction)}
                      onCheckedChange={() => toggleDirection(option.value as Direction)}
                    />
                    <span className="text-slate-200 text-sm">{option.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* URL预览 */}
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
              <label className="text-slate-400 text-xs mb-2 block">URL预览（自动生成）</label>
              <div className="text-slate-300 text-sm font-mono break-all">
                {generateUrlPreview()}
              </div>
            </div>

            {/* 状态 */}
            <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg">
              <span className="text-slate-400">状态</span>
              <div className="flex items-center gap-2">
                <div className={`size-2 rounded-full ${
                  camera.status === 'online' 
                    ? 'bg-green-500 animate-pulse shadow-lg shadow-green-500/50' 
                    : 'bg-red-500'
                }`}></div>
                <span className={`font-mono text-sm ${
                  camera.status === 'online' ? 'text-green-500' : 'text-red-500'
                }`}>
                  {camera.status === 'online' ? '在线' : '离线'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 底部按钮 */}
        <div className="flex items-center justify-between pt-4">
          <button
            onClick={onBack}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            返回
          </button>
          {hasChanges && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                重置更改
              </button>
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/30 border border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="size-4" />
                    保存设置
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}