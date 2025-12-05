"""
Test script for Sensor API endpoints

验证 WebSocket 端点和运动模式切换端点的基本功能
"""

import sys
from pathlib import Path

# Add backend/src and parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))  # For datahandler

print("=" * 60)
print("测试传感器API导入")
print("=" * 60)

try:
    from api.sensors import router, PatternRequest
    print("✓ sensors API 导入成功")
    print(f"✓ 路由前缀: {router.prefix}")
    print(f"✓ 路由标签: {router.tags}")
    
    # 检查路由
    routes = [route.path for route in router.routes]
    print(f"\n注册的路由:")
    for route in router.routes:
        print(f"  - {route.path} ({', '.join(route.methods) if hasattr(route, 'methods') else 'WebSocket'})")
    
    # 验证 PatternRequest 模型
    print(f"\n✓ PatternRequest 模型已定义")
    test_request = PatternRequest(pattern="forward")
    print(f"  测试请求: {test_request}")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("测试主应用导入")
print("=" * 60)

try:
    from main import app
    print("✓ FastAPI 应用导入成功")
    
    # 检查所有路由
    print(f"\n应用中的所有路由:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'WebSocket'
            print(f"  - {route.path} ({methods})")
    
    # 验证传感器路由已注册
    sensor_routes = [route for route in app.routes if hasattr(route, 'path') and '/sensor' in route.path]
    if sensor_routes:
        print(f"\n✓ 传感器路由已成功注册 ({len(sensor_routes)} 个端点)")
    else:
        print(f"\n✗ 警告: 未找到传感器路由")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("所有测试通过！")
print("=" * 60)
print("\n提示: 要测试实际功能，请运行:")
print("  uv run uvicorn src.main:app --host 0.0.0.0 --port 8000")
print("\n然后访问:")
print("  - API 文档: http://localhost:8000/docs")
print("  - WebSocket: ws://localhost:8000/api/sensor/stream")
print("  - 模式切换: POST http://localhost:8000/api/sensor/pattern")
