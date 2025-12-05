"""Scheduler package for background tasks."""
from .camera_monitor import CameraMonitor, get_camera_monitor

__all__ = ['CameraMonitor', 'get_camera_monitor']
