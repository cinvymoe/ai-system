import { ArrowLeft, FileText, Camera, AlertTriangle, Brain, Download, Filter, Search, X, Calendar } from 'lucide-react';
import { useState } from 'react';

interface AlarmLogSettingsProps {
  onBack: () => void;
  logs: {
    operation: OperationLog[];
    cameraOffline: CameraOfflineLog[];
    aiDetection: AIDetectionLog[];
  };
}

export interface OperationLog {
  id: string;
  timestamp: Date;
  type: 'add' | 'delete' | 'edit' | 'config';
  operator: string;
  target: string;
  description: string;
}

export interface CameraOfflineLog {
  id: string;
  timestamp: Date;
  cameraId: string;
  cameraName: string;
  location: string;
  duration: number; // 离线时长（分钟）
  status: 'offline' | 'recovered';
}

export interface AIDetectionLog {
  id: string;
  timestamp: Date;
  cameraId: string;
  cameraName: string;
  detectionType: 'person' | 'vehicle' | 'danger-zone';
  confidence: number;
  location: string;
  handled: boolean;
}

type TabType = 'operation' | 'offline' | 'ai';

const tabConfig = {
  operation: { label: '操作日志', icon: FileText, color: 'cyan' },
  offline: { label: '摄像头离线', icon: Camera, color: 'red' },
  ai: { label: 'AI识别报警', icon: Brain, color: 'amber' }
};

