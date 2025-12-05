/**
 * Angle Range Settings Component
 * 角度设置页面 - 自定义角度范围并绑定摄像头
 */

import { useEffect, useState } from 'react';
import { ArrowLeft, Plus, Edit2, Trash2, Camera, Gauge, Save, X } from 'lucide-react';
import * as Switch from '@radix-ui/react-switch';
import { useAngleRangeStore } from '../../stores/angleRangeStore';
import { useCameraStore } from '../../stores/cameraStore';
import { AngleRangeCreate, AngleRangeUpdate } from '../../services/angleRangeService';
import { RangeSlider } from '../RangeSlider';

interface AngleRangeSettingsProps {
  onBack: () => void;
}

export function AngleRangeSettings({ onBack }: AngleRangeSettingsProps) {
  const { angleRanges, loading, error, fetchAngleRanges, addAngleRange, updateAngleRange, deleteAngleRange, toggleAngleRangeEnabled } = useAngleRangeStore();
  const { cameras, fetchCameras } = useCameraStore();
  
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    min_angle: 0,
    max_angle: 90,
    enabled: true,
    camera_ids: [] as string[],
  });

  useEffect(() => {
    fetchAngleRanges();
    fetchCameras();
  }, [fetchAngleRanges, fetchCameras]);

  const handleCreate = async () => {
    try {
      const data: AngleRangeCreate = {
        name: formData.name,
        min_angle: formData.min_angle,
        max_angle: formData.max_angle,
        enabled: formData.enabled,
        camera_ids: formData.camera_ids,
      };
      await addAngleRange(data);
      setIsCreating(false);
      setFormData({ name: '', min_angle: 0, max_angle: 90, enabled: true, camera_ids: [] });
    } catch (error) {
      console.error('Failed to create angle range:', error);
    }
  };

  const handleUpdate = async (id: string) => {
    try {
      const data: AngleRangeUpdate = {
        name: formData.name,
        min_angle: formData.min_angle,
        max_angle: formData.max_angle,
        enabled: formData.enabled,
        camera_ids: formData.camera_ids,
      };
      await updateAngleRange(id, data);
      setEditingId(null);
      setFormData({ name: '', min_angle: 0, max_angle: 90, enabled: true, camera_ids: [] });
    } catch (error) {
      console.error('Failed to update angle range:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('确定要删除这个角度范围吗？')) {
      try {
        await deleteAngleRange(id);
      } catch (error) {
        console.error('Failed to delete angle range:', error);
      }
    }
  };

  const startEdit = (angleRange: any) => {
    setEditingId(angleRange.id);
    setFormData({
      name: angleRange.name,
      min_angle: angleRange.min_angle,
      max_angle: angleRange.max_angle,
      enabled: angleRange.enabled ?? true,
      camera_ids: angleRange.camera_ids || [],
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setIsCreating(false);
    setFormData({ name: '', min_angle: 0, max_angle: 90, enabled: true, camera_ids: [] });
  };

  const toggleCamera = (cameraId: string) => {
    setFormData(prev => ({
      ...prev,
      camera_ids: prev.camera_ids.includes(cameraId)
        ? prev.camera_ids.filter(id => id !== cameraId)
        : [...prev.camera_ids, cameraId],
    }));
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
            <Gauge className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">角度设置</h2>
          </div>
          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
          >
            <Plus className="size-4" />
            <span>新增角度范围</span>
          </button>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* 创建表单 */}
        {isCreating && (
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">新增角度范围</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">名称</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如：30-90度"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">角度范围</label>
                <RangeSlider
                  min={0}
                  max={360}
                  minValue={formData.min_angle}
                  maxValue={formData.max_angle}
                  onChange={(min, max) => setFormData({ ...formData, min_angle: min, max_angle: max })}
                  step={1}
                  unit="°"
                />
              </div>
              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                    className="w-5 h-5 rounded border-slate-600 text-cyan-600 focus:ring-cyan-500"
                  />
                  <span className="text-sm font-medium text-slate-300">启用此角度范围</span>
                </label>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">绑定摄像头</label>
                <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto p-2 bg-slate-900 rounded-lg border border-slate-700">
                  {cameras.map((camera) => (
                    <label
                      key={camera.id}
                      className="flex items-center gap-2 p-2 hover:bg-slate-800 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={formData.camera_ids.includes(camera.id)}
                        onChange={() => toggleCamera(camera.id)}
                        className="rounded border-slate-600 text-cyan-600 focus:ring-cyan-500"
                      />
                      <span className="text-sm text-slate-300">{camera.name}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleCreate}
                  className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
                >
                  <Save className="size-4" />
                  <span>保存</span>
                </button>
                <button
                  onClick={cancelEdit}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
                >
                  <X className="size-4" />
                  <span>取消</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 角度范围列表 */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
            <p className="text-slate-400 mt-4">加载中...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400">{error}</p>
          </div>
        ) : angleRanges.length === 0 && !isCreating ? (
          <div className="text-center py-12">
            <Gauge className="size-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">暂无角度范围配置</p>
          </div>
        ) : (
          <div className="space-y-4">
            {angleRanges.map((angleRange) => (
              <div
                key={angleRange.id}
                className="bg-slate-800 border border-slate-700 rounded-xl p-6"
              >
                {editingId === angleRange.id ? (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-100">编辑角度范围</h3>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">名称</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-3">角度范围</label>
                      <RangeSlider
                        min={0}
                        max={360}
                        minValue={formData.min_angle}
                        maxValue={formData.max_angle}
                        onChange={(min, max) => setFormData({ ...formData, min_angle: min, max_angle: max })}
                        step={1}
                        unit="°"
                      />
                    </div>
                    <div>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.enabled}
                          onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                          className="w-5 h-5 rounded border-slate-600 text-cyan-600 focus:ring-cyan-500"
                        />
                        <span className="text-sm font-medium text-slate-300">启用此角度范围</span>
                      </label>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">绑定摄像头</label>
                      <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto p-2 bg-slate-900 rounded-lg border border-slate-700">
                        {cameras.map((camera) => (
                          <label
                            key={camera.id}
                            className="flex items-center gap-2 p-2 hover:bg-slate-800 rounded cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={formData.camera_ids.includes(camera.id)}
                              onChange={() => toggleCamera(camera.id)}
                              className="rounded border-slate-600 text-cyan-600 focus:ring-cyan-500"
                            />
                            <span className="text-sm text-slate-300">{camera.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleUpdate(angleRange.id)}
                        className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
                      >
                        <Save className="size-4" />
                        <span>保存</span>
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
                      >
                        <X className="size-4" />
                        <span>取消</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <Gauge className="size-6 text-cyan-500" />
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-semibold text-slate-100">{angleRange.name}</h3>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                              angleRange.enabled 
                                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                                : 'bg-slate-700/50 text-slate-400 border border-slate-600/30'
                            }`}>
                              {angleRange.enabled ? '已启用' : '已禁用'}
                            </span>
                          </div>
                          <p className="text-sm text-slate-400">
                            {angleRange.min_angle}° - {angleRange.max_angle}°
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Toggle Switch */}
                        <Switch.Root
                          checked={angleRange.enabled}
                          onCheckedChange={() => toggleAngleRangeEnabled(angleRange.id)}
                          style={{
                            width: '44px',
                            height: '24px',
                            backgroundColor: angleRange.enabled ? '#06b6d4' : '#475569',
                            borderRadius: '9999px',
                            position: 'relative',
                            cursor: 'pointer',
                            transition: 'background-color 0.2s'
                          }}
                        >
                          <Switch.Thumb 
                            style={{
                              display: 'block',
                              width: '20px',
                              height: '20px',
                              backgroundColor: 'white',
                              borderRadius: '9999px',
                              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                              transition: 'transform 0.2s',
                              transform: angleRange.enabled ? 'translateX(20px)' : 'translateX(2px)',
                              marginTop: '2px'
                            }}
                          />
                        </Switch.Root>
                        <button
                          onClick={() => startEdit(angleRange)}
                          className="p-1.5 hover:bg-slate-700 rounded-lg transition-colors"
                        >
                          <Edit2 className="size-4 text-slate-400" />
                        </button>
                        <button
                          onClick={() => handleDelete(angleRange.id)}
                          className="p-1.5 hover:bg-slate-700 rounded-lg transition-colors"
                        >
                          <Trash2 className="size-4 text-red-400" />
                        </button>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Camera className="size-4 text-slate-400" />
                        <span className="text-sm text-slate-400">
                          绑定摄像头 ({angleRange.camera_ids.length})
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {angleRange.camera_ids.map((cameraId) => {
                          const camera = cameras.find(c => c.id === cameraId);
                          return camera ? (
                            <span
                              key={cameraId}
                              className="px-3 py-1 bg-slate-700 text-slate-300 rounded-lg text-sm"
                            >
                              {camera.name}
                            </span>
                          ) : null;
                        })}
                        {angleRange.camera_ids.length === 0 && (
                          <span className="text-sm text-slate-500">未绑定摄像头</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
