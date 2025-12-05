#!/usr/bin/env python3
"""Quick test script for camera online check functionality."""
import sys
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_single_camera(camera_id: str) -> Optional[dict]:
    """Check status of a single camera."""
    print(f"检查摄像头: {camera_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cameras/{camera_id}/check-status",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 摄像头名称: {data['camera_name']}")
            print(f"  URL: {data['url']}")
            print(f"  之前状态: {data['previous_status']}")
            print(f"  当前状态: {data['current_status']}")
            print(f"  在线: {'是' if data['is_online'] else '否'}")
            print(f"  状态改变: {'是' if data['status_changed'] else '否'}")
            return data
        else:
            print(f"✗ 错误 {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务器")
        print(f"  请确保后端服务正在运行: {BASE_URL}")
        return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def check_all_cameras() -> Optional[dict]:
    """Check status of all cameras."""
    print("检查所有摄像头...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cameras/check-all-status",
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n摄像头总数: {data['total_cameras']}")
            print(f"在线数量: {data['online_count']}")
            print(f"离线数量: {data['offline_count']}")
            print(f"状态改变: {data['status_changed_count']}")
            
            print("\n详细信息:")
            print("-" * 60)
            
            for camera in data['cameras']:
                status_icon = "✓" if camera.get('is_online', False) else "✗"
                status = camera.get('current_status', 'unknown')
                name = camera.get('camera_name', 'Unknown')
                
                print(f"{status_icon} {name:20s} | {status:8s}", end="")
                
                if camera.get('status_changed', False):
                    prev = camera.get('previous_status', '')
                    curr = camera.get('current_status', '')
                    print(f" | 状态改变: {prev} → {curr}")
                else:
                    print()
                    
                if 'error' in camera:
                    print(f"  错误: {camera['error']}")
            
            return data
        else:
            print(f"✗ 错误 {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务器")
        print(f"  请确保后端服务正在运行: {BASE_URL}")
        return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def get_all_cameras() -> Optional[list]:
    """Get list of all cameras."""
    try:
        response = requests.get(f"{BASE_URL}/api/cameras", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def main():
    """Main test function."""
    print_section("摄像头在线检查测试")
    
    # Check if backend is running
    print("检查后端服务...")
    try:
        response = requests.get(f"{BASE_URL}/api/cameras", timeout=5)
        print(f"✓ 后端服务运行正常 ({BASE_URL})")
    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到后端服务器: {BASE_URL}")
        print("\n请先启动后端服务:")
        print("  cd backend")
        print("  uvicorn src.main:app --reload")
        sys.exit(1)
    
    # Get list of cameras
    cameras = get_all_cameras()
    if not cameras:
        print("\n✗ 无法获取摄像头列表或数据库中没有摄像头")
        print("\n请先添加摄像头，例如:")
        print('  curl -X POST "http://localhost:8000/api/cameras" \\')
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"id":"cam-001","name":"测试摄像头","url":"rtsp://example.com/stream","direction":"forward"}\'')
        sys.exit(1)
    
    print(f"✓ 找到 {len(cameras)} 个摄像头\n")
    
    # Test 1: Check all cameras
    print_section("测试 1: 检查所有摄像头状态")
    result = check_all_cameras()
    
    if result and result['total_cameras'] > 0:
        # Test 2: Check first camera individually
        print_section("测试 2: 检查单个摄像头状态")
        first_camera_id = cameras[0]['id']
        check_single_camera(first_camera_id)
    
    print_section("测试完成")
    print("所有测试已完成！\n")


if __name__ == "__main__":
    main()
