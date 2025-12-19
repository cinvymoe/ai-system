#!/usr/bin/env python3
"""迁移脚本：为 ai_settings 表添加 enabled 字段"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import engine
from sqlalchemy import text


def main():
    """添加 enabled 字段到 ai_settings 表"""
    print("🔧 检查 ai_settings 表结构...")

    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(ai_settings)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"当前列: {columns}")

        if "enabled" not in columns:
            print("添加 enabled 列...")
            conn.execute(
                text("ALTER TABLE ai_settings ADD COLUMN enabled BOOLEAN DEFAULT 1")
            )
            conn.commit()
            print("✅ enabled 列添加成功！")
        else:
            print("✅ enabled 列已存在")


if __name__ == "__main__":
    main()
