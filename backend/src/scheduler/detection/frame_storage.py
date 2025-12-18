"""Global frame storage for person detection results."""

import logging
import threading
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

# Global frame storage for each camera
_global_frames: Dict[str, np.ndarray] = {}  # Original frames
_global_drawn_frames: Dict[str, np.ndarray] = {}  # Frames with detection drawings
_frame_locks: Dict[str, threading.Lock] = {}
_frame_timestamps: Dict[str, datetime] = {}
_detection_results: Dict[str, List[Dict]] = {}  # Store detection results


def get_global_frames() -> Dict[str, np.ndarray]:
    """Get reference to global frames storage."""
    return _global_frames


def get_global_drawn_frames() -> Dict[str, np.ndarray]:
    """Get reference to global drawn frames storage."""
    return _global_drawn_frames


def get_frame_locks() -> Dict[str, threading.Lock]:
    """Get reference to frame locks."""
    return _frame_locks


def get_frame_timestamps() -> Dict[str, datetime]:
    """Get reference to frame timestamps."""
    return _frame_timestamps


def get_detection_results() -> Dict[str, List[Dict]]:
    """Get reference to detection results."""
    return _detection_results


def ensure_lock(camera_id: str) -> threading.Lock:
    """Ensure a lock exists for the given camera ID."""
    if camera_id not in _frame_locks:
        _frame_locks[camera_id] = threading.Lock()
    return _frame_locks[camera_id]


def store_frame(camera_id: str, frame: np.ndarray, drawn_frame: np.ndarray, 
                timestamp: datetime, detections: List[Dict]):
    """Store frame data for a camera.
    
    Args:
        camera_id: Camera ID
        frame: Original frame
        drawn_frame: Frame with detection drawings
        timestamp: Capture timestamp
        detections: Detection results
    """
    camera_id = str(camera_id)
    lock = ensure_lock(camera_id)
    
    with lock:
        _global_frames[camera_id] = frame.copy()
        _global_drawn_frames[camera_id] = drawn_frame.copy()
        _frame_timestamps[camera_id] = timestamp
        _detection_results[camera_id] = detections.copy()


def read_latest_frame(camera_id: str, with_drawings: bool = True) -> Tuple[bool, Optional[np.ndarray], Optional[datetime], Optional[List[Dict]]]:
    """Read the latest frame from global frame storage - defaults to drawn frames.
    
    Args:
        camera_id: Camera ID to read frame from
        with_drawings: If True, return frame with detection drawings; if False, return original frame
        
    Returns:
        Tuple of (success, frame, timestamp, detections)
    """
    camera_id = str(camera_id)
    
    frame_storage = _global_drawn_frames if with_drawings else _global_frames
    
    if camera_id not in frame_storage:
        logger.debug(f"No {'drawn' if with_drawings else 'original'} frames stored for camera {camera_id}")
        return False, None, None, None
    
    lock = ensure_lock(camera_id)
    
    try:
        with lock:
            frame = frame_storage[camera_id]
            timestamp = _frame_timestamps.get(camera_id)
            detections = _detection_results.get(camera_id) if with_drawings else None
            
            if frame is None:
                logger.debug(f"Frame is None for camera {camera_id}")
                return False, None, None, None
            
            return True, frame.copy(), timestamp, detections.copy() if detections else None
            
    except Exception as e:
        logger.error(f"Error reading latest frame for camera {camera_id}: {e}")
        return False, None, None, None


def read_latest_drawn_frame(camera_id: str) -> Tuple[bool, Optional[np.ndarray], Optional[datetime], Optional[List[Dict]]]:
    """Read the latest frame with detection drawings from global frame storage.
    
    Args:
        camera_id: Camera ID to read frame from
        
    Returns:
        Tuple of (success, frame, timestamp, detections)
    """
    return read_latest_frame(camera_id, with_drawings=True)


def get_frame_info(camera_id: str) -> Dict:
    """Get information about stored frame for a camera.
    
    Args:
        camera_id: Camera ID to get info for
        
    Returns:
        Dictionary with frame information
    """
    camera_id = str(camera_id)
    
    info = {
        "camera_id": camera_id,
        "has_original_frame": camera_id in _global_frames,
        "has_drawn_frame": camera_id in _global_drawn_frames,
        "has_detections": camera_id in _detection_results,
        "timestamp": None,
        "frame_shape": None,
        "age_seconds": None,
        "detection_count": 0,
        "person_count": 0
    }
    
    if camera_id in _global_frames and camera_id in _frame_timestamps:
        try:
            lock = ensure_lock(camera_id)
            with lock:
                frame = _global_frames.get(camera_id)
                timestamp = _frame_timestamps.get(camera_id)
                detections = _detection_results.get(camera_id, [])
                
                if frame is not None:
                    info["frame_shape"] = frame.shape
                
                if timestamp is not None:
                    info["timestamp"] = timestamp.isoformat()
                    info["age_seconds"] = (datetime.now() - timestamp).total_seconds()
                
                if detections:
                    info["detection_count"] = len(detections)
                    info["person_count"] = len([d for d in detections if d.get('class') == 'person'])
                    
        except Exception as e:
            logger.error(f"Error getting frame info for camera {camera_id}: {e}")
    
    return info


def clear_frame_storage(camera_id: Optional[str] = None):
    """Clear frame storage for a specific camera or all cameras.
    
    Args:
        camera_id: Camera ID to clear, or None to clear all
    """
    global _global_frames, _global_drawn_frames, _frame_timestamps, _detection_results
    
    if camera_id is not None:
        camera_id = str(camera_id)
        if camera_id in _frame_locks:
            with _frame_locks[camera_id]:
                _global_frames.pop(camera_id, None)
                _global_drawn_frames.pop(camera_id, None)
                _frame_timestamps.pop(camera_id, None)
                _detection_results.pop(camera_id, None)
        logger.info(f"Cleared frame storage for camera {camera_id}")
    else:
        for cid in list(_frame_locks.keys()):
            with _frame_locks[cid]:
                _global_frames.pop(cid, None)
                _global_drawn_frames.pop(cid, None)
                _frame_timestamps.pop(cid, None)
                _detection_results.pop(cid, None)
        logger.info("Cleared all frame storage")
