"""
消息处理器测试

测试各种消息类型处理器的验证和处理逻辑。
"""

import pytest
from datetime import datetime

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.broker.handlers import (
    DirectionMessageHandler,
    AngleMessageHandler,
    AIAlertMessageHandler,
)


class TestDirectionMessageHandler:
    """测试方向消息处理器"""
    
    @pytest.fixture
    def handler(self):
        return DirectionMessageHandler()
    
    def test_valid_commands(self, handler):
        """测试所有有效的方向命令"""
        valid_commands = ['forward', 'backward', 'turn_left', 'turn_right', 'stationary']
        
        for command in valid_commands:
            data = {
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
            result = handler.validate(data)
            assert result.valid is True, f"Command '{command}' should be valid"
            assert len(result.errors) == 0
    
    def test_invalid_command(self, handler):
        """测试无效的方向命令"""
        data = {
            'command': 'invalid_command',
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('Invalid command' in err for err in result.errors)
    
    def test_missing_command(self, handler):
        """测试缺少命令字段"""
        data = {
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('command' in err.lower() for err in result.errors)
    
    def test_missing_timestamp_warning(self, handler):
        """测试缺少时间戳会产生警告"""
        data = {
            'command': 'forward'
        }
        result = handler.validate(data)
        assert result.valid is True
        assert any('timestamp' in warn.lower() for warn in result.warnings)
    
    def test_optional_intensity(self, handler):
        """测试可选的强度字段"""
        data = {
            'command': 'forward',
            'timestamp': datetime.now().isoformat(),
            'intensity': 0.8
        }
        result = handler.validate(data)
        assert result.valid is True
    
    def test_negative_intensity_warning(self, handler):
        """测试负强度值会产生警告"""
        data = {
            'command': 'forward',
            'timestamp': datetime.now().isoformat(),
            'intensity': -0.5
        }
        result = handler.validate(data)
        assert result.valid is True
        assert any('intensity' in warn.lower() for warn in result.warnings)
    
    def test_process_message(self, handler):
        """测试处理消息"""
        data = {
            'command': 'forward',
            'timestamp': datetime.now().isoformat(),
            'intensity': 0.8,
            'angular_intensity': 0.3
        }
        processed = handler.process(data)
        
        assert processed.validated is True
        assert processed.original.type == 'direction_result'
        assert processed.original.data['command'] == 'forward'
        assert processed.original.data['intensity'] == 0.8
    
    def test_process_with_defaults(self, handler):
        """测试处理消息时使用默认值"""
        data = {
            'command': 'forward'
        }
        processed = handler.process(data)
        
        assert processed.original.data['intensity'] == 0.0
        assert processed.original.data['angular_intensity'] == 0.0
        assert 'timestamp' in processed.original.data
    
    def test_get_type_name(self, handler):
        """测试获取类型名称"""
        assert handler.get_type_name() == 'direction_result'


class TestAngleMessageHandler:
    """测试角度消息处理器"""
    
    @pytest.fixture
    def handler(self):
        return AngleMessageHandler()
    
    def test_valid_angles(self, handler):
        """测试有效的角度值"""
        valid_angles = [0, 45, 90, 180, 270, 360, -90, -180]
        
        for angle in valid_angles:
            data = {
                'angle': angle,
                'timestamp': datetime.now().isoformat()
            }
            result = handler.validate(data)
            assert result.valid is True, f"Angle {angle} should be valid"
            assert len(result.errors) == 0
    
    def test_out_of_range_angles(self, handler):
        """测试超出范围的角度值"""
        invalid_angles = [-181, 361, 500, -200]
        
        for angle in invalid_angles:
            data = {
                'angle': angle,
                'timestamp': datetime.now().isoformat()
            }
            result = handler.validate(data)
            assert result.valid is False, f"Angle {angle} should be invalid"
            assert any('out of valid range' in err for err in result.errors)
    
    def test_missing_angle(self, handler):
        """测试缺少角度字段"""
        data = {
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('angle' in err.lower() for err in result.errors)
    
    def test_invalid_angle_type(self, handler):
        """测试无效的角度类型"""
        data = {
            'angle': 'not_a_number',
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('invalid' in err.lower() for err in result.errors)
    
    def test_missing_timestamp_warning(self, handler):
        """测试缺少时间戳会产生警告"""
        data = {
            'angle': 45
        }
        result = handler.validate(data)
        assert result.valid is True
        assert any('timestamp' in warn.lower() for warn in result.warnings)
    
    def test_process_message(self, handler):
        """测试处理消息"""
        data = {
            'angle': 45.5,
            'timestamp': datetime.now().isoformat()
        }
        processed = handler.process(data)
        
        assert processed.validated is True
        assert processed.original.type == 'angle_value'
        assert processed.original.data['angle'] == 45.5
    
    def test_process_with_default_timestamp(self, handler):
        """测试处理消息时使用默认时间戳"""
        data = {
            'angle': 90
        }
        processed = handler.process(data)
        
        assert 'timestamp' in processed.original.data
    
    def test_get_type_name(self, handler):
        """测试获取类型名称"""
        assert handler.get_type_name() == 'angle_value'
    
    def test_float_conversion(self, handler):
        """测试角度值会被转换为浮点数"""
        data = {
            'angle': 45,  # 整数
            'timestamp': datetime.now().isoformat()
        }
        processed = handler.process(data)
        
        assert isinstance(processed.original.data['angle'], float)
        assert processed.original.data['angle'] == 45.0


class TestAIAlertMessageHandler:
    """测试 AI 报警消息处理器"""
    
    @pytest.fixture
    def handler(self):
        return AIAlertMessageHandler()
    
    def test_valid_severities(self, handler):
        """测试所有有效的严重程度"""
        valid_severities = ['low', 'medium', 'high', 'critical']
        
        for severity in valid_severities:
            data = {
                'alert_type': 'intrusion',
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            result = handler.validate(data)
            assert result.valid is True, f"Severity '{severity}' should be valid"
            assert len(result.errors) == 0
    
    def test_invalid_severity(self, handler):
        """测试无效的严重程度"""
        data = {
            'alert_type': 'intrusion',
            'severity': 'invalid_severity',
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('Invalid severity' in err for err in result.errors)
    
    def test_missing_alert_type(self, handler):
        """测试缺少报警类型"""
        data = {
            'severity': 'high',
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('alert_type' in err.lower() for err in result.errors)
    
    def test_missing_severity(self, handler):
        """测试缺少严重程度"""
        data = {
            'alert_type': 'intrusion',
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is False
        assert any('severity' in err.lower() for err in result.errors)
    
    def test_placeholder_warning(self, handler):
        """测试会产生占位符实现警告"""
        data = {
            'alert_type': 'intrusion',
            'severity': 'high',
            'timestamp': datetime.now().isoformat()
        }
        result = handler.validate(data)
        assert result.valid is True
        assert any('placeholder' in warn.lower() for warn in result.warnings)
    
    def test_process_message(self, handler):
        """测试处理消息"""
        data = {
            'alert_type': 'intrusion',
            'severity': 'high',
            'timestamp': datetime.now().isoformat(),
            'metadata': {'location': 'entrance'}
        }
        processed = handler.process(data)
        
        assert processed.validated is True
        assert processed.original.type == 'ai_alert'
        assert processed.original.data['alert_type'] == 'intrusion'
        assert processed.original.data['severity'] == 'high'
        assert processed.original.data['metadata'] == {'location': 'entrance'}
    
    def test_process_with_defaults(self, handler):
        """测试处理消息时使用默认值"""
        data = {
            'alert_type': 'intrusion',
            'severity': 'high'
        }
        processed = handler.process(data)
        
        assert 'timestamp' in processed.original.data
        assert processed.original.data['metadata'] == {}
    
    def test_get_type_name(self, handler):
        """测试获取类型名称"""
        assert handler.get_type_name() == 'ai_alert'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
