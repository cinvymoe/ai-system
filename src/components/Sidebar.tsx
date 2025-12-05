import { X, Info, Camera, Compass, Brain, FileText, UserCog, LogOut, Zap, Server, Gauge } from 'lucide-react';
import { SettingsView, UserRole } from '../App';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentView: SettingsView;
  onViewChange: (view: SettingsView) => void;
  isInSettings: boolean;
  userRole: UserRole;
  onLogout: () => void;
}

export function Sidebar({ isOpen, onClose, currentView, onViewChange, isInSettings, userRole, onLogout }: SidebarProps) {
  // 根据用户角色过滤菜单项
  const allMenuItems = [
    { id: 'camera-list' as SettingsView, label: '摄像头列表', icon: Camera, adminOnly: true },
    { id: 'direction-cameras' as SettingsView, label: '方向摄像头', icon: Compass, adminOnly: true },
    { id: 'angle-range' as SettingsView, label: '角度设置', icon: Gauge, adminOnly: true },
    { id: 'sensor' as SettingsView, label: '传感器设置', icon: Compass, adminOnly: true },
    { id: 'ai' as SettingsView, label: 'AI识别设置', icon: Brain, adminOnly: true },
    { id: 'alarm-log' as SettingsView, label: '报警日志', icon: FileText, adminOnly: true },
    { id: 'admin-management' as SettingsView, label: '管理员管理', icon: UserCog, adminOnly: true },
    { id: 'ipc-test' as SettingsView, label: 'IPC 通信测试', icon: Zap, adminOnly: false },
    { id: 'backend-test' as SettingsView, label: 'Python 后端测试', icon: Server, adminOnly: false },
    { id: 'about' as SettingsView, label: '关于', icon: Info, adminOnly: false },
  ];
  
  const menuItems = userRole === 'admin' 
    ? allMenuItems 
    : allMenuItems.filter(item => !item.adminOnly);

  return (
    <>
      {/* 遮罩层 - 仅在主界面时显示 */}
      {isOpen && currentView === 'main' && (
        <div 
          className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10"
          onClick={onClose}
        />
      )}

      {/* 侧边栏 - 在设置界面时作为固定侧栏，不使用absolute */}
      <div 
        className={`h-full w-80 bg-gradient-to-b from-slate-950 to-slate-900 border-r-2 border-cyan-500/30 flex flex-col shadow-2xl transition-all duration-300 ${
          isInSettings 
            ? (isOpen ? 'relative' : 'absolute -translate-x-full') 
            : `absolute left-0 z-20 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`
        }`}
      >
        {/* 侧边栏标题 */}
        <div className="border-b-2 border-cyan-500/30 px-6 py-4 flex items-center justify-between shrink-0 bg-slate-950/50">
          <h2 className="text-cyan-400 tracking-wide">系统设置</h2>
          {currentView === 'main' && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-cyan-600/20 rounded-lg transition-all border border-transparent hover:border-cyan-500/50"
            >
              <X className="size-5 text-cyan-400" />
            </button>
          )}
        </div>

        {/* 菜单列表 */}
        <div className="flex-1 overflow-y-auto p-4">
          <nav className="space-y-3">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => onViewChange(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                    isActive 
                      ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white shadow-lg shadow-cyan-500/30 border border-cyan-400/50' 
                      : 'text-slate-300 hover:bg-slate-800/70 border border-transparent hover:border-slate-700'
                  }`}
                >
                  <Icon className={`size-5 ${isActive ? 'animate-pulse' : ''}`} />
                  <span className="tracking-wide">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* 底部信息 */}
        <div className="border-t-2 border-cyan-500/30 p-4 shrink-0 bg-slate-950/50">
          {userRole && (
            <div className="mb-4">
              <button
                onClick={onLogout}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-all border border-red-500/30 hover:border-red-500/50"
              >
                <LogOut className="size-4" />
                <span>退出登录</span>
              </button>
              <div className="text-xs text-slate-500 text-center mt-2">
                当前身份: {userRole === 'admin' ? '管理员' : '普通用户'}
              </div>
            </div>
          )}
          <div className="text-slate-400 text-sm space-y-2">
            <div className="flex justify-between">
              <span>版本:</span>
              <span className="text-cyan-400">v2.1.0</span>
            </div>
            <div className="flex justify-between">
              <span>设备:</span>
              <span className="text-cyan-400">Linux 平板</span>
            </div>
            <div className="flex items-center justify-center gap-2 mt-3 pt-3 border-t border-slate-700">
              <div className="size-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
              <span className="text-green-500 font-mono">系统运行中</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}