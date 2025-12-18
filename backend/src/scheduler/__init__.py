"""Scheduler package for background tasks."""
from .camera_monitor import CameraMonitor, get_camera_monitor
from .person_detector import PersonDetectionMonitor, get_person_detection_monitor

__all__ = [
    'CameraMonitor', 
    'get_camera_monitor',
    'PersonDetectionMonitor',
    'get_person_detection_monitor'
]
