"""Camera monitoring scheduler for automatic status checks."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
    from services.camera_service import CameraService
    from repositories.camera_repository import CameraRepository
except ImportError:
    from src.database import SessionLocal
    from src.services.camera_service import CameraService
    from src.repositories.camera_repository import CameraRepository

logger = logging.getLogger(__name__)


class CameraMonitor:
    """Background monitor for checking camera online status."""
    
    def __init__(self, check_interval_minutes: int = 5):
        """Initialize the camera monitor.
        
        Args:
            check_interval_minutes: Interval between status checks in minutes (default: 5)
        """
        self.scheduler = BackgroundScheduler()
        self.check_interval_minutes = check_interval_minutes
        self.is_running = False
        self.last_check_time = None
        self.check_count = 0
        
        logger.info(f"Camera monitor initialized with {check_interval_minutes} minute interval")
    
    def check_cameras_status(self):
        """Check status of all cameras and update database."""
        try:
            logger.info("Starting scheduled camera status check...")
            self.check_count += 1
            
            # Create database session
            db: Session = SessionLocal()
            
            try:
                # Create service instance
                repository = CameraRepository(db)
                service = CameraService(repository)
                
                # Check all cameras
                result = service.check_all_cameras_status()
                
                self.last_check_time = datetime.now()
                
                logger.info(
                    f"Camera status check #{self.check_count} completed: "
                    f"{result['online_count']}/{result['total_cameras']} online, "
                    f"{result['status_changed_count']} status changed"
                )
                
                # Log any offline cameras
                for camera in result['cameras']:
                    if not camera.get('is_online', False):
                        logger.warning(
                            f"Camera offline: {camera['camera_name']} ({camera['camera_id']}) - {camera['url']}"
                        )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error during scheduled camera status check: {e}", exc_info=True)
    
    def start(self):
        """Start the camera monitoring scheduler."""
        if self.is_running:
            logger.warning("Camera monitor is already running")
            return
        
        try:
            # Add job to scheduler
            self.scheduler.add_job(
                func=self.check_cameras_status,
                trigger=IntervalTrigger(minutes=self.check_interval_minutes),
                id='camera_status_check',
                name='Check camera online status',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Camera monitor started - checking every {self.check_interval_minutes} minutes")
            
            # Run initial check immediately
            self.check_cameras_status()
            
        except Exception as e:
            logger.error(f"Failed to start camera monitor: {e}")
            raise
    
    def stop(self):
        """Stop the camera monitoring scheduler."""
        if not self.is_running:
            logger.warning("Camera monitor is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Camera monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping camera monitor: {e}")
    
    def get_status(self) -> dict:
        """Get current status of the monitor.
        
        Returns:
            Dictionary with monitor status information
        """
        return {
            "is_running": self.is_running,
            "check_interval_minutes": self.check_interval_minutes,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "total_checks": self.check_count,
            "next_check_time": self._get_next_check_time()
        }
    
    def _get_next_check_time(self) -> str:
        """Get the next scheduled check time."""
        if not self.is_running:
            return None
        
        try:
            job = self.scheduler.get_job('camera_status_check')
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        except Exception:
            pass
        
        return None


# Global monitor instance
_monitor_instance = None


def get_camera_monitor(check_interval_minutes: int = 5) -> CameraMonitor:
    """Get or create the global camera monitor instance.
    
    Args:
        check_interval_minutes: Interval between checks (only used on first call)
        
    Returns:
        CameraMonitor instance
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = CameraMonitor(check_interval_minutes)
    
    return _monitor_instance
