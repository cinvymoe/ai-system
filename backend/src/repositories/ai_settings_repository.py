"""AI Settings repository for database operations."""
from sqlalchemy.orm import Session
from typing import Optional, List
import json

try:
    from models.ai_settings import AISettings
    from schemas.ai_settings import AISettingsCreate, AISettingsUpdate
except ImportError:
    from src.models.ai_settings import AISettings
    from src.schemas.ai_settings import AISettingsCreate, AISettingsUpdate


class AISettingsRepository:
    """Repository for AI Settings database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_settings(self) -> Optional[AISettings]:
        """获取AI设置（只有一条记录）"""
        return self.db.query(AISettings).first()
    
    def get_by_id(self, settings_id: int) -> Optional[AISettings]:
        """根据ID获取AI设置"""
        return self.db.query(AISettings).filter(AISettings.id == settings_id).first()
    
    def create(self, settings_data: AISettingsCreate) -> AISettings:
        """创建AI设置"""
        # 转换 Point 对象为字典
        settings_dict = settings_data.model_dump()
        if settings_dict.get('danger_zone'):
            settings_dict['danger_zone'] = [point.model_dump() if hasattr(point, 'model_dump') else point 
                                           for point in settings_dict['danger_zone']]
        if settings_dict.get('warning_zone'):
            settings_dict['warning_zone'] = [point.model_dump() if hasattr(point, 'model_dump') else point 
                                            for point in settings_dict['warning_zone']]
        
        db_settings = AISettings(**settings_dict)
        self.db.add(db_settings)
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings
    
    def update(self, settings_id: int, settings_data: AISettingsUpdate) -> Optional[AISettings]:
        """更新AI设置"""
        db_settings = self.get_by_id(settings_id)
        if not db_settings:
            return None
        
        update_data = settings_data.model_dump(exclude_unset=True)
        
        # 转换 Point 对象为字典
        if 'danger_zone' in update_data and update_data['danger_zone']:
            update_data['danger_zone'] = [point.model_dump() if hasattr(point, 'model_dump') else point 
                                         for point in update_data['danger_zone']]
        if 'warning_zone' in update_data and update_data['warning_zone']:
            update_data['warning_zone'] = [point.model_dump() if hasattr(point, 'model_dump') else point 
                                          for point in update_data['warning_zone']]
        
        for key, value in update_data.items():
            setattr(db_settings, key, value)
        
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings
    
    def delete(self, settings_id: int) -> bool:
        """删除AI设置"""
        db_settings = self.get_by_id(settings_id)
        if not db_settings:
            return False
        
        self.db.delete(db_settings)
        self.db.commit()
        return True
    
    def get_or_create_default(self) -> AISettings:
        """获取或创建默认AI设置"""
        settings = self.get_settings()
        if not settings:
            default_settings = AISettingsCreate(
                confidence_threshold=75.0,
                sound_alarm=True,
                visual_alarm=True,
                auto_screenshot=True,
                alarm_cooldown=5
            )
            settings = self.create(default_settings)
        return settings
