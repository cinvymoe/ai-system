"""Person detection scheduler - Backward compatibility layer.

This module re-exports all components from the refactored detection package
to maintain backward compatibility with existing code.

The actual implementation has been split into:
- detection/constants.py: Detection parameters and constants
- detection/detector.py: PersonDetector class
- detection/monitor.py: PersonDetectionMonitor class
- detection/frame_storage.py: Global frame storage functions
- detection/factory.py: Factory functions and broker callback
"""

# Re-export all public APIs for backward compatibility
from .detection.constants import (
    OBJ_THRESH,
    NMS_THRESH,
    IMG_SIZE,
    PERSON_CLASS_ID,
    DEFAULT_ANCHORS,
)

from .detection.detector import PersonDetector

from .detection.monitor import PersonDetectionMonitor

from .detection.frame_storage import (
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

from .detection.factory import (
    get_person_detection_monitor,
    _broker_person_detection_callback,
)

# For backward compatibility with direct access to global variables
# These are now functions that return the actual storage
_global_frames = get_global_frames()
_global_drawn_frames = get_global_drawn_frames()
_frame_locks = get_frame_locks()
_frame_timestamps = get_frame_timestamps()
_detection_results = get_detection_results()

__all__ = [
    # Constants
    'OBJ_THRESH',
    'NMS_THRESH',
    'IMG_SIZE',
    'PERSON_CLASS_ID',
    'DEFAULT_ANCHORS',
    # Classes
    'PersonDetector',
    'PersonDetectionMonitor',
    # Frame storage functions
    'read_latest_frame',
    'read_latest_drawn_frame',
    'get_frame_info',
    'clear_frame_storage',
    # Factory
    'get_person_detection_monitor',
    '_broker_person_detection_callback',
    # Global variables (for backward compatibility)
    '_global_frames',
    '_global_drawn_frames',
    '_frame_locks',
    '_frame_timestamps',
    '_detection_results',
]
