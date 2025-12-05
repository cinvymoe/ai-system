# 测试快速参考

## 快速启动测试

### 1分钟快速测试

```bash
# 终端 1: 启动后端
cd backend && uvicorn src.main:app --reload

# 终端 2: 运行自动化测试
python backend/run_verification_tests.py

# 终端 3: 启动前端
npm run dev
```

## 常用测试命令

### 后端测试

```bash
# 运行所有单元测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_camera_repository.py -v

# 运行带覆盖率的测试
pytest tests/ --cov=src --cov-report=term-missing

# 运行自动化验证
python run_verification_tests.py
```

### API 测试

```bash
# 获取所有摄像头
curl http://localhost:8000/api/cameras

# 创建摄像头
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","url":"rtsp://test","direction":"forward"}'

# 更新摄像头 (替换 {id})
curl -X PATCH http://localhost:8000/api/cameras/{id} \
  -H "Content-Type: application/json" \
  -d '{"brightness":70}'

# 删除摄像头
curl -X DELETE http://localhost:8000/api/cameras/{id}
```

### 数据库操作

```bash
# 查看所有摄像头
sqlite3 backend/data/vision_security.db "SELECT * FROM cameras;"

# 查看摄像头数量
sqlite3 backend/data/vision_security.db "SELECT COUNT(*) FROM cameras;"

# 按方向统计
sqlite3 backend/data/vision_security.db \
  "SELECT direction, COUNT(*) FROM cameras GROUP BY direction;"

# 备份数据库
cp backend/data/vision_security.db backend/data/vision_security.db.backup

# 重置数据库
rm backend/data/vision_security.db
```

## 关键测试场景

### 场景 1: 基本 CRUD (5分钟)

1. ✓ 创建摄像头
2. ✓ 查看列表
3. ✓ 编辑摄像头
4. ✓ 删除摄像头

### 场景 2: 数据验证 (3分钟)

1. ✓ 空名称 → 应该拒绝
2. ✓ 重复名称 → 应该拒绝
3. ✓ 无效 URL → 应该拒绝
4. ✓ 超出范围的值 → 应该拒绝

### 场景 3: 持久化 (2分钟)

1. ✓ 创建摄像头
2. ✓ 重启应用
3. ✓ 验证数据仍存在

### 场景 4: 错误处理 (3分钟)

1. ✓ 停止后端 → 应该显示错误
2. ✓ 重启后端 → 应该恢复正常

## 测试检查清单

### 每次发布前必测

- [ ] 所有单元测试通过
- [ ] 自动化验证脚本通过
- [ ] 创建摄像头正常
- [ ] 更新摄像头正常
- [ ] 删除摄像头正常
- [ ] 数据持久化正常
- [ ] 错误提示友好

### 重要功能测试

- [ ] 名称重复验证
- [ ] 数据验证
- [ ] 状态切换
- [ ] 按方向分组
- [ ] UI 响应及时

## 常见问题快速修复

### 后端无法启动

```bash
# 检查端口
lsof -i :8000
# 如果被占用，杀死进程
kill -9 <PID>
```

### 数据库损坏

```bash
# 备份当前数据库
mv backend/data/vision_security.db backend/data/vision_security.db.old
# 重新初始化
python -c "from src.database import init_db; init_db()"
```

### 测试失败

```bash
# 清理缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
# 重新运行
pytest tests/ -v
```

## 性能基准

| 操作 | 目标时间 | 可接受时间 |
|------|----------|------------|
| 获取所有摄像头 | < 500ms | < 2s |
| 创建摄像头 | < 300ms | < 1s |
| 更新摄像头 | < 300ms | < 1s |
| 删除摄像头 | < 300ms | < 1s |
| 状态切换 | < 200ms | < 500ms |

## 测试数据

### 有效的测试数据

```json
{
  "name": "测试摄像头1",
  "url": "rtsp://192.168.1.100:554/stream",
  "direction": "forward",
  "enabled": true,
  "resolution": "1920x1080",
  "fps": 30,
  "brightness": 50,
  "contrast": 50
}
```

### 无效的测试数据

```json
// 空名称
{"name": "", "url": "rtsp://test", "direction": "forward"}

// 无效 URL
{"name": "测试", "url": "http://test", "direction": "forward"}

// 超出范围
{"name": "测试", "url": "rtsp://test", "direction": "forward", "brightness": 150}
```

## 测试报告位置

- 手动测试清单: `backend/MANUAL_TEST_CHECKLIST.md`
- 测试报告模板: `backend/TEST_REPORT_TEMPLATE.md`
- 测试执行指南: `backend/TEST_EXECUTION_GUIDE.md`
- 自动化测试脚本: `backend/run_verification_tests.py`

## 联系信息

- 文档: `backend/README.md`
- 快速参考: `backend/QUICK_REFERENCE.md`
- 迁移指南: `backend/MIGRATION_GUIDE.md`
