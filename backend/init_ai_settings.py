#!/usr/bin/env python3
"""初始化 AI 设置数据库表"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database import init_db, SessionLocal
from src.models.ai_settings import AISettings

def main():
    """初始化 AI 设置表"""
    print("🔧 初始化 AI 设置数据库表...")
    
    # 创建表
    init_db()
    print("✅ 数据库表创建成功")
    
    # 检查是否已有默认设置
    db = SessionLocal()
    try:
        existing = db.query(AISettings).first()
        if existing:
            print(f"ℹ️ 已存在 AI 设置 (ID: {existing.id})")
        else:
            # 创建默认设置
            default_settings = AISettings(
                confidence_threshold=75.0,
                sound_alarm=True,
                visual_alarm=True,
                auto_screenshot=True,
                alarm_cooldown=5
            )
            db.add(default_settings)
            db.commit()
            db.refresh(default_settings)
            print(f"✅ 创建默认 AI 设置 (ID: {default_settings.id})")
            print(f"   - 置信度阈值: {default_settings.confidence_threshold}%")
            print(f"   - 声音报警: {default_settings.sound_alarm}")
            print(f"   - 视觉报警: {default_settings.visual_alarm}")
            print(f"   - 自动截图: {default_settings.auto_screenshot}")
            print(f"   - 报警冷却: {default_settings.alarm_cooldown}秒")
    finally:
        db.close()
    
    print("\n✅ AI 设置初始化完成！")

if __name__ == "__main__":
    main()
