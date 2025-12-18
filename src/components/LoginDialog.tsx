import { X, Lock, User } from 'lucide-react';
import { useState, useCallback, useMemo, useRef } from 'react';

interface LoginDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (username: string, password: string) => boolean;
}

export function LoginDialog({ isOpen, onClose, onLogin }: LoginDialogProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  // 使用 ref 来避免不必要的重新渲染
  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  // 使用 useCallback 优化事件处理函数
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    const success = onLogin(username, password);
    if (success) {
      setUsername('');
      setPassword('');
      onClose();
    } else {
      setError('用户名或密码错误');
    }
  }, [username, password, onLogin, onClose]);

  const handleClose = useCallback(() => {
    setUsername('');
    setPassword('');
    setError('');
    onClose();
  }, [onClose]);

  // 优化输入处理函数
  const handleUsernameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
  }, []);

  const handlePasswordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
  }, []);

  // 使用 useMemo 缓存样式类名
  const inputClassName = useMemo(() => 
    "w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors",
    []
  );

  // 缓存按钮样式
  const buttonStyles = useMemo(() => ({
    cancel: "flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors",
    submit: "flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
  }), []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-cyan-500/50 rounded-lg shadow-xl w-full max-w-md">
        {/* 标题栏 */}
        <div className="border-b border-slate-700 px-6 py-4 flex items-center justify-between bg-slate-800">
          <div className="flex items-center gap-3">
            <Lock className="size-5 text-cyan-500" />
            <h2 className="text-cyan-400 tracking-wide">管理员登录</h2>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="size-5 text-slate-400" />
          </button>
        </div>

        {/* 表单内容 */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* 用户名 */}
          <div>
            <label className="block text-slate-300 mb-2">用户名</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-500" />
              <input
                ref={usernameRef}
                type="text"
                value={username}
                onChange={handleUsernameChange}
                placeholder="请输入用户名"
                className={inputClassName}
                autoFocus
                autoComplete="username"
              />
            </div>
          </div>

          {/* 密码 */}
          <div>
            <label className="block text-slate-300 mb-2">密码</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-500" />
              <input
                ref={passwordRef}
                type="password"
                value={password}
                onChange={handlePasswordChange}
                placeholder="请输入密码"
                className={inputClassName}
                autoComplete="current-password"
              />
            </div>
          </div>

          {/* 提示信息 */}
          <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-3 text-cyan-300 text-sm">
            <p>默认管理员账号: admin / admin123</p>
            <p className="mt-1 text-xs text-slate-400">普通用户无需登录，可直接查看关于界面</p>
          </div>

          {/* 按钮组 */}
          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className={buttonStyles.cancel}
            >
              取消
            </button>
            <button
              type="submit"
              className={buttonStyles.submit}
            >
              登录
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
