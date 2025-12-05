#!/usr/bin/env python3
"""测试新添加的路由"""

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_route(path, description):
    """测试单个路由"""
    url = f"{BASE_URL}{path}"
    print(f"\n测试: {description}")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✓ 成功")
            if 'html' in response.headers.get('content-type', '').lower():
                print(f"返回 HTML 页面 ({len(response.text)} 字符)")
            else:
                print(f"返回: {response.text[:100]}...")
        else:
            print(f"✗ 失败: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("测试新添加的后端路由")
    print("=" * 60)
    
    test_route("/", "根路径")
    test_route("/health", "健康检查")
    test_route("/test", "测试页面索引")
    test_route("/test/websocket", "WebSocket 测试页面")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n如果看到 404 错误，请重启后端服务:")
    print("  cd backend && bash restart_backend.sh")
    print("\n或者手动重启:")
    print("  pkill -f 'uvicorn src.main:app'")
    print("  cd backend && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
