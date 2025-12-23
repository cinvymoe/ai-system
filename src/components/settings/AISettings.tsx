import { ArrowLeft, Brain, AlertTriangle, CheckCircle2, Camera, ChevronDown, Power } from 'lucide-react';
import { ZoneManagement } from '../ZoneManagement';
import { useState, useEffect } from 'react';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { cameraService, Camera as CameraType } from '../../services/cameraService';
import { aiSettingsService } from '../../services/aiSettingsService';

interface AISettingsProps {
  onBack: () => void;
}

export function AISettings({ onBack }: AISettingsProps) {
  // AI 设置状态
  const [settingsId, setSettingsId] = useState<number | null>(null);
  const [enabled, setEnabled] = useState(true);
  const [confidence, setConfidence] = useState(75);
  const [soundAlarm, setSoundAlarm] = useState(true);
  const [visualAlarm, setVisualAlarm] = useState(true);
  const [autoScreenshot, setAutoScreenshot] = useState(true);
  const [alarmCooldown, setAlarmCooldown] = useState(5);
  
  // 摄像头状态
  const [cameras, setCameras] = useState<CameraType[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>('');
  const [isLoadingCameras, setIsLoadingCameras] = useState(false);
  const [showCameraDropdown, setShowCameraDropdown] = useState(false);
  
  // UI 状态
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [isLoadingSettings, setIsLoadingSettings] = useState(true);

  // 加载 AI 设置
  useEffect(() => {
    loadAISettings();
    loadCameras();
  }, []);

  const loadAISettings = async () => {
    setIsLoadingSettings(true);
    try {
      const settings = await aiSettingsService.getSettings();
      setSettingsId(settings.id);
      setEnabled(settings.enabled);
      setConfidence(settings.confidence_threshold);
      setSoundAlarm(settings.sound_alarm);
      setVisualAlarm(settings.visual_alarm);
      setAutoScreenshot(settings.auto_screenshot);
      setAlarmCooldown(settings.alarm_cooldown);
      if (settings.camera_id) {
        setSelectedCameraId(settings.camera_id);
      }
      console.log('AI 设置加载成功:', settings);
    } catch (error) {
      console.error('加载 AI 设置失败:', error);
      showMessage('error', '加载设置失败');
    } finally {
      setIsLoadingSettings(false);
    }
  };

  const loadCameras = async () => {
    setIsLoadingCameras(true);
    try {
      const cameraList = await cameraService.getAllCameras();
      setCameras(cameraList);
    } catch (error) {
      console.error('加载摄像头列表失败:', error);
    } finally {
      setIsLoadingCameras(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setSaveMessage({ type, text });
    setTimeout(() => setSaveMessage(null), 3000);
  };

  const handleSave = async () => {
    if (!settingsId) {
      showMessage('error', '设置ID不存在');
      return;
    }

    setIsSaving(true);
    try {
      await aiSettingsService.updateSettings(settingsId, {
        enabled: enabled,
        camera_id: selectedCameraId || null,
        confidence_threshold: confidence,
        sound_alarm: soundAlarm,
        visual_alarm: visualAlarm,
        auto_screenshot: autoScreenshot,
        alarm_cooldown: alarmCooldown,
      });
      showMessage('success', '设置保存成功！');
      console.log('AI 设置已保存');
    } catch (error: any) {
      console.error('保存设置失败:', error);
      showMessage('error', error.message || '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  const [aiStats] = useState({
    totalDetections: 1247,
    personDetections: 823,
    vehicleDetections: 312,
    alerts: 112,
    accuracy: 94.5
  });

  if (isLoadingSettings) {
    return (
      <div className="h-full bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">加载中...</div>
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
            <Brain className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">AI识别设置</h2>
            {/* AI 开启/关闭按钮 */}
            <div className="flex items-center gap-2 ml-4 px-3 py-1.5 bg-slate-800 rounded-lg border border-slate-600">
              <Power className={`size-4 ${enabled ? 'text-green-500' : 'text-slate-500'}`} />
              <span className={`text-sm ${enabled ? 'text-green-500' : 'text-slate-400'}`}>
                {enabled ? '已开启' : '已关闭'}
              </span>
              <Switch checked={enabled} onCheckedChange={setEnabled} />
            </div>
          </div>
          
          {/* 保存消息 */}
          {saveMessage && (
            <div className={`px-4 py-2 rounded-lg text-sm ${
              saveMessage.type === 'success' 
                ? 'bg-green-600 text-white' 
                : 'bg-red-600 text-white'
            }`}>
              {saveMessage.text}
            </div>
          )}
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        {/* AI统计信息 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">总检测数</div>
            <div className="text-slate-100 text-2xl">{aiStats.totalDetections}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">人员检测</div>
            <div className="text-green-500 text-2xl">{aiStats.personDetections}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">车辆检测</div>
            <div className="text-blue-500 text-2xl">{aiStats.vehicleDetections}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">报警次数</div>
            <div className="text-red-500 text-2xl">{aiStats.alerts}</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">准确率</div>
            <div className="text-cyan-500 text-2xl">{aiStats.accuracy}%</div>
          </div>
        </div>

        {/* 绑定识别摄像头 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4 flex items-center gap-2">
            <Camera className="size-5 text-cyan-500" />
            绑定识别摄像头
          </h3>
          <div className="space-y-4">
            <div>
              <label className="text-slate-300 text-sm mb-2 block">选择摄像头</label>
              <div className="relative">
                <button
                  onClick={() => setShowCameraDropdown(!showCameraDropdown)}
                  disabled={isLoadingCameras}
                  className="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg text-left text-slate-200 hover:border-cyan-500 transition-colors flex items-center justify-between disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="flex items-center gap-2">
                    <Camera className="size-4 text-cyan-500" />
                    {isLoadingCameras ? (
                      '加载中...'
                    ) : selectedCameraId ? (
                      cameras.find((c: CameraType) => c.id === selectedCameraId)?.name || '请选择摄像头'
                    ) : (
                      '请选择摄像头'
                    )}
                  </span>
                  <ChevronDown className={`size-4 text-slate-400 transition-transform ${showCameraDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showCameraDropdown && (
                  <div className="absolute z-10 w-full mt-2 bg-slate-900 border border-slate-600 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                    {cameras.length === 0 ? (
                      <div className="px-4 py-3 text-slate-400 text-sm text-center">
                        暂无可用摄像头
                      </div>
                    ) : (
                      cameras.map((camera: CameraType) => (
                        <button
                          key={camera.id}
                          onClick={() => {
                            setSelectedCameraId(camera.id);
                            setShowCameraDropdown(false);
                          }}
                          className={`w-full px-4 py-3 text-left hover:bg-slate-800 transition-colors flex items-center justify-between ${
                            selectedCameraId === camera.id ? 'bg-slate-800 text-cyan-500' : 'text-slate-200'
                          }`}
                        >
                          <span className="flex items-center gap-2">
                            <Camera className="size-4" />
                            <div>
                              <div className="font-medium">{camera.name}</div>
                              <div className="text-xs text-slate-400">{camera.address}</div>
                            </div>
                          </span>
                          {camera.status === 'online' && (
                            <span className="text-xs px-2 py-1 bg-green-600 text-white rounded">在线</span>
                          )}
                          {camera.status === 'offline' && (
                            <span className="text-xs px-2 py-1 bg-red-600 text-white rounded">离线</span>
                          )}
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
              <p className="text-slate-500 text-xs mt-2">
                选择用于AI识别的摄像头。只有在线的摄像头才能进行AI识别。
              </p>
            </div>

            {selectedCameraId && (
              <div className="bg-slate-900 border border-slate-600 rounded-lg p-4">
                <div className="text-slate-300 text-sm mb-2">当前绑定摄像头信息</div>
                {(() => {
                  const selectedCamera = cameras.find((c: CameraType) => c.id === selectedCameraId);
                  if (!selectedCamera) return null;
                  return (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">名称:</span>
                        <span className="text-slate-200">{selectedCamera.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">地址:</span>
                        <span className="text-slate-200">{selectedCamera.address}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">分辨率:</span>
                        <span className="text-slate-200">{selectedCamera.resolution}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">帧率:</span>
                        <span className="text-slate-200">{selectedCamera.fps} FPS</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">状态:</span>
                        <span className={selectedCamera.status === 'online' ? 'text-green-500' : 'text-red-500'}>
                          {selectedCamera.status === 'online' ? '在线' : '离线'}
                        </span>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}
          </div>
        </div>

        {/* 检测参数 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">检测参数</h3>
          <div className="space-y-6">
            {/* 置信度阈值 */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-slate-300 text-sm">置信度阈值</label>
                <span className="text-slate-400 text-sm">{confidence}%</span>
              </div>
              <Slider
                value={[confidence]}
                onValueChange={(value: number[]) => setConfidence(value[0])}
                max={100}
                step={1}
                className="w-full"
              />
              <p className="text-slate-500 text-xs mt-2">
                低于此值的检测结果将被忽略。提高阈值可减少误报，但可能遗漏目标。
              </p>
            </div>
          </div>
        </div>

        {/* 区域管理 */}
        {selectedCameraId && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h3 className="text-slate-100 mb-4 flex items-center gap-2">
              <Camera className="size-5 text-cyan-500" />
              警报区域设置
            </h3>
            <div className="text-slate-400 text-sm mb-4">
              在摄像头画面上绘制警告区域和报警区域，AI检测到目标进入这些区域时会触发相应级别的警报。
            </div>
            <ZoneManagement cameraId={selectedCameraId} />
          </div>
        )}

        {/* 报警设置 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4 flex items-center gap-2">
            <AlertTriangle className="size-5 text-yellow-500" />
            报警设置
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-slate-200">声音报警</div>
                <div className="text-slate-400 text-sm">检测到入侵时播放警报声</div>
              </div>
              <Switch checked={soundAlarm} onCheckedChange={setSoundAlarm} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-slate-200">视觉报警</div>
                <div className="text-slate-400 text-sm">屏幕闪烁提示</div>
              </div>
              <Switch checked={visualAlarm} onCheckedChange={setVisualAlarm} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-slate-200">自动截图</div>
                <div className="text-slate-400 text-sm">报警时自动保存截图</div>
              </div>
              <Switch checked={autoScreenshot} onCheckedChange={setAutoScreenshot} />
            </div>
            <div>
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-slate-200">报警冷却时间</div>
                  <div className="text-slate-400 text-sm">避免重复报警</div>
                </div>
                <span className="text-slate-400 text-sm">{alarmCooldown}秒</span>
              </div>
              <Slider
                value={[alarmCooldown]}
                onValueChange={(value: number[]) => setAlarmCooldown(value[0])}
                min={0}
                max={60}
                step={1}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* AI模型信息 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">AI模型信息</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">模型版本:</span>
              <span className="text-slate-200">YOLOv8-Industrial v2.3</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">支持类别:</span>
              <span className="text-slate-200">15类</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">推理速度:</span>
              <span className="text-green-500">33ms (30 FPS)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">GPU加速:</span>
              <span className="text-green-500">已启用</span>
            </div>
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onBack}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
            disabled={isSaving}
          >
            取消
          </button>
          <button 
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <div className="size-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                保存中...
              </>
            ) : (
              <>
                <CheckCircle2 className="size-4" />
                保存设置
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
