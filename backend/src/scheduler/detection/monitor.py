"""PersonDetectionMonitor class - Background monitor for person detection."""

import logging
import time
import threading
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
    from services.camera_service import CameraService
    from repositories.camera_repository import CameraRepository
    from utils.rts_capture import RTSCapture
except ImportError:
    from src.database import SessionLocal
    from src.services.camera_service import CameraService
    from src.repositories.camera_repository import CameraRepository
    from src.utils.rts_capture import RTSCapture

from .detector import PersonDetector
from .frame_storage import store_frame, ensure_lock

logger = logging.getLogger(__name__)


class PersonDetectionMonitor:
    """Background monitor for person detection on camera streams."""
    
    def __init__(self, model_path: str, check_interval_seconds: float = 0.1, 
                 anchors: Optional[List] = None, target: str = 'rk3576', 
                 device_id: Optional[str] = None):
        """Initialize the person detection monitor.
        
        Args:
            model_path: Path to YOLOv5 model file
            check_interval_seconds: Interval between detection runs in seconds (default: 0.1)
            anchors: Custom anchors (optional)
            target: Target RKNPU platform (default: rk3576)
            device_id: Device ID for RKNN (optional)
        """
        self.check_interval_seconds = check_interval_seconds
        self.is_running = False
        self.last_check_time = None
        self.detection_count = 0
        self.total_persons_detected = 0
        
        # Store initialization parameters
        self.model_path = model_path
        self.anchors = anchors
        self.target = target
        self.device_id = device_id
        self.detector = None
        
        # Camera and capture setup
        self.camera = None
        self.cap = None
        
        # Thread for background detection
        self._detection_thread = None
        self._stop_event = threading.Event()
        
        # Callback system for person detection alerts
        self.person_detection_callbacks = []
        
        # Track if callback has been triggered (only trigger once)
        self._callback_triggered = False
    
    def add_person_detection_callback(self, callback):
        """Add a callback function to be called when persons are detected.
        
        Args:
            callback: Function that takes (camera_info, detections, timestamp) as parameters
        """
        if callback not in self.person_detection_callbacks:
            self.person_detection_callbacks.append(callback)
            logger.info(f"Added person detection callback: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}")
    
    def remove_person_detection_callback(self, callback):
        """Remove a callback function from person detection alerts.
        
        Args:
            callback: Function to remove
        """
        if callback in self.person_detection_callbacks:
            self.person_detection_callbacks.remove(callback)
            logger.info(f"Removed person detection callback: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}")
    
    def _trigger_person_detection_callbacks(self, camera_info, detections, timestamp):
        """Trigger all registered callbacks when persons are detected.
        
        Args:
            camera_info: Dictionary with camera information
            detections: List of person detection results
            timestamp: Detection timestamp
        """
        if not self.person_detection_callbacks:
            return
        
        for callback in self.person_detection_callbacks:
            try:
                callback(camera_info, detections, timestamp)
            except Exception as e:
                logger.error(f"Error in person detection callback {callback}: {e}", exc_info=True)
    
    def detect_on_cameras(self):
        """Run person detection on pre-initialized camera."""
        if self.detector is None or self.camera is None or self.cap is None:
            logger.warning("Detector, camera, or capture not initialized, skipping detection")
            return
        
        try:
            self.detection_count += 1
            
            ret, frame = self.cap.read_latest_frame()
            
            if not ret or frame is None:
                logger.warning(f"Failed to capture frame from camera {self.camera.name}")
                return
            
            camera_id = str(self.camera.id)
            ensure_lock(camera_id)
            
            drawn_frame, detections = self.detector.detect_and_draw(frame, draw_all=False)
            
            # Store frames using frame_storage module
            store_frame(camera_id, frame, drawn_frame, datetime.now(), detections)
            
            persons = [d for d in detections if d.get('class') == 'person']
            
            if persons:
                self.total_persons_detected += len(persons)
                detection_timestamp = datetime.now()
                
                logger.info(
                    f"Detected {len(persons)} person(s) on camera "
                    f"{self.camera.name} ({self.camera.id})"
                )
                
                self._trigger_person_detection_callbacks(
                    camera_info=self.camera.model_dump(),
                    detections=persons,
                    timestamp=detection_timestamp
                )
            else:
                logger.debug(f"No persons detected on camera {self.camera.name}")
            
            self.last_check_time = datetime.now()
            
            logger.debug(f"Person detection #{self.detection_count} completed")
                
        except Exception as e:
            logger.error(f"Error during scheduled person detection: {e}", exc_info=True)
    
    def _detection_loop(self):
        """Background thread loop for continuous detection."""
        logger.info("Detection thread started")
        
        while not self._stop_event.is_set():
            self.detect_on_cameras()
            time.sleep(self.check_interval_seconds)
        
        logger.info("Detection thread stopped")
    
    def start(self):
        """Start the person detection scheduler."""
        if self.is_running:
            logger.warning("Person detection monitor is already running")
            return
        
        # Initialize detector
        if self.detector is None:
            try:
                self.detector = PersonDetector(
                    model_path=self.model_path,
                    anchors=self.anchors,
                    target=self.target,
                    device_id=self.device_id
                )
                logger.info(f"Person detection monitor initialized with {self.check_interval_seconds}s interval")
            except Exception as e:
                logger.error(f"Failed to initialize detector: {e}")
                return
        
        # Initialize camera and capture
        try:
            logger.info("Starting scheduled person detection...")
            
            db: Session = SessionLocal()
            
            try:
                from src.services.ai_settings_service import AISettingsService
                ai_service = AISettingsService(db)
                ai_settings = ai_service.get_settings()
                
                if not ai_settings or not ai_settings.camera_id:
                    logger.info("No camera bound in AI settings, skipping detection")
                    return
                
                # 检查 AI 检测是否启用
                if not ai_settings.enabled:
                    logger.info("AI detection is disabled in settings, skipping detection")
                    return
                
                repository = CameraRepository(db)
                service = CameraService(repository)
                camera = service.get_camera_by_id(ai_settings.camera_id)
                
                if not camera:
                    logger.warning(f"Bound camera {ai_settings.camera_id} not found")
                    return
                
                if camera.status != "online":
                    logger.info(f"Bound camera {camera.name} is offline, skipping detection")
                    return
                
                self.camera = camera
                
                rtsp_url = camera.url
                if not rtsp_url:
                    logger.warning("Camera has no RTSP URL")
                    return
                
                cap = RTSCapture.create(rtsp_url)
                
                if not cap.isOpened():
                    logger.warning(f"Failed to open stream: {rtsp_url}")
                    return
                
                cap.start_read()
                self.cap = cap
                
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Failed to initialize camera setup: {e}")
            return
        
        try:
            self._stop_event.clear()
            self._detection_thread = threading.Thread(
                target=self._detection_loop,
                name="PersonDetectionThread",
                daemon=True
            )
            self._detection_thread.start()
            self.is_running = True
            
            logger.info(f"Person detection monitor started - running every {self.check_interval_seconds}s")
            
        except Exception as e:
            logger.error(f"Failed to start person detection monitor: {e}")
            raise
    
    def stop(self):
        """Stop the person detection scheduler."""
        if not self.is_running:
            logger.warning("Person detection monitor is not running")
            return
        
        try:
            self._stop_event.set()
            
            if self._detection_thread is not None:
                self._detection_thread.join(timeout=2.0)
                self._detection_thread = None
            
            if self.cap is not None:
                self.cap.stop_read()
                self.cap.release()
                self.cap = None
            
            self.camera = None
            
            self.is_running = False
            logger.info("Person detection monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping person detection monitor: {e}")
    
    def get_status(self) -> dict:
        """Get current status of the monitor.
        
        Returns:
            Dictionary with monitor status information
        """
        return {
            "is_running": self.is_running,
            "check_interval_seconds": self.check_interval_seconds,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "total_detections": self.detection_count,
            "total_persons_detected": self.total_persons_detected,
            "detector_initialized": self.detector is not None,
            "next_check_time": self._get_next_check_time()
        }
    
    def _get_next_check_time(self) -> Optional[str]:
        """Get the next scheduled detection time."""
        if not self.is_running:
            return None
        return None
