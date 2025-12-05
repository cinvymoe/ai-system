#!/usr/bin/env python3
"""测试 AI 设置 API"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_response(title, response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")

def test_ai_settings():
    """测试 AI 设置 API"""
    
    print("\n🧪 开始测试 AI 设置 API")
    
    # 1. 获取 AI 设置（如果不存在会自动创建默认设置）
    print("\n1️⃣ 获取 AI 设置")
    response = requests.get(f"{BASE_URL}/api/ai-settings")
    print_response("GET /api/ai-settings", response)
    
    if response.status_code == 200:
        settings = response.json()
        settings_id = settings['id']
        print(f"\n✅ 获取成功，设置ID: {settings_id}")
    else:
        print("\n❌ 获取失败")
        return
    
    # 2. 更新置信度阈值
    print("\n2️⃣ 更新置信度阈值")
    update_data = {
        "confidence_threshold": 80.0
    }
    response = requests.put(
        f"{BASE_URL}/api/ai-settings/{settings_id}",
        json=update_data
    )
    print_response(f"PUT /api/ai-settings/{settings_id}", response)
    
    # 3. 设置危险区域
    print("\n3️⃣ 设置危险区域（4个点）")
    update_data = {
        "danger_zone": [
            {"x": 0.1, "y": 0.2},
            {"x": 0.4, "y": 0.2},
            {"x": 0.4, "y": 0.8},
            {"x": 0.1, "y": 0.8}
        ]
    }
    response = requests.put(
        f"{BASE_URL}/api/ai-settings/{settings_id}",
        json=update_data
    )
    print_response(f"PUT /api/ai-settings/{settings_id} (危险区域)", response)
    
    # 4. 设置警告区域
    print("\n4️⃣ 设置警告区域（4个点）")
    update_data = {
        "warning_zone": [
            {"x": 0.5, "y": 0.3},
            {"x": 0.8, "y": 0.3},
            {"x": 0.8, "y": 0.7},
            {"x": 0.5, "y": 0.7}
        ]
    }
    response = requests.put(
        f"{BASE_URL}/api/ai-settings/{settings_id}",
        json=update_data
    )
    print_response(f"PUT /api/ai-settings/{settings_id} (警告区域)", response)
    
    # 5. 更新报警设置
    print("\n5️⃣ 更新报警设置")
    update_data = {
        "sound_alarm": True,
        "visual_alarm": True,
        "auto_screenshot": True,
        "alarm_cooldown": 10
    }
    response = requests.put(
        f"{BASE_URL}/api/ai-settings/{settings_id}",
        json=update_data
    )
    print_response(f"PUT /api/ai-settings/{settings_id} (报警设置)", response)
    
    # 6. 获取所有摄像头
    print("\n6️⃣ 获取所有摄像头")
    response = requests.get(f"{BASE_URL}/api/cameras")
    print_response("GET /api/cameras", response)
    
    cameras = response.json() if response.status_code == 200 else []
    
    # 7. 绑定摄像头（如果有摄像头）
    if cameras:
        camera_id = cameras[0]['id']
        print(f"\n7️⃣ 绑定摄像头 {camera_id}")
        response = requests.post(
            f"{BASE_URL}/api/ai-settings/{settings_id}/bind-camera/{camera_id}"
        )
        print_response(f"POST /api/ai-settings/{settings_id}/bind-camera/{camera_id}", response)
        
        # 8. 解绑摄像头
        print(f"\n8️⃣ 解绑摄像头")
        response = requests.post(
            f"{BASE_URL}/api/ai-settings/{settings_id}/unbind-camera"
        )
        print_response(f"POST /api/ai-settings/{settings_id}/unbind-camera", response)
    else:
        print("\n⚠️ 没有可用的摄像头，跳过绑定测试")
    
    # 9. 最终获取完整设置
    print("\n9️⃣ 获取最终的完整设置")
    response = requests.get(f"{BASE_URL}/api/ai-settings")
    print_response("GET /api/ai-settings (最终)", response)
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)

if __name__ == "__main__":
    try:
        test_ai_settings()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务")
        print("请确保后端服务正在运行: python backend/src/main.py")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