export function AlarmLogSettings({ onBack, logs }: AlarmLogSettingsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('operation');
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleExport = () => {
    alert('导出日志功能开发中...\n\n将导出为CSV或Excel格式');
  };

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).format(date);
  };

  const isDateInRange = (timestamp: Date) => {
    if (!startDate && !endDate) return true;
    
    const logDate = new Date(timestamp.getFullYear(), timestamp.getMonth(), timestamp.getDate());
    
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      return logDate >= start && logDate <= end;
    }
    
    if (startDate) {
      const start = new Date(startDate);
      return logDate >= start;
    }
    
    if (endDate) {
      const end = new Date(endDate);
      return logDate <= end;
    }
    
    return true;
  };

  const filteredOperationLogs = logs.operation.filter(log =>
    isDateInRange(log.timestamp) && (
      searchQuery === '' ||
      log.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.target.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.operator.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const filteredOfflineLogs = logs.cameraOffline.filter(log =>
    isDateInRange(log.timestamp) && (
      searchQuery === '' ||
      log.cameraName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.location.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const filteredAILogs = logs.aiDetection.filter(log =>
    isDateInRange(log.timestamp) && (
      searchQuery === '' ||
      log.cameraName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.location.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

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
            <FileText className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">报警日志</h2>
          </div>
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/30 border border-cyan-400/50"
          >
            <Download className="size-4" />
            导出日志
          </button>
        </div>

        {/* 标签页 */}
        <div className="flex items-center gap-2 mt-4">
          {(Object.keys(tabConfig) as TabType[]).map((tab) => {
            const config = tabConfig[tab];
            const Icon = config.icon;
            const isActive = activeTab === tab;
            
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
                  isActive
                    ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/30'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                <Icon className="size-4" />
                <span>{config.label}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-mono ${
                  isActive ? 'bg-cyan-700' : 'bg-slate-700'
                }`}>
                  {tab === 'operation' && logs.operation.length}
                  {tab === 'offline' && logs.cameraOffline.length}
                  {tab === 'ai' && logs.aiDetection.length}
                </span>
              </button>
            );
          })}
        </div>

        {/* 搜索栏 */}
        <div className="mt-4 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索日志..."
            className="w-full pl-10 pr-10 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-700 rounded transition-colors"
            >
              <X className="size-4 text-slate-400" />
            </button>
          )}
        </div>

        {/* 日期筛选 */}
        <div className="mt-4 flex items-center gap-4">
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-500" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder="开始日期"
              className="w-full pl-10 pr-10 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-500" />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder="结束日期"
              className="w-full pl-10 pr-10 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="p-6">
        {/* 操作日志 */}
        {activeTab === 'operation' && (
          <div className="space-y-3">
            {filteredOperationLogs.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <FileText className="size-16 mx-auto mb-4 opacity-30" />
                <p>暂无操���日志</p>
              </div>
            ) : (
              filteredOperationLogs.map((log) => (
                <div key={log.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:bg-slate-750 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-cyan-600/20 rounded-lg">
                      <FileText className="size-5 text-cyan-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-slate-100 font-mono">{log.description}</span>
                        <span className="px-2 py-0.5 bg-slate-700 text-slate-400 text-xs rounded">
                          {log.type === 'add' && '新增'}
                          {log.type === 'delete' && '删除'}
                          {log.type === 'edit' && '编辑'}
                          {log.type === 'config' && '配置'}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span>操作员: {log.operator}</span>
                        <span>目标: {log.target}</span>
                        <span className="font-mono">{formatTimestamp(log.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* 摄像头离线日志 */}
        {activeTab === 'offline' && (
          <div className="space-y-3">
            {filteredOfflineLogs.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Camera className="size-16 mx-auto mb-4 opacity-30" />
                <p>暂无离线报警</p>
              </div>
            ) : (
              filteredOfflineLogs.map((log) => (
                <div key={log.id} className="bg-slate-800 border border-red-900/50 rounded-lg p-4 hover:bg-slate-750 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-lg ${
                      log.status === 'offline' ? 'bg-red-600/20' : 'bg-green-600/20'
                    }`}>
                      <Camera className={`size-5 ${
                        log.status === 'offline' ? 'text-red-500' : 'text-green-500'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-slate-100 font-mono">{log.cameraName}</span>
                        <span className={`px-2 py-0.5 text-xs rounded ${
                          log.status === 'offline' 
                            ? 'bg-red-600/20 text-red-400 border border-red-500/30' 
                            : 'bg-green-600/20 text-green-400 border border-green-500/30'
                        }`}>
                          {log.status === 'offline' ? '离线' : '已恢复'}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span>位置: {log.location}</span>
                        <span>离线时长: {log.duration} 分钟</span>
                        <span className="font-mono">{formatTimestamp(log.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* AI识别报警日志 */}
        {activeTab === 'ai' && (
          <div className="space-y-3">
            {filteredAILogs.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Brain className="size-16 mx-auto mb-4 opacity-30" />
                <p>暂无AI识别报警</p>
              </div>
            ) : (
              filteredAILogs.map((log) => (
                <div key={log.id} className="bg-slate-800 border border-amber-900/50 rounded-lg p-4 hover:bg-slate-750 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-amber-600/20 rounded-lg">
                      <AlertTriangle className="size-5 text-amber-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-slate-100 font-mono">{log.cameraName}</span>
                        <span className="px-2 py-0.5 bg-amber-600/20 text-amber-400 text-xs rounded border border-amber-500/30">
                          {log.detectionType === 'person' && '人员入侵'}
                          {log.detectionType === 'vehicle' && '车辆异常'}
                          {log.detectionType === 'danger-zone' && '危险区域'}
                        </span>
                        {log.handled && (
                          <span className="px-2 py-0.5 bg-green-600/20 text-green-400 text-xs rounded border border-green-500/30">
                            已处理
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-400 mb-2">
                        <span>摄像头: {log.cameraName}</span>
                        <span>位置: {log.location}</span>
                        <span>置信度: {(log.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="text-xs text-slate-500 font-mono">
                        {formatTimestamp(log.timestamp)}
                      </div>
                    </div>
                    {!log.handled && (
                      <button
                        onClick={() => alert(`标记报警 ${log.id} 为已处理`)}
                        className="px-3 py-1 bg-cyan-600 hover:bg-cyan-700 text-white text-sm rounded-lg transition-colors"
                      >
                        标记处理
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}