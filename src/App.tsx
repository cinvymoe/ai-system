import { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import { MainCamera } from './components/MainCamera';
import { Sidebar } from './components/Sidebar';
import { AlertPanel } from './components/AlertPanel';
import { AboutSettings } from './components/settings/AboutSettings';
import { CameraSettings } from './components/settings/CameraSettings';
import { DirectionCamerasSettings } from './components/settings/DirectionCamerasSettings';
import { SensorSettings } from './components/settings/SensorSettings';
import { AISettings } from './components/settings/AISettings';
import { AddCameraSettings } from './components/settings/AddCameraSettings';
import { CameraListSettings } from './components/settings/CameraListSettings';
import { EditCameraSettings } from './components/settings/EditCameraSettings';
import { AngleRangeSettings } from './components/settings/AngleRangeSettings';
import { AlarmLogSettings, OperationLog, CameraOfflineLog, AIDetectionLog } from './components/settings/AlarmLogSettings';
import { AdminManagement, Admin } from './components/settings/AdminManagement';
import { LoginDialog } from './components/LoginDialog';
import { ElectronIPCTest } from './components/ElectronIPCTest';
import BackendTest from './components/BackendTest';

export type Direction = 'forward' | 'backward' | 'left' | 'right' | 'idle';
export type SettingsView = 'main' | 'about' | 'camera' | 'direction-cameras' | 'angle-range' | 'sensor' | 'ai' | 'add-camera' | 'camera-list' | 'edit-camera' | 'alarm-log' | 'admin-management' | 'ipc-test' | 'backend-test';
export type UserRole = 'admin' | 'user' | null;

export interface Camera {
  id: string;
  name: string;
  url: string;
  enabled: boolean;
  resolution: string;
  fps: number;
  brightness: number;
  contrast: number;
  status: 'online' | 'offline';
}

export interface CameraGroup {
  direction: Direction;
  cameras: Camera[];
}

export interface Alert {
  id: string;
  type: 'intrusion' | 'tracking' | 'system';
  message: string;
  timestamp: Date;
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState<SettingsView>('main');
  const [currentDirection, setCurrentDirection] = useState<Direction>('idle');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [activeCameraId, setActiveCameraId] = useState('camera-forward-1');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [editingCameraId, setEditingCameraId] = useState<string | null>(null);
  const [loginDialogOpen, setLoginDialogOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<UserRole>(null);
  
  // 管理员账号数据
  const [admins, setAdmins] = useState<Admin[]>([
    {
      id: '1',
      username: 'admin',
      password: 'admin123',
      role: 'admin',
      createdAt: new Date('2024-01-01'),
      lastLogin: new Date()
    },
    {
      id: '2',
      username: 'tech01',
      password: 'tech123',
      role: 'user',
      createdAt: new Date('2024-01-15'),
      lastLogin: new Date(Date.now() - 1000 * 60 * 60 * 24)
    }
  ]);
  
  // 日志数据
  const [logs, setLogs] = useState<{
    operation: OperationLog[];
    cameraOffline: CameraOfflineLog[];
    aiDetection: AIDetectionLog[];
  }>({
    operation: [
      {
        id: '1',
        timestamp: new Date(Date.now() - 1000 * 60 * 30),
        type: 'add',
        operator: '管理员',
        target: '前方主摄像头',
        description: '添加新摄像头'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 1000 * 60 * 60),
        type: 'config',
        operator: '技术员01',
        target: '系统配置',
        description: '修改AI识别阈值'
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 1000 * 60 * 120),
        type: 'edit',
        operator: '管理员',
        target: '右侧摄像头',
        description: '更新摄像头参数'
      }
    ],
    cameraOffline: [
      {
        id: '1',
        timestamp: new Date(Date.now() - 1000 * 60 * 15),
        cameraId: 'camera-right-1',
        cameraName: '右侧摄像头',
        location: '右侧监控区',
        duration: 15,
        status: 'offline'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 1000 * 60 * 90),
        cameraId: 'camera-backward-1',
        cameraName: '后方摄像头',
        location: '后方监控区',
        duration: 5,
        status: 'recovered'
      }
    ],
    aiDetection: [
      {
        id: '1',
        timestamp: new Date(Date.now() - 1000 * 60 * 5),
        cameraId: 'camera-forward-1',
        cameraName: '前方主摄像头',
        detectionType: 'person',
        confidence: 0.95,
        location: '前方作业区',
        handled: false
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 1000 * 60 * 20),
        cameraId: 'camera-left-1',
        cameraName: '左侧摄像头',
        detectionType: 'danger-zone',
        confidence: 0.88,
        location: '左侧危险区',
        handled: true
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 1000 * 60 * 45),
        cameraId: 'camera-forward-2',
        cameraName: '前方辅助摄像头',
        detectionType: 'vehicle',
        confidence: 0.92,
        location: '前方作业区',
        handled: true
      }
    ]
  });
  
  // Note: Camera data is now managed by the camera store (useCameraStore)
  // The local cameraGroups state has been removed in favor of centralized state management

  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 模拟9轴传感器数据
  useEffect(() => {
    const directions: Direction[] = ['idle', 'forward', 'backward', 'left', 'right'];
    const interval = setInterval(() => {
      const randomDirection = directions[Math.floor(Math.random() * directions.length)];
      setCurrentDirection(randomDirection);
      
      // Note: Camera switching based on direction is now handled by the camera store
      // The active camera selection logic can be implemented in the MainCamera component
    }, 5000);

    return () => clearInterval(interval);
  }, []);



  const handleViewChange = (view: SettingsView) => {
    setCurrentView(view);
    if (view !== 'main') {
      setSidebarOpen(true);
    }
  };

  const handleBackToMain = () => {
    setCurrentView('main');
    setSidebarOpen(false);
  };

  // Camera operations are now handled by the camera store
  // These handlers have been removed in favor of direct store actions

  // 登录函数
  const handleLogin = (username: string, password: string): boolean => {
    const user = admins.find(a => a.username === username && a.password === password);
    if (user) {
      setCurrentUser(user.role);
      // 更新最后登录时间
      setAdmins(prev => prev.map(a => 
        a.id === user.id ? { ...a, lastLogin: new Date() } : a
      ));
      // 根据用户角色决定显示的界面
      if (user.role === 'admin') {
        setSidebarOpen(true);
        setCurrentView('camera-list'); // 管理员默认进入摄像头列表
      } else {
        setCurrentView('about'); // 普通用户只能看关于界面
        setSidebarOpen(true);
      }
      return true;
    }
    return false;
  };

  // 登出函数
  const handleLogout = () => {
    setCurrentUser(null);
    setCurrentView('main');
    setSidebarOpen(false);
  };

  // 管理员管理相关函数
  const handleAddAdmin = (admin: Omit<Admin, 'id'>) => {
    const newAdmin: Admin = {
      ...admin,
      id: Date.now().toString()
    };
    setAdmins(prev => [...prev, newAdmin]);
  };

  const handleEditAdmin = (id: string, updates: Partial<Admin>) => {
    setAdmins(prev => prev.map(a => a.id === id ? { ...a, ...updates } : a));
  };

  const handleDeleteAdmin = (id: string) => {
    setAdmins(prev => prev.filter(a => a.id !== id));
  };

  // 处理设置按钮点击
  const handleSettingsClick = () => {
    if (currentUser) {
      // 已登录，切换侧边栏
      setSidebarOpen(!sidebarOpen);
    } else {
      // 未登录，显示登录对话框
      setLoginDialogOpen(true);
    }
  };

  const renderContent = () => {
    switch (currentView) {
      case 'about':
        return <AboutSettings onBack={handleBackToMain} />;
      case 'camera':
        return (
          <CameraSettings 
            onBack={handleBackToMain}
            cameraGroups={[]} // TODO: Update CameraSettings to use store
            activeCameraId={activeCameraId}
            setActiveCameraId={setActiveCameraId}
          />
        );
      case 'direction-cameras':
        return <DirectionCamerasSettings onBack={handleBackToMain} />;
      case 'angle-range':
        return <AngleRangeSettings onBack={handleBackToMain} />;
      case 'camera-list':
        return (
          <CameraListSettings
            onBack={handleBackToMain}
            onNavigateToAddCamera={() => setCurrentView('add-camera')}
            onNavigateToEditCamera={(cameraId) => {
              setEditingCameraId(cameraId);
              setCurrentView('edit-camera');
            }}
          />
        );
      case 'add-camera':
        return (
          <AddCameraSettings
            onBack={() => setCurrentView('camera-list')}
          />
        );
      case 'edit-camera':
        return (
          <EditCameraSettings
            onBack={() => setCurrentView('camera-list')}
            editingCameraId={editingCameraId}
            setEditingCameraId={setEditingCameraId}
          />
        );
      case 'sensor':
        return <SensorSettings onBack={handleBackToMain} currentDirection={currentDirection} />;
      case 'ai':
        return <AISettings onBack={handleBackToMain} />;
      case 'alarm-log':
        return <AlarmLogSettings onBack={handleBackToMain} logs={logs} />;
      case 'admin-management':
        return <AdminManagement onBack={handleBackToMain} admins={admins} onAddAdmin={handleAddAdmin} onEditAdmin={handleEditAdmin} onDeleteAdmin={handleDeleteAdmin} />;
      case 'ipc-test':
        return (
          <div className="h-full bg-slate-900 overflow-auto">
            <div className="max-w-4xl mx-auto">
              <div className="sticky top-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700/50 px-6 py-4 z-10">
                <button
                  onClick={handleBackToMain}
                  className="text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  ← 返回主界面
                </button>
              </div>
              <ElectronIPCTest />
            </div>
          </div>
        );
      case 'backend-test':
        return (
          <div className="h-full bg-slate-900 overflow-auto">
            <div className="max-w-4xl mx-auto">
              <div className="sticky top-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700/50 px-6 py-4 z-10">
                <button
                  onClick={handleBackToMain}
                  className="text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  ← 返回主界面
                </button>
              </div>
              <BackendTest />
            </div>
          </div>
        );
      default:
        return <MainCamera 
          direction={currentDirection} 
          activeCameraId={activeCameraId} 
          onAlert={(alert) => {
            const newAlert = {
              id: Date.now().toString(),
              type: alert.type,
              message: alert.message,
              timestamp: new Date()
            };
            setAlerts([newAlert]); // 只保留一个警报
          }}
        />;
    }
  };

  // 判断是否在设置界面
  const isInSettings = currentView !== 'main';

  return (
    <div className="h-screen w-screen bg-slate-900 overflow-hidden flex flex-col">
      {/* 标题栏 */}
      <header className="bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border-b-2 border-cyan-500/30 px-6 py-3 flex items-center justify-between shrink-0 shadow-lg">
        <button
          onClick={handleSettingsClick}
          className="p-2 hover:bg-cyan-600/20 rounded-lg transition-all duration-300 border border-transparent hover:border-cyan-500/50"
        >
          <Settings className={`size-6 text-cyan-400 transition-transform duration-500 ${sidebarOpen ? 'rotate-180' : ''}`} />
        </button>
        
        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-3">
          <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse shadow-lg shadow-cyan-500/50"></div>
          <h1 className="text-slate-100 text-xl tracking-wide font-semibold">起重机视觉安全监控系统</h1>
          <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse shadow-lg shadow-cyan-500/50"></div>
        </div>

        <div className="px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50 backdrop-blur-sm">
          <div className="text-cyan-400 font-mono">
            {currentTime.toLocaleTimeString('zh-CN', { hour12: false })}
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* 侧边栏 - 在设置界面时固定显示，不遮挡内容 */}
        <Sidebar 
          isOpen={sidebarOpen} 
          onClose={() => setSidebarOpen(false)} 
          currentView={currentView}
          onViewChange={handleViewChange}
          isInSettings={isInSettings}
          userRole={currentUser}
          onLogout={handleLogout}
        />

        {/* 内容区域 */}
        <div className={`flex-1 overflow-auto transition-all duration-300 ${
          isInSettings && sidebarOpen ? 'ml-0' : ''
        }`}>
          {renderContent()}
        </div>
      </div>

      {/* 报警面板 */}
      <AlertPanel alerts={alerts} onClearAlert={(id) => setAlerts(prev => prev.filter(a => a.id !== id))} />
      
      {/* 登录对话框 */}
      <LoginDialog 
        isOpen={loginDialogOpen}
        onClose={() => setLoginDialogOpen(false)}
        onLogin={handleLogin}
      />
    </div>
  );
}