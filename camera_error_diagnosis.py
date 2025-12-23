#!/usr/bin/env python3
"""
摄像头错误诊断脚本
用于诊断和修复 Camera Error 问题
"""

import subprocess
import sys
import time
import socket
from urllib.parse import urlparse

def check_backend_service():
    """检查后端服务是否运行"""
    print("🔍 检查后端服务状态...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/cameras", timeout=5)
        print("✅ 后端服务运行正常")
        return True
    except ImportError:
        print("❌ 缺少 requests 模块")
        return False
    except Exception as e:
        print(f"❌ 后端服务未运行: {e}")
        return False

def check_camera_connectivity():
    """检查摄像头网络连接"""
    print("\n🔍 检查摄像头网络连接...")
    camera_ip = "192.168.1.254"
    rtsp_port = 554
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((camera_ip, rtsp_port))
        sock.close()
        
        if result == 0:
            print(f"✅ 摄像头 {camera_ip}:{rtsp_port} 网络连接正常")
            return True
        else:
            print(f"❌ 摄像头 {camera_ip}:{rtsp_port} 网络连接失败")
            return False
    except Exception as e:
        print(f"❌ 网络连接检查失败: {e}")
        return False

def test_rtsp_stream():
    """测试 RTSP 流连接"""
    print("\n🔍 测试 RTSP 流连接...")
    rtsp_url = "rtsp://admin:cx888888@192.168.1.254/Streaming/Channels/101"
    
    try:
        # 使用 ffprobe 测试 RTSP 流
        cmd = [
            "ffprobe", 
            "-v", "quiet", 
            "-print_format", "json", 
            "-show_streams", 
            "-rtsp_transport", "tcp",
            "-timeout", "10000000",  # 10 seconds
            rtsp_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ RTSP 流连接成功")
            return True
        else:
            print(f"❌ RTSP 流连接失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ RTSP 流连接超时")
        return False
    except FileNotFoundError:
        print("❌ 未找到 ffprobe 工具，请安装 ffmpeg")
        return False
    except Exception as e:
        print(f"❌ RTSP 流测试失败: {e}")
        return False

def check_camera_credentials():
    """检查摄像头认证信息"""
    print("\n🔍 检查摄像头认证信息...")
    
    # 这里可以添加更详细的认证检查
    print("📝 当前使用的认证信息:")
    print("   用户名: admin")
    print("   密码: cx888888")
    print("   IP地址: 192.168.1.254")
    print("💡 如果认证失败，请检查摄像头的用户名和密码是否正确")

def provide_solutions():
    """提供解决方案"""
    print("\n🔧 解决方案:")
    print("1. 启动后端服务:")
    print("   cd backend")
    print("   uvicorn src.main:app --reload")
    print()
    print("2. 检查网络连接:")
    print("   ping 192.168.1.254")
    print()
    print("3. 验证摄像头认证:")
    print("   - 检查摄像头Web界面是否可访问: http://192.168.1.254")
    print("   - 确认用户名密码: admin/cx888888")
    print()
    print("4. 测试RTSP流:")
    print("   ffplay rtsp://admin:cx888888@192.168.1.254/Streaming/Channels/101")
    print()
    print("5. 检查防火墙设置:")
    print("   - 确保端口554 (RTSP) 和8000 (后端API) 开放")

def main():
    """主函数"""
    print("🚀 摄像头错误诊断开始...")
    print("=" * 60)
    
    # 检查各个组件
    backend_ok = check_backend_service()
    network_ok = check_camera_connectivity()
    rtsp_ok = test_rtsp_stream()
    
    print("\n" + "=" * 60)
    print("📊 诊断结果:")
    print(f"   后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"   网络连接: {'✅ 正常' if network_ok else '❌ 异常'}")
    print(f"   RTSP流: {'✅ 正常' if rtsp_ok else '❌ 异常'}")
    
    if not (backend_ok and network_ok and rtsp_ok):
        check_camera_credentials()
        provide_solutions()
    else:
        print("\n🎉 所有检查都通过！摄像头应该可以正常工作。")
        print("如果仍然看到 Camera Error，请检查前端控制台的错误信息。")

if __name__ == "__main__":
    main()