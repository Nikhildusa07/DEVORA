from fastapi import APIRouter

from app.services.monitoring_service import (
    MonitoringService
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"]
)

service = MonitoringService()


@router.get("/health")
def health_check():

    return service.get_health()