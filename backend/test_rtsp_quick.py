#!/usr/bin/env python3
"""
快速测试 RTSP 服务是否可以启动
"""
import requests
import time

def test_backend_health():
    """测试后端是否运行"""
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=3)
        if response.ok:
            print("✓ 后端服务运行正常")
            return True
        else:
            print("✗ 后端服务响应异常")
            return False
    except Exception as e:
        print(f"✗ 无法连接后端服务: {e}")
        print("请确保后端服务已启动: cd backend && python -m uvicorn src.main:app --reload")
        return False

def test_rtsp_api():
    """测试 RTSP API 是否可用"""
    try:
        # 测试启动流
        response = requests.post(
            'http://127.0.0.1:8000/rtsp/streams/start',
            json={
                'stream_id': 'test-camera',
                'rtsp_url': 'rtsp://admin:cx888888@192.168.1.254/Streaming/Channels/101'
            },
            timeout=10
        )
        
        if response.ok:
            print("✓ RTSP 流启动成功")
            
            # 等待一下
            time.sleep(2)
            
            # 测试获取流信息
            info_response = requests.get('http://127.0.0.1:8000/rtsp/streams/test-camera', timeout=5)
            if info_response.ok:
                data = info_response.json()
                print(f"✓ 流信息: {data['width']}x{data['height']} @ {data['fps']}fps")
            
            # 停止流
            stop_response = requests.post('http://127.0.0.1:8000/rtsp/streams/stop/test-camera', timeout=5)
            if stop_response.ok:
                print("✓ RTSP 流停止成功")
            
            return True
        else:
            error = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"✗ RTSP 流启动失败: {error}")
            return False
            
    except Exception as e:
        print(f"✗ RTSP API 测试失败: {e}")
        return False

def main():
    print("=" * 50)
    print("RTSP 服务快速测试")
    print("=" * 50)
    
    if not test_backend_health():
        return
    
    print("\n测试 RTSP API...")
    if test_rtsp_api():
        print("\n✓ 所有测试通过！")
        print("现在可以在前端界面中查看 RTSP 视频流")
    else:
        print("\n✗ RTSP 测试失败")
        print("请检查:")
        print("1. RTSP URL 是否正确")
        print("2. 网络连接是否正常")
        print("3. 摄像头是否在线")

if __name__ == '__main__':
    main()