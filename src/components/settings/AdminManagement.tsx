import { ArrowLeft, UserCog, Plus, Trash2, Edit, Shield, User } from 'lucide-react';
import { useState } from 'react';

interface AdminManagementProps {
  onBack: () => void;
  admins: Admin[];
  onAddAdmin: (admin: Omit<Admin, 'id'>) => void;
  onEditAdmin: (id: string, updates: Partial<Admin>) => void;
  onDeleteAdmin: (id: string) => void;
}

export interface Admin {
  id: string;
  username: string;
  password: string;
  role: 'admin' | 'user';
  createdAt: Date;
  lastLogin?: Date;
}

export function AdminManagement({ onBack, admins, onAddAdmin, onEditAdmin, onDeleteAdmin }: AdminManagementProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'user' as 'admin' | 'user'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      alert('请填写完整信息');
      return;
    }

    if (editingId) {
      onEditAdmin(editingId, formData);
      setEditingId(null);
    } else {
      onAddAdmin({
        ...formData,
        createdAt: new Date()
      });
    }

    setFormData({ username: '', password: '', role: 'user' });
    setShowAddForm(false);
  };

  const handleEdit = (admin: Admin) => {
    setFormData({
      username: admin.username,
      password: admin.password,
      role: admin.role
    });
    setEditingId(admin.id);
    setShowAddForm(true);
  };

  const handleCancel = () => {
    setFormData({ username: '', password: '', role: 'user' });
    setEditingId(null);
    setShowAddForm(false);
  };

  const handleDelete = (admin: Admin) => {
    if (admin.username === 'admin') {
      alert('不能删除默认管理员账号');
      return;
    }
    if (confirm(`确定要删除用户"${admin.username}"吗？`)) {
      onDeleteAdmin(admin.id);
    }
  };

  const formatDate = (date?: Date) => {
    if (!date) return '从未登录';
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(date);
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
            <UserCog className="size-5 text-cyan-500" />
            <h2 className="text-slate-100">管理员管理</h2>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/30 border border-cyan-400/50"
          >
            <Plus className="size-4" />
            添加账号
          </button>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        {/* 添加/编辑表单 */}
        {showAddForm && (
          <div className="bg-slate-800 border border-cyan-500/30 rounded-lg p-6 shadow-lg shadow-cyan-500/10">
            <h3 className="text-cyan-400 mb-4 tracking-wide">
              {editingId ? '编辑账号' : '添加新账号'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 用户名 */}
              <div>
                <label className="block text-slate-300 mb-2">用户名</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="请输入用户名"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                />
              </div>

              {/* 密码 */}
              <div>
                <label className="block text-slate-300 mb-2">密码</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="请输入密码"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                />
              </div>

              {/* 角色 */}
              <div>
                <label className="block text-slate-300 mb-2">角色</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, role: 'admin' })}
                    className={`px-4 py-3 rounded-lg border-2 transition-all flex items-center gap-2 ${
                      formData.role === 'admin'
                        ? 'bg-cyan-600 border-cyan-400 text-white shadow-lg shadow-cyan-500/30'
                        : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    <Shield className="size-4" />
                    <span>管理员</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, role: 'user' })}
                    className={`px-4 py-3 rounded-lg border-2 transition-all flex items-center gap-2 ${
                      formData.role === 'user'
                        ? 'bg-cyan-600 border-cyan-400 text-white shadow-lg shadow-cyan-500/30'
                        : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    <User className="size-4" />
                    <span>普通用户</span>
                  </button>
                </div>
              </div>

              {/* 按钮组 */}
              <div className="flex items-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-700 hover:to-cyan-600 text-white rounded-lg transition-all shadow-lg shadow-cyan-500/30 border border-cyan-400/50"
                >
                  {editingId ? '保存' : '添加'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* 账号列表 */}
        <div className="space-y-3">
          {admins.map((admin) => (
            <div key={admin.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:bg-slate-750 transition-colors">
              <div className="flex items-start gap-4">
                {/* 图标 */}
                <div className={`p-3 rounded-lg ${
                  admin.role === 'admin' ? 'bg-cyan-600/20' : 'bg-slate-700'
                }`}>
                  {admin.role === 'admin' ? (
                    <Shield className="size-6 text-cyan-500" />
                  ) : (
                    <User className="size-6 text-slate-400" />
                  )}
                </div>

                {/* 信息 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-slate-100 font-mono">{admin.username}</span>
                    <span className={`px-2 py-0.5 text-xs rounded ${
                      admin.role === 'admin'
                        ? 'bg-cyan-600/20 text-cyan-400 border border-cyan-500/30'
                        : 'bg-slate-700 text-slate-400'
                    }`}>
                      {admin.role === 'admin' ? '管理员' : '普通用户'}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-slate-400">
                    <div>创建时间: {formatDate(admin.createdAt)}</div>
                    <div>最后登录: {formatDate(admin.lastLogin)}</div>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(admin)}
                    className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-cyan-400"
                    title="编辑"
                  >
                    <Edit className="size-4" />
                  </button>
                  {admin.username !== 'admin' && (
                    <button
                      onClick={() => handleDelete(admin)}
                      className="p-2 hover:bg-red-900/20 rounded-lg transition-colors text-red-400"
                      title="删除"
                    >
                      <Trash2 className="size-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 权限说明 */}
        <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
          <h4 className="text-cyan-400 mb-2">权限说明</h4>
          <div className="space-y-2 text-sm text-slate-300">
            <div className="flex items-start gap-2">
              <Shield className="size-4 text-cyan-500 mt-0.5" />
              <div>
                <span className="text-cyan-400">管理员：</span>
                <span className="text-slate-400">拥有所有设置权限，可以管理摄像头、传感器、AI设置、查看日志等</span>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <User className="size-4 text-slate-500 mt-0.5" />
              <div>
                <span className="text-slate-300">普通用户：</span>
                <span className="text-slate-400">只能查看关于界面和基本系统信息</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
