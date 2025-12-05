import { ArrowLeft, Camera, CheckCircle2, Video, Loader2, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { Checkbox } from '../ui/checkbox';
import { useCameraStore } from '../../stores/cameraStore';
import type { CameraCreate } from '../../services/cameraService';

type Direction = 'forward' | 'backward' | 'left' | 'right' | 'idle';

interface AddCameraSettingsProps {
  onBack: () => void;
}

const directionOptions = [
  { value: 'forward', label: '前进方向' },
  { value: 'backward', label: '后退方向' },
  { value: 'left', label: '左转方向' },
  { value: 'right', label: '右转方向' },
  { value: 'idle', label: '空闲' },
];

export function AddCameraSettings({ onBack }: AddCameraSettingsProps) {
  const { addCamera, loading, error, clearError } = useCameraStore();
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    username: '',
    password: '',
    channel: 1,
    directions: ['forward'] as Direction[],
    stream_type: 'main' as 'main' | 'sub',
    enabled: true,
    status: 'offline' as 'online' | 'offline'
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [checkingOnline, setCheckingOnline] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 清除之前的错误和成功消息
    setErrors({});
    setSuccessMessage('');
    clearError();
    
    // 验证
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = '请输入摄像头名称';
    }
    
    if (!formData.address.trim()) {
      newErrors.address = '请输入摄像头IP地址';
    }
    
    if (!formData.username.trim()) {
      newErrors.username = '请输入用户名';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = '请输入密码';
    }
    
    if (formData.channel < 1 || formData.channel > 999) {
      newErrors.channel = '通道号必须在 1-999 之间';
    }
    
    if (formData.directions.length === 0) {
      newErrors.directions = '请至少选择一个方向';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // 提交到 store
    try {
      setCheckingOnline(true);
      
      const cameraData: CameraCreate = {
        name: formData.name,
        address: formData.address,
        username: formData.username,
        password: formData.password,
        channel: formData.channel,
        directions: formData.directions,
        stream_type: formData.stream_type,
        enabled: formData.enabled,
        status: formData.status
      };
      
      await addCamera(cameraData);
      setCheckingOnline(false);
      setSuccessMessage('摄像头添加成功！');
      
      // 延迟返回，让用户看到成功消息
      setTimeout(() => {
        onBack();
      }, 1500);
    } catch (err: any) {
      setCheckingOnline(false);
      
      // 处理不同类型的错误
      const errorMessage = err.message || '';
      
      if (errorMessage.includes('already exists') || errorMessage.includes('已存在')) {
        setErrors({ name: '摄像头名称已存在' });
      } else if (errorMessage.includes('offline') || errorMessage.includes('unreachable') || errorMessage.includes('离线') || errorMessage.includes('不在线')) {
        setErrors({ address: '摄像头离线或无法访问，请检查摄像头地址和网络连接' });
      }
      // 其他错误会显示在顶部的错误消息区域
    }
  };

  const toggleDirection = (direction: Direction) => {
    setFormData(prev => {
      const directions = prev.directions.includes(direction)
        ? prev.directions.filter(d => d !== direction)
        : [...prev.directions, direction];
      return { ...prev, directions };
    });
    setErrors({ ...errors, directions: '' });
  };

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
          <Camera className="size-5 text-cyan-500" />
          <h2 className="text-slate-100">添加摄像头</h2>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 max-w-3xl mx-auto">
        {/* 成功消息 */}
        {successMessage && (
          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 flex items-start gap-3 mb-6">
            <CheckCircle2 className="size-5 text-green-500 shrink-0 mt-0.5" />
            <div>
              <div className="text-green-400 font-semibold">{successMessage}</div>
            </div>
          </div>
        )}

        {/* 错误消息 */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 flex items-start gap-3 mb-6">
            <AlertCircle className="size-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <div className="text-red-400 font-semibold mb-1">保存失败</div>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 基本信息 */}
          <div className="bg-slate-800 border-2 border-cyan-500/30 rounded-lg p-6 shadow-xl">
            <h3 className="text-cyan-400 mb-6 flex items-center gap-2 tracking-wide">
              <Video className="size-5" />
              基本信息
            </h3>
            
            <div className="space-y-5">
              {/* 摄像头名称 */}
              <div>
                <label className="text-slate-300 text-sm mb-2 block">
                  摄像头名称 <span className="text-red-500">*</span>
                </label>
                <Input
                  value={formData.name}
                  onChange={(e) => {
                    setFormData({ ...formData, name: e.target.value });
                    setErrors({ ...errors, name: '' });
                  }}
                  placeholder="例如：前方主摄像头"
                  className={`bg-slate-900 border-slate-700 text-slate-200 ${
                    errors.name ? 'border-red-500' : ''
                  }`}
                />
                {errors.name && (
                  <p className="text-red-500 text-xs mt-1">{errors.name}</p>
                )}
              </div>

              {/* IP地址 */}
              <div>
                <label className="text-slate-300 text-sm mb-2 block">
                  IP地址 <span className="text-red-500">*</span>
                </label>
                <Input
                  value={formData.address}
                  onChange={(e) => {
                    setFormData({ ...formData, address: e.target.value });
                    setErrors({ ...errors, address: '' });
                  }}
                  placeholder="192.168.1.254"
                  className={`bg-slate-900 border-slate-700 text-slate-200 font-mono ${
                    errors.address ? 'border-red-500' : ''
                  }`}
                />
                {errors.address && (
                  <p className="text-red-500 text-xs mt-1">{errors.address}</p>
                )}
              </div>

              {/* 用户名和密码 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-slate-300 text-sm mb-2 block">
                    用户名 <span className="text-red-500">*</span>
                  </label>
                  <Input
                    value={formData.username}
                    onChange={(e) => {
                      setFormData({ ...formData, username: e.target.value });
                      setErrors({ ...errors, username: '' });
                    }}
                    placeholder="admin"
                    className={`bg-slate-900 border-slate-700 text-slate-200 ${
                      errors.username ? 'border-red-500' : ''
                    }`}
                  />
                  {errors.username && (
                    <p className="text-red-500 text-xs mt-1">{errors.username}</p>
                  )}
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-2 block">
                    密码 <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type="password"
                    value={formData.password}
                    onChange={(e) => {
                      setFormData({ ...formData, password: e.target.value });
                      setErrors({ ...errors, password: '' });
                    }}
                    placeholder="••••••••"
                    className={`bg-slate-900 border-slate-700 text-slate-200 ${
                      errors.password ? 'border-red-500' : ''
                    }`}
                  />
                  {errors.password && (
                    <p className="text-red-500 text-xs mt-1">{errors.password}</p>
                  )}
                </div>
              </div>

              {/* 通道号和码流类型 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-slate-300 text-sm mb-2 block">
                    通道号 <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="999"
                    value={formData.channel}
                    onChange={(e) => {
                      setFormData({ ...formData, channel: parseInt(e.target.value) || 1 });
                      setErrors({ ...errors, channel: '' });
                    }}
                    className={`bg-slate-900 border-slate-700 text-slate-200 ${
                      errors.channel ? 'border-red-500' : ''
                    }`}
                  />
                  {errors.channel && (
                    <p className="text-red-500 text-xs mt-1">{errors.channel}</p>
                  )}
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-2 block">
                    码流类型 <span className="text-red-500">*</span>
                  </label>
                  <Select
                    value={formData.stream_type}
                    onValueChange={(value: 'main' | 'sub') => setFormData({ ...formData, stream_type: value })}
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
                <label className="text-slate-300 text-sm mb-2 block">
                  所属方向 <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {directionOptions.map((option) => (
                    <div
                      key={option.value}
                      className={`flex items-center gap-2 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        formData.directions.includes(option.value as Direction)
                          ? 'bg-cyan-900/30 border-cyan-500/50'
                          : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                      }`}
                      onClick={() => toggleDirection(option.value as Direction)}
                    >
                      <Checkbox
                        checked={formData.directions.includes(option.value as Direction)}
                        onCheckedChange={() => toggleDirection(option.value as Direction)}
                      />
                      <span className="text-slate-200 text-sm">{option.label}</span>
                    </div>
                  ))}
                </div>
                {errors.directions && (
                  <p className="text-red-500 text-xs mt-1">{errors.directions}</p>
                )}
              </div>

              {/* URL预览 */}
              <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                <label className="text-slate-400 text-xs mb-2 block">URL预览（自动生成）</label>
                <div className="text-slate-300 text-sm font-mono break-all">
                  {formData.address && formData.username && formData.password
                    ? `rtsp://${formData.username}:${formData.password}@${formData.address}/Streaming/Channels/${formData.channel}${formData.stream_type === 'main' ? '01' : '02'}`
                    : '请填写完整信息后自动生成'}
                </div>
              </div>

              {/* 启用状态 */}
              <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg">
                <div>
                  <div className="text-slate-200">启用摄像头</div>
                  <div className="text-slate-400 text-sm">添加后立即启用该摄像头</div>
                </div>
                <Switch
                  checked={formData.enabled}
                  onCheckedChange={(checked) => setFormData({ ...formData, enabled: checked })}
                />
              </div>
            </div>
          </div>

          {/* 在线检测提示 */}
          {checkingOnline && (
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 flex items-start gap-3">
              <Loader2 className="size-5 text-blue-500 shrink-0 mt-0.5 animate-spin" />
              <div>
                <div className="text-blue-400 font-semibold mb-1">正在检测摄像头...</div>
                <p className="text-blue-300 text-sm">正在验证摄像头是否在线，请稍候...</p>
              </div>
            </div>
          )}

          {/* 提交按钮 */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onBack}
              className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors border border-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading || checkingOnline}
            >
              取消
            </button>
            <button
              type="submit"
              className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/30 border border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading || checkingOnline}
            >
              {loading || checkingOnline ? (
                <>
                  <Loader2 className="size-5 animate-spin" />
                  {checkingOnline ? '检测中...' : '添加中...'}
                </>
              ) : (
                <>
                  <CheckCircle2 className="size-5" />
                  添加摄像头
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
