#!/usr/bin/env python3
"""
简单的摄像头连接测试
"""

import socket
import sys

def test_camera_connection():
    """测试摄像头网络连接"""
    camera_ip = "192.168.1.254"
    rtsp_port = 554
    http_port = 80
    
    print(f"🔍 测试摄像头连接: {camera_ip}")
    
    # 测试 HTTP 端口 (Web界面)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((camera_ip, http_port))
        sock.close()
        
        if result == 0:
            print(f"✅ HTTP端口 {http_port} 连接成功 - Web界面可访问")
        else:
            print(f"❌ HTTP端口 {http_port} 连接失败")
    except Exception as e:
        print(f"❌ HTTP连接测试失败: {e}")
    
    # 测试 RTSP 端口
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((camera_ip, rtsp_port))
        sock.close()
        
        if result == 0:
            print(f"✅ RTSP端口 {rtsp_port} 连接成功 - 流媒体服务可用")
            return True
        else:
            print(f"❌ RTSP端口 {rtsp_port} 连接失败")
            return False
    except Exception as e:
        print(f"❌ RTSP连接测试失败: {e}")
        return False

def main():
    print("🚀 摄像头连接测试")
    print("=" * 40)
    
    if test_camera_connection():
        print("\n✅ 摄像头网络连接正常")
        print("\n📝 下一步检查:")
        print("1. 确认后端服务运行: uvicorn src.main:app --reload")
        print("2. 检查认证信息是否正确")
        print("3. 在浏览器访问: http://192.168.1.254")
    else:
        print("\n❌ 摄像头网络连接失败")
        print("\n🔧 解决方案:")
        print("1. 检查摄像头是否开机")
        print("2. 检查网络连接")
        print("3. 确认IP地址是否正确")
        print("4. 检查防火墙设置")

if __name__ == "__main__":
    main()