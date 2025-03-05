from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from app.services.monitoring_service import monitoring_service, SystemMetrics, Alert, ServiceStatus
from app.services.auth_service import get_current_user, require_role
import logging

router = APIRouter(tags=["monitoring"])

# Get logger for this module
logger = logging.getLogger(__name__)

class AlertRequest(BaseModel):
    """Schema for creating alerts"""
    type: str
    severity: str
    message: str

class AlertAcknowledgement(BaseModel):
    """Schema for acknowledging alerts"""
    comment: str

class AlertResolution(BaseModel):
    """Schema for resolving alerts"""
    resolution_note: str

@router.get("/monitoring/health",
    summary="Get system health status",
    description="Returns the current health status of the system and its components",
    response_description="System health information",
    responses={
        200: {
            "description": "System health retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-03-05T12:00:00Z",
                        "services": {
                            "database": "up",
                            "redis": "up",
                            "api": "up"
                        },
                        "metrics": {
                            "cpu_usage": 45.2,
                            "memory_usage": 62.8,
                            "disk_usage": 73.1,
                            "active_connections": 15,
                            "response_time": 150,
                            "error_rate": 0.5
                        }
                    }
                }
            }
        }
    }
)
async def get_health():
    """Get system health status"""
    try:
        health_data = await monitoring_service.get_system_health()
        
        # Handle Redis status specially
        if "redis" in health_data["services"]:
            redis_status = health_data["services"]["redis"]
            # If Redis is in mock mode, consider it "up" for overall health
            if redis_status == "mock":
                health_data["services"]["redis"] = "up (mock)"
        
        return health_data
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/metrics",
    summary="Get system metrics",
    description="Returns detailed system performance metrics",
    response_description="System metrics",
    responses={
        200: {
            "description": "System metrics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "current": {
                            "cpu_usage": 45.2,
                            "memory_usage": 62.8,
                            "disk_usage": 73.1,
                            "active_connections": 15,
                            "response_time": 150,
                            "error_rate": 0.5,
                            "timestamp": "2024-03-05T12:00:00Z"
                        },
                        "history": [
                            {
                                "timestamp": "2024-03-05T11:59:00Z",
                                "cpu_usage": 44.8,
                                "memory_usage": 62.5
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_metrics(
    history: bool = Query(False, description="Include historical metrics"),
    limit: int = Query(10, description="Number of historical records to return")
):
    """
    Get system metrics with optional history
    
    Args:
        history: Whether to include historical metrics
        limit: Number of historical records to return
    """
    current_metrics = await monitoring_service.get_current_metrics()
    
    response = {
        "current": current_metrics.dict()
    }
    
    if history:
        response["history"] = [
            metrics.dict() 
            for metrics in monitoring_service.metrics_history[-limit:]
        ]
    
    return response

@router.get("/monitoring/logs",
    summary="Get system logs",
    description="Returns system logs with optional filtering",
    response_description="System logs",
    responses={
        200: {
            "description": "System logs retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "timestamp": "2024-03-05T12:00:00Z",
                            "level": "INFO",
                            "message": "Application started"
                        }
                    ]
                }
            }
        }
    }
)
async def get_logs(
    level: str = Query("INFO", description="Log level filter"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    current_user: dict = Depends(require_role("support"))
):
    """
    Get system logs with filtering
    
    Args:
        level: Log level to filter by
        limit: Maximum number of logs to return
    """
    return await monitoring_service.get_system_logs(level, limit)

@router.post("/monitoring/alerts",
    summary="Create system alert",
    description="Creates a new system alert",
    response_description="Created alert",
    responses={
        200: {
            "description": "Alert created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "alert_1234567890",
                        "type": "high_cpu_usage",
                        "severity": "warning",
                        "message": "CPU usage above threshold",
                        "timestamp": "2024-03-05T12:00:00Z",
                        "resolved": False
                    }
                }
            }
        }
    }
)
async def create_alert(
    alert: AlertRequest,
    current_user: dict = Depends(require_role("support"))
):
    """
    Create a new system alert
    
    Args:
        alert: Alert details
    """
    return await monitoring_service.create_alert(
        alert.type,
        alert.severity,
        alert.message
    )

@router.get("/monitoring/alerts",
    summary="Get system alerts",
    description="Returns system alerts with optional filtering",
    response_description="System alerts",
    responses={
        200: {
            "description": "System alerts retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "alert_1234567890",
                            "type": "high_cpu_usage",
                            "severity": "warning",
                            "message": "CPU usage above threshold",
                            "timestamp": "2024-03-05T12:00:00Z",
                            "resolved": False
                        }
                    ]
                }
            }
        }
    }
)
async def get_alerts(
    type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by alert severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    current_user: dict = Depends(require_role("support"))
):
    """
    Get system alerts with filtering
    
    Args:
        type: Filter by alert type
        severity: Filter by alert severity
        resolved: Filter by resolution status
    """
    alerts = monitoring_service.alerts
    
    if type:
        alerts = [a for a in alerts if a.type == type]
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    if resolved is not None:
        alerts = [a for a in alerts if a.resolved == resolved]
    
    return alerts

