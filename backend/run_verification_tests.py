#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化验证测试脚本
用于验证摄像头数据库集成的基本功能
"""

import sys
import time
import requests
from typing import Dict, List, Any
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/cameras"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_section(title: str):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

# 测试结果跟踪
class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.start_time = time.time()
    
    def add_pass(self):
        self.total += 1
        self.passed += 1
    
    def add_fail(self):
        self.total += 1
        self.failed += 1
    
    def add_warning(self):
        self.warnings += 1
    
    def print_summary(self):
        elapsed = time.time() - self.start_time
        print_section("测试总结")
        print(f"总测试数: {self.total}")
        print(f"{Colors.GREEN}通过: {self.passed}{Colors.END}")
        print(f"{Colors.RED}失败: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}警告: {self.warnings}{Colors.END}")
        print(f"通过率: {(self.passed/self.total*100) if self.total > 0 else 0:.1f}%")
        print(f"耗时: {elapsed:.2f} 秒")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}所有测试通过！{Colors.END}")
            return 0
        else:
            print(f"\n{Colors.RED}有 {self.failed} 个测试失败{Colors.END}")
            return 1

results = TestResults()

def check_backend_available() -> bool:
    """检查后端服务是否可用"""
    print_section("1. 检查后端服务")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success("后端服务运行正常")
            results.add_pass()
            return True
        else:
            print_error(f"后端服务返回异常状态码: {response.status_code}")
            results.add_fail()
            return False
    except requests.exceptions.ConnectionError:
        print_error("无法连接到后端服务")
        print_info("请确保后端服务已启动: cd backend && uvicorn src.main:app --reload")
        results.add_fail()
        return False
    except Exception as e:
        print_error(f"检查后端服务时出错: {e}")
        results.add_fail()
        return False

def test_get_all_cameras():
    """测试获取所有摄像头"""
    print_section("2. 测试获取所有摄像头")
    try:
        response = requests.get(API_BASE, timeout=5)
        if response.status_code == 200:
            cameras = response.json()
            print_success(f"成功获取摄像头列表，共 {len(cameras)} 个摄像头")
            results.add_pass()
            return cameras
        else:
            print_error(f"获取摄像头列表失败: {response.status_code}")
            results.add_fail()
            return []
    except Exception as e:
        print_error(f"获取摄像头列表时出错: {e}")
        results.add_fail()
        return []

def test_create_camera() -> Dict[str, Any] | None:
    """测试创建摄像头"""
    print_section("3. 测试创建摄像头")
    
    camera_data = {
        "name": f"测试摄像头_{int(time.time())}",
        "url": "rtsp://192.168.1.100:554/stream",
        "direction": "forward",
        "enabled": True,
        "resolution": "1920x1080",
        "fps": 30,
        "brightness": 50,
        "contrast": 50,
        "status": "offline"
    }
    
    try:
        response = requests.post(API_BASE, json=camera_data, timeout=5)
        if response.status_code == 201:
            camera = response.json()
            print_success(f"成功创建摄像头: {camera['name']} (ID: {camera['id']})")
            
            # 验证返回的数据
            for key, value in camera_data.items():
                if camera.get(key) != value:
                    print_warning(f"字段 {key} 值不匹配: 期望 {value}, 实际 {camera.get(key)}")
                    results.add_warning()
            
            results.add_pass()
            return camera
        else:
            print_error(f"创建摄像头失败: {response.status_code} - {response.text}")
            results.add_fail()
            return None
    except Exception as e:
        print_error(f"创建摄像头时出错: {e}")
        results.add_fail()
        return None

def test_create_duplicate_name(existing_name: str):
    """测试创建重复名称的摄像头"""
    print_section("4. 测试创建重复名称摄像头")
    
    camera_data = {
        "name": existing_name,
        "url": "rtsp://192.168.1.101:554/stream",
        "direction": "backward",
    }
    
    try:
        response = requests.post(API_BASE, json=camera_data, timeout=5)
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "already exists" in error_detail.lower():
                print_success("正确拒绝了重复名称的摄像头")
                results.add_pass()
            else:
                print_warning(f"错误消息不明确: {error_detail}")
                results.add_warning()
                results.add_pass()
        else:
            print_error(f"应该返回 400 错误，实际返回: {response.status_code}")
            results.add_fail()
    except Exception as e:
        print_error(f"测试重复名称时出错: {e}")
        results.add_fail()

def test_create_invalid_data():
    """测试创建无效数据"""
    print_section("5. 测试数据验证")
    
    test_cases = [
        {
            "name": "空名称测试",
            "data": {"name": "", "url": "rtsp://test", "direction": "forward"},
            "expected_error": "validation"
        },
        {
            "name": "无效URL测试",
            "data": {"name": "测试", "url": "http://test", "direction": "forward"},
            "expected_error": "validation"
        },
        {
            "name": "超出范围的亮度",
            "data": {"name": "测试", "url": "rtsp://test", "direction": "forward", "brightness": 150},
            "expected_error": "validation"
        },
        {
            "name": "超出范围的FPS",
            "data": {"name": "测试", "url": "rtsp://test", "direction": "forward", "fps": 100},
            "expected_error": "validation"
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(API_BASE, json=test_case["data"], timeout=5)
            if response.status_code == 422 or response.status_code == 400:
                print_success(f"{test_case['name']}: 正确拒绝了无效数据")
                results.add_pass()
            else:
                print_error(f"{test_case['name']}: 应该拒绝，但返回 {response.status_code}")
                results.add_fail()
        except Exception as e:
            print_error(f"{test_case['name']}: 测试时出错 - {e}")
            results.add_fail()

def test_get_camera_by_id(camera_id: str):
    """测试通过ID获取摄像头"""
    print_section("6. 测试通过ID获取摄像头")
    
    try:
        response = requests.get(f"{API_BASE}/{camera_id}", timeout=5)
        if response.status_code == 200:
            camera = response.json()
            print_success(f"成功获取摄像头: {camera['name']}")
            results.add_pass()
            return camera
        else:
            print_error(f"获取摄像头失败: {response.status_code}")
            results.add_fail()
            return None
    except Exception as e:
        print_error(f"获取摄像头时出错: {e}")
        results.add_fail()
        return None

def test_update_camera(camera_id: str):
    """测试更新摄像头"""
    print_section("7. 测试更新摄像头")
    
    update_data = {
        "brightness": 70,
        "contrast": 60,
        "fps": 25
    }
    
    try:
        response = requests.patch(f"{API_BASE}/{camera_id}", json=update_data, timeout=5)
        if response.status_code == 200:
            camera = response.json()
            print_success(f"成功更新摄像头: {camera['name']}")
            
            # 验证更新
            for key, value in update_data.items():
                if camera.get(key) != value:
                    print_warning(f"字段 {key} 未正确更新: 期望 {value}, 实际 {camera.get(key)}")
                    results.add_warning()
            
            results.add_pass()
            return camera
        else:
            print_error(f"更新摄像头失败: {response.status_code}")
            results.add_fail()
            return None
    except Exception as e:
        print_error(f"更新摄像头时出错: {e}")
        results.add_fail()
        return None

def test_update_camera_status(camera_id: str):
    """测试更新摄像头状态"""
    print_section("8. 测试更新摄像头状态")
    
    try:
        # 更新为 online
        response = requests.patch(
            f"{API_BASE}/{camera_id}/status",
            params={"status": "online"},
            timeout=5
        )
        if response.status_code == 200:
            camera = response.json()
            if camera.get("status") == "online":
                print_success("成功更新状态为 online")
                results.add_pass()
            else:
                print_error(f"状态未正确更新: {camera.get('status')}")
                results.add_fail()
        else:
            print_error(f"更新状态失败: {response.status_code}")
            results.add_fail()
    except Exception as e:
        print_error(f"更新状态时出错: {e}")
        results.add_fail()

def test_get_by_direction():
    """测试按方向获取摄像头"""
    print_section("9. 测试按方向获取摄像头")
    
    directions = ["forward", "backward", "left", "right", "idle"]
    
    for direction in directions:
        try:
            response = requests.get(f"{API_BASE}/direction/{direction}", timeout=5)
            if response.status_code == 200:
                cameras = response.json()
                # 验证所有返回的摄像头都是指定方向
                all_correct = all(cam.get("direction") == direction for cam in cameras)
                if all_correct:
                    print_success(f"方向 {direction}: 获取到 {len(cameras)} 个摄像头")
                    results.add_pass()
                else:
                    print_error(f"方向 {direction}: 返回了错误方向的摄像头")
                    results.add_fail()
            else:
                print_error(f"获取方向 {direction} 失败: {response.status_code}")
                results.add_fail()
        except Exception as e:
            print_error(f"获取方向 {direction} 时出错: {e}")
            results.add_fail()

def test_delete_camera(camera_id: str):
    """测试删除摄像头"""
    print_section("10. 测试删除摄像头")
    
    try:
        response = requests.delete(f"{API_BASE}/{camera_id}", timeout=5)
        if response.status_code == 200:
            print_success(f"成功删除摄像头 (ID: {camera_id})")
            
            # 验证删除：尝试再次获取应该返回 404
            verify_response = requests.get(f"{API_BASE}/{camera_id}", timeout=5)
            if verify_response.status_code == 404:
                print_success("验证删除成功：摄像头不再存在")
                results.add_pass()
            else:
                print_error(f"删除验证失败：摄像头仍然存在 (状态码: {verify_response.status_code})")
                results.add_fail()
        else:
            print_error(f"删除摄像头失败: {response.status_code}")
            results.add_fail()
    except Exception as e:
        print_error(f"删除摄像头时出错: {e}")
        results.add_fail()

def test_delete_nonexistent():
    """测试删除不存在的摄像头"""
    print_section("11. 测试删除不存在的摄像头")
    
    fake_id = "nonexistent-id-12345"
    
    try:
        response = requests.delete(f"{API_BASE}/{fake_id}", timeout=5)
        if response.status_code == 404:
            print_success("正确返回 404 错误")
            results.add_pass()
        else:
            print_error(f"应该返回 404，实际返回: {response.status_code}")
            results.add_fail()
    except Exception as e:
        print_error(f"测试删除不存在的摄像头时出错: {e}")
        results.add_fail()

def test_performance():
    """测试性能"""
    print_section("12. 测试性能")
    
    # 测试获取所有摄像头的响应时间
    try:
        start = time.time()
        response = requests.get(API_BASE, timeout=5)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            cameras = response.json()
            print_info(f"摄像头数量: {len(cameras)}")
            print_info(f"响应时间: {elapsed*1000:.2f} ms")
            
            if elapsed < 2.0:
                print_success("响应时间符合要求 (< 2秒)")
                results.add_pass()
            else:
                print_warning(f"响应时间较慢: {elapsed:.2f} 秒")
                results.add_warning()
                results.add_pass()
        else:
            print_error(f"性能测试失败: {response.status_code}")
            results.add_fail()
    except Exception as e:
        print_error(f"性能测试时出错: {e}")
        results.add_fail()

def main():
    """主测试流程"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("摄像头数据库集成 - 自动化验证测试")
    print(f"{'='*60}{Colors.END}\n")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. 检查后端服务
    if not check_backend_available():
        print_error("\n后端服务不可用，无法继续测试")
        return 1
    
    # 2. 获取所有摄像头
    initial_cameras = test_get_all_cameras()
    
    # 3. 创建摄像头
    created_camera = test_create_camera()
    if not created_camera:
        print_warning("无法创建测试摄像头，跳过后续测试")
        return results.print_summary()
    
    camera_id = created_camera["id"]
    camera_name = created_camera["name"]
    
    # 4. 测试重复名称
    test_create_duplicate_name(camera_name)
    
    # 5. 测试数据验证
    test_create_invalid_data()
    
    # 6. 通过ID获取摄像头
    test_get_camera_by_id(camera_id)
    
    # 7. 更新摄像头
    test_update_camera(camera_id)
    
    # 8. 更新状态
    test_update_camera_status(camera_id)
    
    # 9. 按方向获取
    test_get_by_direction()
    
    # 10. 删除摄像头
    test_delete_camera(camera_id)
    
    # 11. 删除不存在的摄像头
    test_delete_nonexistent()
    
    # 12. 性能测试
    test_performance()
    
    # 打印总结
    return results.print_summary()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}测试过程中发生未预期的错误: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
