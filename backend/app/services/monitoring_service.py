from datetime import datetime
import platform


class MonitoringService:

    def get_health(self):

        return {
            "system": "DEVORA",
            "status": "healthy",
            "service": "FastAPI",
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "application": "healthy",
                "api": "healthy",
                "runtime": "healthy"
            },
            "next_stage": "regression_detection"
        }