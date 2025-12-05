#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick verification script to check database data."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import SessionLocal
from models.camera import Camera
from models.angle_range import AngleRange
from models.ai_settings import AISettings

def main():
    """Verify database contains data."""
    db = SessionLocal()
    
    try:
        cameras = db.query(Camera).all()
        angle_ranges = db.query(AngleRange).all()
        ai_settings = db.query(AISettings).all()
        
        print("=" * 60)
        print("Database Verification")
        print("=" * 60)
        
        # 摄像头数据
        print(f"\n📹 Total cameras: {len(cameras)}")
        
        if cameras:
            print("\nCamera List:")
            for i, camera in enumerate(cameras, 1):
                status_icon = "🟢" if camera.status == "online" else "🔴"
                enabled_icon = "✓" if camera.enabled else "✗"
                directions_str = ", ".join(camera.directions) if camera.directions else "N/A"
                stream_type_label = "主码流" if camera.stream_type == "main" else "子码流"
                
                print(f"  {i}. {camera.name}")
                print(f"     地址: {camera.address}")
                print(f"     用户名: {camera.username}")
                print(f"     通道: {camera.channel} ({stream_type_label})")
                print(f"     方向: {directions_str}")
                print(f"     状态: {status_icon} {camera.status}")
                print(f"     启用: {enabled_icon}")
                print(f"     URL: {camera.url}")
                print()
        else:
            print("\n⚠️  No cameras found in database")
            print("Run: python src/migrate_data.py --import-sample")
        
        # 角度范围数据
        print(f"\n📐 Total angle ranges: {len(angle_ranges)}")
        
        if angle_ranges:
            print("\nAngle Range List:")
            for i, angle_range in enumerate(angle_ranges, 1):
                camera_count = len(angle_range.camera_ids) if angle_range.camera_ids else 0
                enabled_icon = "✓" if angle_range.enabled else "✗"
                
                print(f"  {i}. {angle_range.name}")
                print(f"     角度范围: {angle_range.min_angle}° - {angle_range.max_angle}°")
                print(f"     启用: {enabled_icon}")
                print(f"     绑定摄像头数: {camera_count}")
                
                if angle_range.camera_ids:
                    # 显示绑定的摄像头名称
                    bound_cameras = db.query(Camera).filter(Camera.id.in_(angle_range.camera_ids)).all()
                    if bound_cameras:
                        camera_names = [cam.name for cam in bound_cameras]
                        print(f"     摄像头: {', '.join(camera_names)}")
                print()
        else:
            print("\n⚠️  No angle ranges found in database")
            print("You can add angle ranges through the web interface")
        
        # AI 设置数据
        print(f"\n🤖 Total AI settings: {len(ai_settings)}")
        
        if ai_settings:
            print("\nAI Settings List:")
            for i, settings in enumerate(ai_settings, 1):
                print(f"  {i}. AI 设置 ID: {settings.id}")
                
                # 摄像头绑定信息
                if settings.camera_id:
                    bound_camera = db.query(Camera).filter(Camera.id == settings.camera_id).first()
                    if bound_camera:
                        print(f"     绑定摄像头: {bound_camera.name} ({settings.camera_id})")
                        print(f"     摄像头URL: {settings.camera_url}")
                    else:
                        print(f"     绑定摄像头: {settings.camera_id} (未找到)")
                else:
                    print(f"     绑定摄像头: 未绑定")
                
                # 检测参数
                print(f"     置信度阈值: {settings.confidence_threshold}%")
                
                # 区域设置
                if settings.danger_zone:
                    print(f"     危险区域: 已设置 ({len(settings.danger_zone)} 个点)")
                else:
                    print(f"     危险区域: 未设置")
                
                if settings.warning_zone:
                    print(f"     警告区域: 已设置 ({len(settings.warning_zone)} 个点)")
                else:
                    print(f"     警告区域: 未设置")
                
                # 报警设置
                alarm_features = []
                if settings.sound_alarm:
                    alarm_features.append("声音")
                if settings.visual_alarm:
                    alarm_features.append("视觉")
                if settings.auto_screenshot:
                    alarm_features.append("截图")
                
                if alarm_features:
                    print(f"     报警功能: {', '.join(alarm_features)}")
                else:
                    print(f"     报警功能: 全部关闭")
                
                print(f"     报警冷却: {settings.alarm_cooldown}秒")
                print(f"     创建时间: {settings.created_at}")
                print(f"     更新时间: {settings.updated_at}")
                print()
        else:
            print("\n⚠️  No AI settings found in database")
            print("Run: python backend/init_ai_settings.py")
        
        print("=" * 60)
        
        # 统计摘要
        print("\n📊 Summary:")
        print(f"   Cameras: {len(cameras)}")
        print(f"   Angle Ranges: {len(angle_ranges)}")
        print(f"   AI Settings: {len(ai_settings)}")
        
        # 检查数据完整性
        print("\n🔍 Data Integrity Check:")
        
        # 检查 AI 设置中的摄像头绑定
        if ai_settings:
            for settings in ai_settings:
                if settings.camera_id:
                    camera_exists = db.query(Camera).filter(Camera.id == settings.camera_id).first()
                    if not camera_exists:
                        print(f"   ⚠️  AI 设置 {settings.id} 绑定的摄像头 {settings.camera_id} 不存在")
                    else:
                        print(f"   ✓ AI 设置 {settings.id} 摄像头绑定正常")
        
        # 检查角度范围中的摄像头绑定
        if angle_ranges:
            for angle_range in angle_ranges:
                if angle_range.camera_ids:
                    for camera_id in angle_range.camera_ids:
                        camera_exists = db.query(Camera).filter(Camera.id == camera_id).first()
                        if not camera_exists:
                            print(f"   ⚠️  角度范围 '{angle_range.name}' 绑定的摄像头 {camera_id} 不存在")
        
        print("\n" + "=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
