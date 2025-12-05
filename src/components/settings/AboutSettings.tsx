import { ArrowLeft, Shield, Cpu, Camera, AlertTriangle } from 'lucide-react';

interface AboutSettingsProps {
  onBack: () => void;
}

export function AboutSettings({ onBack }: AboutSettingsProps) {
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
          <h2 className="text-slate-100">关于系统</h2>
        </div>
      </div>

      {/* 内容 */}
      <div className="p-6 space-y-6 max-w-3xl mx-auto">
        {/* 系统信息卡片 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-cyan-600 rounded-lg">
              <Shield className="size-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-slate-100 text-xl mb-2">龙门吊视觉安全监控系统</h3>
              <p className="text-slate-400">
                专为龙门吊和门座机驾驶员打造的一体化智能监控解决方案
              </p>
            </div>
          </div>
        </div>

        {/* 版本信息 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">版本信息</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">系统版本:</span>
              <span className="text-slate-200">v2.1.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">构建日期:</span>
              <span className="text-slate-200">2025-11-21</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">平台:</span>
              <span className="text-slate-200">Linux 平板</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">内核版本:</span>
              <span className="text-slate-200">Linux 6.5.0</span>
            </div>
          </div>
        </div>

        {/* 核心功能 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">核心功能</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Camera className="size-5 text-cyan-500 mt-0.5 shrink-0" />
              <div>
                <div className="text-slate-200">多摄像头智能切换</div>
                <div className="text-slate-400 text-sm mt-1">
                  根据运动方向自动匹配对应摄像头画面
                </div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Cpu className="size-5 text-cyan-500 mt-0.5 shrink-0" />
              <div>
                <div className="text-slate-200">9轴传感器方向检测</div>
                <div className="text-slate-400 text-sm mt-1">
                  实时检测前进、后退、左转、右转运动状态
                </div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Shield className="size-5 text-cyan-500 mt-0.5 shrink-0" />
              <div>
                <div className="text-slate-200">AI智能识别</div>
                <div className="text-slate-400 text-sm mt-1">
                  人员入侵检测、目标追踪、实时报警
                </div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertTriangle className="size-5 text-cyan-500 mt-0.5 shrink-0" />
              <div>
                <div className="text-slate-200">实时安全预警</div>
                <div className="text-slate-400 text-sm mt-1">
                  多级报警机制，保障作业安全
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 技术规格 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">技术规格</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-slate-400 mb-1">摄像头支持</div>
              <div className="text-slate-200">最多4路1080P</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">AI处理</div>
              <div className="text-slate-200">实时推理 30FPS</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">传感器刷新率</div>
              <div className="text-slate-200">100Hz</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">系统延迟</div>
              <div className="text-slate-200">&lt; 50ms</div>
            </div>
          </div>
        </div>

        {/* 版权信息 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">版权信息</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            © 2025 工业安全监控系统。保留所有权利。<br />
            本系统专为工业作业环境设计，未经授权不得用于其他用途。
          </p>
        </div>

        {/* 联系信息 */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-slate-100 mb-4">技术支持</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">服务热线:</span>
              <span className="text-slate-200">400-888-8888</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">技术邮箱:</span>
              <span className="text-slate-200">support@example.com</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">在线文档:</span>
              <span className="text-cyan-500">docs.example.com</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}