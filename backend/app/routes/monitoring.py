from fastapi import APIRouter, HTTPException, Query, Depends, Path, Request
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.services.monitoring_service import monitoring_service, SystemMetrics, Alert, ServiceStatus
from app.services.auth_service import get_current_user, require_role
import logging
import psycopg

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

@router.get("/health",
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

@router.get("/metrics",
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
        "current": current_metrics
    }
    
    if history:
        response["history"] = [
            metrics.dict() 
            for metrics in monitoring_service.metrics_history[-limit:]
        ]
    
    return response

@router.get("/logs",
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

@router.post("/alerts",
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

@router.get("/alerts",
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

@router.get("/summary",
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

@router.get("/services",
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

@router.post("/alerts/{alert_id}/acknowledge",
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

@router.post("/alerts/{alert_id}/resolve",
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

@router.get("/dashboard",
    summary="Get dashboard data",
    description="Returns aggregated dashboard data for the support dashboard",
    response_description="Dashboard data",
    responses={
        200: {
            "description": "Dashboard data retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "active_users": 1250,
                        "user_change": 12,
                        "open_issues": 8,
                        "new_issues": 3,
                        "system_status": "Healthy",
                        "status_message": "All systems operational",
                        "avg_response_time": 120,
                        "response_time_change": -5
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
    Get aggregated dashboard data for the support dashboard
    """
    # Get system health
    health_data = await monitoring_service.get_system_health()
    
    # Determine system status
    system_status = "Healthy"
    status_message = "All systems operational"
    
    if health_data["services"]:
        services = health_data["services"].values()
        if any(s == "down" for s in services):
            system_status = "Critical"
            status_message = "Some services are down"
        elif any(s == "degraded" or "mock" in str(s) for s in services):
            system_status = "Degraded"
            status_message = "Some services are degraded"
    
    # Get active users (mock data)
    active_users = monitoring_service.active_users
    user_count = len(active_users)
    previous_count = user_count - int(user_count * 0.12)  # Fake 12% increase
    
    # Get open issues (mock data)
    open_issues = 8
    new_issues = 3
    
    # Get average response time
    metrics = await monitoring_service.get_current_metrics()
    avg_response_time = metrics.response_time
    
    # Mock response time change
    response_time_change = -5  # 5% decrease
    
    return {
        "active_users": user_count,
        "user_change": 12,  # Mock 12% increase
        "open_issues": open_issues,
        "new_issues": new_issues,
        "system_status": system_status,
        "status_message": status_message,
        "avg_response_time": avg_response_time,
        "response_time_change": response_time_change
    }

@router.get("/performance", 
    summary="Get performance metrics history",
    description="Returns historical performance metrics for charting",
    response_description="Performance metrics history",
    responses={
        200: {
            "description": "Performance metrics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "current": {
                            "response_time": 120,
                            "request_rate": 150,
                            "error_rate": 0.5
                        },
                        "history": [
                            {
                                "timestamp": "2024-03-05T11:59:00Z",
                                "response_time": 115,
                                "request_rate": 145,
                                "error_rate": 0.4
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_performance_metrics(
    time_range: str = Query("24h", description="Time range (1h, 24h, 7d, 30d)"),
    current_user: dict = Depends(require_role("support"))
):
    """
    Get performance metrics with history
    
    Args:
        time_range: Time range for historical data
    """
    # Get current metrics
    current_metrics = await monitoring_service.get_current_metrics()
    
    # Convert time_range to timedelta
    now = datetime.now()
    if time_range == "1h":
        start_time = now - timedelta(hours=1)
    elif time_range == "7d":
        start_time = now - timedelta(days=7)
    elif time_range == "30d":
        start_time = now - timedelta(days=30)
    else:  # Default to 24h
        start_time = now - timedelta(days=1)
    
    # Get historical metrics
    history = []
    for metrics in monitoring_service.metrics_history:
        if metrics.timestamp >= start_time:
            history.append({
                "timestamp": metrics.timestamp,
                "response_time": metrics.response_time,
                "request_rate": 150,  # Mock data
                "error_rate": metrics.error_rate
            })
    
    return {
        "current": {
            "response_time": current_metrics.response_time,
            "request_rate": 150,  # Mock data
            "error_rate": current_metrics.error_rate
        },
        "history": history
    }

@router.get("/endpoints",
    summary="Get endpoint performance metrics",
    description="Returns performance metrics for individual API endpoints",
    response_description="Endpoint performance metrics",
    responses={
        200: {
            "description": "Endpoint performance metrics retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "path": "/api/v1/courses",
                            "avg_response_time": 85,
                            "request_count": 15000,
                            "error_rate": 0.2,
                            "status": "healthy"
                        }
                    ]
                }
            }
        }
    }
)
async def get_endpoint_performance(
    current_user: dict = Depends(require_role("support"))
):
    """
    Get performance metrics for individual API endpoints
    """
    # Mock endpoint performance data - in a real app this would come from monitoring
    endpoints = [
        {
            "path": "/api/v1/courses",
            "avg_response_time": 85,
            "request_count": 15000,
            "error_rate": 0.2,
            "status": "healthy"
        },
        {
            "path": "/api/v1/users",
            "avg_response_time": 95,
            "request_count": 12000,
            "error_rate": 0.3,
            "status": "healthy"
        },
        {
            "path": "/api/v1/assignments",
            "avg_response_time": 150,
            "request_count": 8000,
            "error_rate": 1.2,
            "status": "degraded"
        },
        {
            "path": "/api/v1/auth",
            "avg_response_time": 110,
            "request_count": 20000,
            "error_rate": 0.1,
            "status": "healthy"
        }
    ]
    
    return endpoints

@router.post("/alerts/{alert_id}/dismiss",
    summary="Dismiss an alert",
    description="Marks an alert as dismissed without resolving it",
    response_description="Dismissed alert",
    responses={
        200: {
            "description": "Alert dismissed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "alert_1234567890",
                        "message": "Alert dismissed successfully"
                    }
                }
            }
        }
    }
)
async def dismiss_alert(
    alert_id: str = Path(..., description="The ID of the alert to dismiss"),
    current_user: dict = Depends(require_role("support"))
):
    """
    Dismiss an alert without resolving it
    
    Args:
        alert_id: The ID of the alert to dismiss
    """
    for i, alert in enumerate(monitoring_service.alerts):
        if alert.id == alert_id:
            # In a real app we might just mark it as dismissed rather than removing
            monitoring_service.alerts.pop(i)
            return {"id": alert_id, "message": "Alert dismissed successfully"}
    
    raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")

@router.get("/errors",
    summary="Get error logs",
    description="Returns error logs with optional filtering",
    response_description="Error logs",
    responses={
        200: {
            "description": "Error logs retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "timestamp": "2024-03-05T12:00:00Z",
                            "severity": "error",
                            "component": "api",
                            "message": "Database connection timeout",
                            "stackTrace": "Error: Connection timeout\n    at Database.connect",
                            "context": {
                                "database": "primary",
                                "attemptCount": 3
                            }
                        }
                    ]
                }
            }
        }
    }
)
async def get_error_logs(
    severity: Optional[str] = Query(None, description="Filter by error severity"),
    component: Optional[str] = Query(None, description="Filter by component"),
    start_time: Optional[str] = Query(None, description="Filter by start time"),
    end_time: Optional[str] = Query(None, description="Filter by end time"),
    limit: int = Query(50, description="Maximum number of logs to return"),
    current_user: dict = Depends(require_role("support"))
):
    """
    Get error logs with filtering
    
    Args:
        severity: Filter by error severity
        component: Filter by component
        start_time: Filter by start time
        end_time: Filter by end time
        limit: Maximum number of logs to return
    """
    # Mock error logs - in a real app this would come from a logging database
    error_logs = [
        {
            "id": 1,
            "timestamp": datetime.now() - timedelta(hours=1),
            "severity": "error",
            "component": "api",
            "message": "Database connection timeout",
            "stackTrace": "Error: Connection timeout\n    at Database.connect (/src/db.js:42)\n    at API.handleRequest (/src/api.js:15)",
            "context": {
                "database": "primary",
                "attemptCount": 3
            }
        },
        {
            "id": 2,
            "timestamp": datetime.now() - timedelta(hours=2),
            "severity": "warning",
            "component": "database",
            "message": "Slow query detected",
            "stackTrace": "Warning: Slow query\n    at Database.query (/src/db.js:85)",
            "context": {
                "query": "SELECT * FROM large_table",
                "execution_time": 5.2
            }
        },
        {
            "id": 3,
            "timestamp": datetime.now() - timedelta(hours=3),
            "severity": "error",
            "component": "auth",
            "message": "Failed login attempts exceeded",
            "stackTrace": "Error: Too many login attempts\n    at Auth.login (/src/auth.js:120)",
            "context": {
                "username": "user@example.com",
                "ip": "192.168.1.1",
                "attempts": 5
            }
        }
    ]
    
    # Apply filters
    filtered_logs = error_logs
    
    if severity:
        filtered_logs = [log for log in filtered_logs if log["severity"] == severity]
    
    if component:
        filtered_logs = [log for log in filtered_logs if log["component"] == component]
    
    if start_time:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start]
    
    if end_time:
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end]
    
    # Sort by timestamp (descending) and limit results
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    filtered_logs = filtered_logs[:limit]
    
    # Format timestamps
    for log in filtered_logs:
        log["timestamp"] = log["timestamp"].isoformat()
    
    return filtered_logs

@router.post("/errors/{error_id}/resolve",
    summary="Resolve an error",
    description="Marks an error as resolved",
    response_description="Resolution result",
    responses={
        200: {
            "description": "Error resolved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "message": "Error resolved successfully"
                    }
                }
            }
        },
        404: {
            "description": "Error not found"
        }
    }
)
async def resolve_error(
    error_id: int = Path(..., description="The ID of the error to resolve"),
    current_user: dict = Depends(require_role("support"))
):
    """
    Resolve an error
    
    Args:
        error_id: The ID of the error to resolve
    """
    # In a real app, this would update a database record
    # For this demo, we'll just return a success response
    return {
        "id": error_id,
        "message": "Error resolved successfully"
    }

@router.get("/health/database", 
    summary="Database health check", 
    description="Check database connectivity and report status",
    tags=["Monitoring"]
)
async def check_database_health(request: Request):
    """
    Checks the health of the database connection.
    
    Returns:
        A JSON object with database health status
    """
    app = request.app
    
    try:
        # Check if we have a connection pool
        if not hasattr(app.state, "pool"):
            return {
                "status": "unavailable",
                "error": "Database connection pool not initialized"
            }
            
        # Test the connection
        async with app.state.pool.connection() as conn:
            # Execute a simple query
            result = await conn.execute("SELECT 1 as test")
            row = await result.fetchone()
            
            # Get pool stats
            pool_stats = {
                "pool_size": app.state.pool.get_size(),
                "pool_min_size": app.state.pool.min_size,
                "pool_max_size": app.state.pool.max_size,
                "idle_connections": app.state.pool.get_idle_size()
            }
            
            return {
                "status": "healthy",
                "test_result": row[0],
                "pool_stats": pool_stats
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 