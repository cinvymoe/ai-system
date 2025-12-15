"""
修复摄像头方向命名

将数据库中的方向值从旧格式转换为新格式：
- left -> turn_left
- right -> turn_right
"""

import sys
sys.path.insert(0, 'src')

from src.database import get_db
from src.models.camera import Camera


def fix_directions():
    """修复方向命名"""
    
    # 方向映射
    direction_mapping = {
        'left': 'turn_left',
        'right': 'turn_right',
        # 其他方向保持不变
        'forward': 'forward',
        'backward': 'backward',
        'stationary': 'stationary',
    }
    
    db = next(get_db())
    
    try:
        cameras = db.query(Camera).all()
        
        print("=" * 70)
        print("修复摄像头方向命名")
        print("=" * 70)
        
        updated_count = 0
        
        for camera in cameras:
            if not camera.directions:
                continue
            
            # 转换方向
            old_directions = camera.directions.copy()
            new_directions = []
            
            for direction in old_directions:
                new_direction = direction_mapping.get(direction, direction)
                new_directions.append(new_direction)
            
            # 检查是否有变化
            if old_directions != new_directions:
                print(f"\n摄像头: {camera.name} (ID: {camera.id})")
                print(f"  旧方向: {old_directions}")
                print(f"  新方向: {new_directions}")
                
                camera.directions = new_directions
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"\n✓ 已更新 {updated_count} 个摄像头的方向配置")
        else:
            print("\n✓ 所有摄像头的方向配置都是正确的，无需更新")
        
        # 显示最终配置
        print("\n" + "=" * 70)
        print("当前摄像头配置")
        print("=" * 70)
        
        cameras = db.query(Camera).all()
        for camera in cameras:
            print(f"\n{camera.name}:")
            print(f"  ID: {camera.id}")
            print(f"  URL: {camera.url}")
            print(f"  方向: {camera.directions}")
            print(f"  状态: {camera.status}")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    fix_directions()