@router.get("/monitoring/summary",
    summary="Get system summary",
    description="Returns a comprehensive summary of the system status",
    response_description="System summary",
    responses={
        200: {
            "description": "System summary retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "system_status": "healthy",
                        "current_metrics": {
                            "cpu_usage": 45.2,
                            "memory_usage": 62.8,
                            "disk_usage": 73.1
                        },
                        "services": {
                            "database": {"status": "up"},
                            "redis": {"status": "up"},
                            "api": {"status": "up"}
                        },
                        "active_alerts": 0,
                        "total_alerts_24h": 5,
                        "uptime": 345600,
                        "last_updated": "2024-03-05T12:00:00Z"
                    }
                }
            }
        }
    }
)
async def get_system_summary(
    current_user: dict = Depends(require_role("support"))
):
    """Get system summary"""
    try:
        summary = await monitoring_service.get_system_summary()
        
        # Handle Redis status specially
        if "services" in summary and "redis" in summary["services"]:
            redis_service = summary["services"]["redis"]
            if isinstance(redis_service, dict) and "status" in redis_service:
                # If Redis is in mock mode, consider it "up" for overall health
                if redis_service["status"] == "mock":
                    summary["services"]["redis"]["status"] = "up (mock)"
                    # Don't count mock Redis as a problem for system status
                    if summary["system_status"] == "degraded" and all(
                        service["status"] in ["up", "up (mock)"] 
                        for service_name, service in summary["services"].items() 
                        if service_name != "redis" or service["status"] != "down"
                    ):
                        summary["system_status"] = "healthy"
        
        return summary
    except Exception as e:
        logger.error(f"Error getting system summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/services",
    summary="Get service status",
    description="Returns the status of all monitored services",
    response_description="Service status information",
    responses={
        200: {
            "description": "Service status retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "database": {
                            "status": "up",
                            "last_check": "2024-03-05T12:00:00Z",
                            "response_time": 15.5
                        }
                    }
                }
            }
        }
    }
)
async def get_service_status(
    current_user: dict = Depends(require_role("support"))
):
    """Get status of all services"""
    return await monitoring_service.check_service_health()

@router.post("/monitoring/alerts/{alert_id}/acknowledge",
    summary="Acknowledge alert",
    description="Acknowledge an existing alert",
    response_description="Updated alert",
    responses={
        200: {
            "description": "Alert acknowledged successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "alert_1234567890",
                        "acknowledgement": {
                            "user_id": "user123",
                            "timestamp": "2024-03-05T12:00:00Z",
                            "comment": "Investigating the issue"
                        }
                    }
                }
            }
        }
    }
)
async def acknowledge_alert(
    alert_id: str = Path(..., description="ID of the alert to acknowledge"),
    acknowledgement: AlertAcknowledgement = None,
    current_user: dict = Depends(require_role("support"))
):
    """Acknowledge an alert"""
    return await monitoring_service.acknowledge_alert(
        alert_id,
        current_user["sub"],
        acknowledgement.comment
    )

@router.post("/monitoring/alerts/{alert_id}/resolve",
    summary="Resolve alert",
    description="Mark an alert as resolved",
    response_description="Updated alert",
    responses={
        200: {
            "description": "Alert resolved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "alert_1234567890",
                        "resolved": True,
                        "resolved_at": "2024-03-05T12:00:00Z",
                        "resolved_by": "user123",
                        "resolution_note": "Issue has been fixed"
                    }
                }
            }
        }
    }
)
async def resolve_alert(
    alert_id: str = Path(..., description="ID of the alert to resolve"),
    resolution: AlertResolution = None,
    current_user: dict = Depends(require_role("support"))
):
    """Resolve an alert"""
    return await monitoring_service.resolve_alert(
        alert_id,
        current_user["sub"],
        resolution.resolution_note
    )

@router.get("/monitoring/dashboard",
    summary="Get support dashboard data",
    description="Returns comprehensive data for the support dashboard",
    response_description="Dashboard data",
    responses={
        200: {
            "description": "Dashboard data retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "active_users": 1250,
                        "open_issues": 8,
                        "system_status": {
                            "status": "healthy",
                            "services": {
                                "database": "up",
                                "redis": "up",
                                "api": "up"
                            }
                        },
                        "avg_response_time": 120,
                        "performance_metrics": {
                            "cpu_usage": 45.2,
                            "memory_usage": 62.8,
                            "disk_usage": 73.1
                        },
                        "performance_trends": {
                            "cpu_trend": -5.2,
                            "memory_trend": 2.8,
                            "response_time_trend": -3.1
                        },
                        "error_summary": {
                            "total_errors": 15,
                            "errors_last_hour": 2,
                            "errors_last_day": 8,
                            "error_categories": {
                                "database": 5,
                                "api": 3,
                                "authentication": 7
                            }
                        },
                        "active_alerts": [
                            {
                                "id": "alert_1234567890",
                                "type": "high_cpu_usage",
                                "severity": "critical",
                                "message": "CPU usage above threshold",
                                "timestamp": "2024-03-05T12:00:00Z",
                                "component": "Database Server"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_dashboard_data(
    current_user: dict = Depends(require_role("support"))
):
    """
    Get comprehensive data for the support dashboard.
    This endpoint aggregates various monitoring metrics and statuses.
    """
    try:
        # Update user activity
        await monitoring_service.update_user_activity(current_user["sub"])
        
        # Get dashboard data
        dashboard_data = await monitoring_service.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}") 