"""Person detection module - Refactored for better organization."""

from .detector import PersonDetector
from .monitor import PersonDetectionMonitor
from .frame_storage import (
    read_latest_frame,
    read_latest_drawn_frame,
    get_frame_info,
    clear_frame_storage,
    get_global_frames,
    get_global_drawn_frames,
    get_frame_locks,
    get_frame_timestamps,
    get_detection_results,
)
from .factory import get_person_detection_monitor

__all__ = [
    # Classes
    'PersonDetector',
    'PersonDetectionMonitor',
    # Frame storage functions
    'read_latest_frame',
    'read_latest_drawn_frame',
    'get_frame_info',
    'clear_frame_storage',
    'get_global_frames',
    'get_global_drawn_frames',
    'get_frame_locks',
    'get_frame_timestamps',
    'get_detection_results',
    # Factory
    'get_person_detection_monitor',
]
