# 测试执行指南

## 概述
本文档提供了完整的测试执行步骤，包括环境准备、自动化测试和手动测试。

## 测试环境准备

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（如果使用）
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 启动后端服务
uvicorn src.main:app --reload --port 8000
```

验证后端服务：
- 打开浏览器访问 http://localhost:8000/docs
- 应该看到 FastAPI 的 Swagger UI 文档

### 2. 启动前端应用

在新的终端窗口：

```bash
# 在项目根目录
npm run dev
```

验证前端应用：
- 应用应该在 Electron 窗口中打开
- 或在浏览器中访问显示的 URL

### 3. 检查数据库

```bash
# 检查数据库文件是否存在
ls -la backend/data/vision_security.db

# 查看数据库内容（可选）
sqlite3 backend/data/vision_security.db "SELECT * FROM cameras;"
```

## 自动化验证测试

### 运行自动化验证脚本

```bash
# 确保后端服务正在运行
python backend/run_verification_tests.py
```

这个脚本会自动测试：
- ✓ 后端服务可用性
- ✓ 获取所有摄像头
- ✓ 创建摄像头
- ✓ 重复名称验证
- ✓ 数据验证
- ✓ 通过ID获取摄像头
- ✓ 更新摄像头
- ✓ 更新状态
- ✓ 按方向获取
- ✓ 删除摄像头
- ✓ 删除不存在的摄像头
- ✓ 性能测试

### 运行单元测试

```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_camera_repository.py -v
pytest tests/test_camera_service.py -v
pytest tests/test_api_cameras.py -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

## 手动测试

### 使用手动测试清单

打开 `backend/MANUAL_TEST_CHECKLIST.md` 文件，按照清单逐项测试。

### 关键测试场景

#### 场景 1：完整的 CRUD 流程

1. **创建摄像头**
   - 打开应用
   - 导航到摄像头设置
   - 点击"添加摄像头"
   - 填写所有字段
   - 保存并验证成功

2. **查看摄像头**
   - 在列表中找到新创建的摄像头
   - 验证所有信息正确显示
   - 验证按方向分组正确

3. **更新摄像头**
   - 点击编辑按钮
   - 修改某些字段
   - 保存并验证更新成功

4. **删除摄像头**
   - 点击删除按钮
   - 确认删除
   - 验证摄像头从列表中移除

#### 场景 2：数据持久化验证

1. 创建几个摄像头
2. 记录它们的配置
3. 完全关闭应用（前端和后端）
4. 重新启动应用
5. 验证所有数据仍然存在

#### 场景 3：错误处理验证

1. **验证错误**
   - 尝试创建空名称的摄像头
   - 尝试创建重复名称的摄像头
   - 尝试输入无效的 URL
   - 尝试输入超出范围的数值

2. **网络错误**
   - 停止后端服务
   - 尝试执行操作
   - 验证显示友好的错误消息
   - 重启后端服务
   - 验证可以恢复正常操作

#### 场景 4：并发操作

1. 快速连续创建多个摄像头
2. 同时编辑不同的摄像头
3. 验证所有操作都成功
4. 验证数据一致性

## 使用 API 直接测试

### 使用 curl 测试

```bash
# 获取所有摄像头
curl http://localhost:8000/api/cameras

# 创建摄像头
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试摄像头",
    "url": "rtsp://192.168.1.100:554/stream",
    "direction": "forward",
    "enabled": true,
    "resolution": "1920x1080",
    "fps": 30,
    "brightness": 50,
    "contrast": 50
  }'

# 获取特定摄像头（替换 {id}）
curl http://localhost:8000/api/cameras/{id}

# 更新摄像头
curl -X PATCH http://localhost:8000/api/cameras/{id} \
  -H "Content-Type: application/json" \
  -d '{"brightness": 70}'

# 删除摄像头
curl -X DELETE http://localhost:8000/api/cameras/{id}

# 按方向获取
curl http://localhost:8000/api/cameras/direction/forward
```

### 使用 Swagger UI 测试

1. 打开 http://localhost:8000/docs
2. 展开任意 API 端点
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应

## 测试数据管理

### 备份测试数据

```bash
# 备份数据库
cp backend/data/vision_security.db backend/data/vision_security.db.backup

# 或使用备份脚本
bash backend/scripts/backup_data.sh
```

### 重置测试数据

```bash
# 删除数据库
rm backend/data/vision_security.db

# 重启后端服务，数据库会自动重新创建
```

### 导入测试数据

```bash
# 使用示例数据
python backend/src/migrate_data.py
```

## 性能测试

### 测试大量数据

```bash
# 创建测试脚本生成大量摄像头
python -c "
import requests
for i in range(50):
    requests.post('http://localhost:8000/api/cameras', json={
        'name': f'Camera_{i}',
        'url': f'rtsp://192.168.1.{i}:554/stream',
        'direction': ['forward', 'backward', 'left', 'right', 'idle'][i % 5]
    })
"
```

然后测试：
- 列表加载时间
- 滚动性能
- 搜索/筛选性能

## 测试结果记录

### 创建测试报告

1. 复制 `MANUAL_TEST_CHECKLIST.md` 为 `TEST_REPORT_YYYYMMDD.md`
2. 填写每个测试场景的结果
3. 记录发现的问题
4. 添加截图（如果需要）
5. 填写测试总结

### 问题跟踪

发现的问题应该记录：
- 问题描述
- 重现步骤
- 预期行为
- 实际行为
- 严重程度（高/中/低）
- 截图或日志

## 常见问题排查

### 后端无法启动

```bash
# 检查端口是否被占用
lsof -i :8000

# 检查 Python 环境
python --version
which python

# 检查依赖
pip list | grep fastapi
```

### 数据库错误

```bash
# 检查数据库文件权限
ls -la backend/data/vision_security.db

# 检查数据库完整性
sqlite3 backend/data/vision_security.db "PRAGMA integrity_check;"

# 重建数据库
rm backend/data/vision_security.db
python -c "from src.database import init_db; init_db()"
```

### 前端无法连接后端

1. 检查后端是否运行：`curl http://localhost:8000/docs`
2. 检查 CORS 配置
3. 检查浏览器控制台错误
4. 检查网络请求（开发者工具 Network 标签）

### IPC 通信问题

1. 检查 Electron 主进程日志
2. 检查预加载脚本是否正确加载
3. 验证 contextBridge API 暴露
4. 检查渲染进程控制台

## 测试完成检查清单

在完成所有测试后，确认：

- [ ] 所有自动化测试通过
- [ ] 所有手动测试场景完成
- [ ] 所有 CRUD 操作正常工作
- [ ] 数据验证正确
- [ ] 错误处理友好
- [ ] 数据持久化正常
- [ ] 性能符合要求
- [ ] UI 交互流畅
- [ ] 测试报告已完成
- [ ] 发现的问题已记录

## 下一步

测试完成后：
1. 审查测试报告
2. 修复发现的问题
3. 重新测试修复的功能
4. 更新文档
5. 准备部署

## 联系和支持

如有问题，请查看：
- `backend/README.md` - 后端文档
- `backend/QUICK_REFERENCE.md` - 快速参考
- `backend/MIGRATION_GUIDE.md` - 迁移指南
