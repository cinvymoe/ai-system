"""Factory functions for person detection module."""

import logging
from typing import Optional, List

from .monitor import PersonDetectionMonitor

logger = logging.getLogger(__name__)

# Global monitor instance
_detection_monitor_instance = None


def _broker_person_detection_callback(camera_info, detections, timestamp):
    """Callback function to publish person detection alerts to message broker.
    
    Args:
        camera_info: Dictionary with camera information
        detections: List of person detection results
        timestamp: Detection timestamp
    """
    try:
        try:
            from broker.broker import MessageBroker
        except ImportError:
            from src.broker.broker import MessageBroker
        
        broker = MessageBroker.get_instance()
        
        person_count = len(detections)
        severity = "high" if person_count > 1 else "medium"
        
        alert_data = {
            "alert_type": "person_detected",
            "severity": severity,
            "camera_id": camera_info.get('id'),
            "camera_name": camera_info.get('name', 'Unknown'),
            "person_count": person_count,
            "detections": detections,
            "timestamp": timestamp.isoformat(),
            "confidence": max([d.get('score', 0) for d in detections]) if detections else 0
        }
        
        result = broker.publish("ai_alert", alert_data)
        
        if result.success:
            logger.info(f"Published person detection alert to broker: {len(detections)} person(s) on camera {camera_info.get('camera_name')}")
        else:
            logger.warning(f"Failed to publish person detection alert to broker: {result.errors}")
            
    except Exception as e:
        logger.error(f"Error in broker person detection callback: {e}", exc_info=True)


def get_person_detection_monitor(model_path: str, check_interval_seconds: int = 30,
                                anchors: Optional[List] = None, target: str = 'rk3576',
                                device_id: Optional[str] = None, 
                                enable_broker_alerts: bool = True) -> PersonDetectionMonitor:
    """Get or create the global person detection monitor instance.
    
    Args:
        model_path: Path to YOLOv5 model file
        check_interval_seconds: Interval between detections (only used on first call)
        anchors: Custom anchors (optional, only used on first call)
        target: Target RKNPU platform (default: rk3576, only used on first call)
        device_id: Device ID for RKNN (optional, only used on first call)
        enable_broker_alerts: Whether to enable broker alerts (default: True)
        
    Returns:
        PersonDetectionMonitor instance
    """
    global _detection_monitor_instance
    
    if _detection_monitor_instance is None:
        _detection_monitor_instance = PersonDetectionMonitor(
            model_path=model_path,
            check_interval_seconds=check_interval_seconds,
            anchors=anchors,
            target=target,
            device_id=device_id
        )
        
        if enable_broker_alerts:
            _detection_monitor_instance.add_person_detection_callback(_broker_person_detection_callback)
    
    return _detection_monitor_instance
