import { AlertTriangle, UserX, Target, X } from 'lucide-react';
import { Alert } from '../App';
import { useEffect, useState } from 'react';

interface AlertPanelProps {
  alerts: Alert[];
  onClearAlert: (id: string) => void;
}

interface AlertWithTimer extends Alert {
  progress: number;
}

export function AlertPanel({ alerts, onClearAlert }: AlertPanelProps) {
  const [alertsWithTimers, setAlertsWithTimers] = useState<AlertWithTimer[]>([]);

  // 自动关闭延时（5秒）
  const AUTO_CLOSE_DURATION = 5000;

  useEffect(() => {
    // 将新的alerts添加进度条
    const newAlertsWithTimers = alerts.map(alert => ({
      ...alert,
      progress: 100
    }));
    setAlertsWithTimers(newAlertsWithTimers);

    // 为每个alert设置定时器
    const timers = alerts.map((alert, index) => {
      const startTime = Date.now();
      
      const interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, 100 - (elapsed / AUTO_CLOSE_DURATION) * 100);
        
        setAlertsWithTimers(prev => 
          prev.map(a => a.id === alert.id ? { ...a, progress: remaining } : a)
        );

        if (remaining <= 0) {
          clearInterval(interval);
          setTimeout(() => onClearAlert(alert.id), 300);
        }
      }, 16); // 60fps

      return interval;
    });

    return () => timers.forEach(clearInterval);
  }, [alerts.length]);

  if (alertsWithTimers.length === 0) return null;

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'intrusion':
        return <UserX className="size-6 text-red-400" />;
      case 'tracking':
        return <Target className="size-6 text-yellow-400" />;
      default:
        return <AlertTriangle className="size-6 text-orange-400" />;
    }
  };

  const getAlertColor = (type: Alert['type']) => {
    switch (type) {
      case 'intrusion':
        return {
          border: 'border-red-500/50',
          bg: 'bg-slate-800',
          shadow: 'shadow-lg',
          progress: 'bg-red-500'
        };
      case 'tracking':
        return {
          border: 'border-cyan-500/50',
          bg: 'bg-slate-800',
          shadow: 'shadow-lg',
          progress: 'bg-cyan-500'
        };
      default:
        return {
          border: 'border-slate-500/50',
          bg: 'bg-slate-800',
          shadow: 'shadow-lg',
          progress: 'bg-slate-500'
        };
    }
  };

  const getAlertTitle = (type: Alert['type']) => {
    switch (type) {
      case 'intrusion':
        return '⚠️ 入侵警报';
      case 'tracking':
        return '🎯 目标追踪';
      default:
        return '⚡ 系统提示';
    }
  };

  return (
    <div className="absolute top-4 right-4 w-96 space-y-3 z-30 max-h-[calc(100vh-120px)] overflow-y-auto">
      {alertsWithTimers.map((alert) => {
        const colors = getAlertColor(alert.type);
        
        return (
          <div
            key={alert.id}
            className={`border-2 backdrop-blur-md rounded-lg overflow-hidden animate-in slide-in-from-right ${colors.border} ${colors.bg} ${colors.shadow}`}
          >
            {/* 顶部进度条 */}
            <div className="h-1 bg-slate-800/50 relative overflow-hidden">
              <div 
                className={`h-full transition-all duration-100 ease-linear ${colors.progress}`}
                style={{ width: `${alert.progress}%` }}
              />
            </div>

            {/* 内容区 */}
            <div className="p-4 flex items-start gap-3">
              <div className="shrink-0 mt-1 animate-pulse">
                {getAlertIcon(alert.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-slate-100 font-semibold mb-1">
                  {getAlertTitle(alert.type)}
                </div>
                <div className="text-slate-200 text-sm mb-2">{alert.message}</div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-mono">
                    {alert.timestamp.toLocaleTimeString('zh-CN', { hour12: false })}
                  </span>
                  <span className="text-slate-500">
                    {Math.ceil((alert.progress / 100) * (AUTO_CLOSE_DURATION / 1000))}秒后关闭
                  </span>
                </div>
              </div>
              <button
                onClick={() => onClearAlert(alert.id)}
                className="shrink-0 p-1.5 hover:bg-slate-800/70 rounded-lg transition-all border border-transparent hover:border-slate-700"
              >
                <X className="size-5 text-slate-400 hover:text-slate-200" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}