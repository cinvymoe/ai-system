#!/usr/bin/env python3
"""
简单的 RTSP 流测试脚本
测试启动、连接和停止 RTSP 流
"""
import requests
import time

API_BASE = 'http://127.0.0.1:8000/rtsp'
STREAM_ID = 'main-camera'
RTSP_URL = 'rtsp://admin:cx888888@192.168.1.254/Streaming/Channels/101'

def test_start_stream():
    """测试启动流"""
    print(f"🚀 启动 RTSP 流: {STREAM_ID}")
    try:
        response = requests.post(
            f'{API_BASE}/streams/start',
            json={
                'stream_id': STREAM_ID,
                'rtsp_url': RTSP_URL
            },
            timeout=10
        )
        
        if response.ok:
            data = response.json()
            print(f"✓ 流启动成功: {data['message']}")
            return True
        else:
            print(f"✗ 启动失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_list_streams():
    """测试列出所有流"""
    print(f"\n📋 列出所有活动流")
    try:
        response = requests.get(f'{API_BASE}/streams', timeout=5)
        
        if response.ok:
            data = response.json()
            print(f"✓ 当前活动流数量: {data['total']}")
            for stream in data['streams']:
                print(f"  - {stream['stream_id']}: {stream['width']}x{stream['height']} @ {stream['fps']}fps")
                print(f"    连接数: {stream['connections']}, 状态: {'运行中' if stream['is_opened'] else '已停止'}")
            return True
        else:
            print(f"✗ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_get_stream_info():
    """测试获取流信息"""
    print(f"\n📊 获取流信息: {STREAM_ID}")
    try:
        response = requests.get(f'{API_BASE}/streams/{STREAM_ID}', timeout=5)
        
        if response.ok:
            data = response.json()
            print(f"✓ 流信息:")
            print(f"  分辨率: {data['width']}x{data['height']}")
            print(f"  帧率: {data['fps']} FPS")
            print(f"  连接数: {data['connections']}")
            print(f"  状态: {'运行中' if data['is_opened'] else '已停止'}")
            return True
        else:
            print(f"✗ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_stop_stream():
    """测试停止流"""
    print(f"\n⏹️  停止 RTSP 流: {STREAM_ID}")
    try:
        response = requests.post(f'{API_BASE}/streams/stop/{STREAM_ID}', timeout=5)
        
        if response.ok:
            data = response.json()
            print(f"✓ 流停止成功: {data['message']}")
            return True
        else:
            print(f"✗ 停止失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def main():
    print("=" * 60)
    print("RTSP 流测试")
    print("=" * 60)
    
    # 测试启动流
    if not test_start_stream():
        print("\n⚠️  启动流失败，请检查:")
        print("  1. 后端服务是否运行 (python -m uvicorn src.main:app --reload)")
        print("  2. RTSP URL 是否正确")
        print("  3. 网络连接是否正常")
        return
    
    # 等待流初始化
    print("\n⏳ 等待流初始化...")
    time.sleep(2)
    
    # 测试列出流
    test_list_streams()
    
    # 测试获取流信息
    test_get_stream_info()
    
    # 等待一段时间
    print("\n⏳ 流运行中，5秒后停止...")
    time.sleep(5)
    
    # 测试停止流
    test_stop_stream()
    
    # 验证流已停止
    print("\n🔍 验证流已停止...")
    time.sleep(1)
    test_list_streams()
    
    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
