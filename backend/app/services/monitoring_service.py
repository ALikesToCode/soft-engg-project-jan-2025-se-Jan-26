from typing import Dict, List, Optional
import psutil
import logging
import time
from datetime import datetime, timedelta
from fastapi import HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
import os
import asyncio
from app.config import settings

# Get logger for this module
logger = logging.getLogger(__name__)

class ServiceStatus(BaseModel):
    """Service status data model"""
    name: str
    status: str  # "up", "down", "degraded"
    last_check: datetime
    response_time: Optional[float]
    error_message: Optional[str]

class SystemMetrics(BaseModel):
    """System metrics data model"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    response_time: float
    error_rate: float
    timestamp: datetime
    network_io: Dict[str, float]  # bytes sent/received
    process_count: int
    thread_count: int
    open_file_descriptors: int

class Alert(BaseModel):
    """Alert data model"""
    id: str
    type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    acknowledgement: Optional[Dict] = None

class MonitoringService:
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Alert] = []
        self.service_status: Dict[str, ServiceStatus] = {}
        self.alert_thresholds = {
            "cpu_usage": settings.ALERT_THRESHOLD_CPU,
            "memory_usage": settings.ALERT_THRESHOLD_MEMORY,
            "disk_usage": settings.ALERT_THRESHOLD_DISK,
            "response_time": settings.ALERT_THRESHOLD_RESPONSE_TIME,
            "error_rate": settings.ALERT_THRESHOLD_ERROR_RATE,
            "open_files": settings.ALERT_THRESHOLD_OPEN_FILES,
            "process_count": settings.ALERT_THRESHOLD_PROCESS_COUNT
        }
        self.active_users = {}  # Track active user sessions
        self.open_issues = []   # Track open issues/tickets
        self.alert_history = [] # Track alert history
        self.background_tasks = []
        self._is_running = False

    async def start_background_tasks(self):
        """Start background monitoring tasks"""
        if not self._is_running:
            self._is_running = True
            self.background_tasks = [
                asyncio.create_task(self.periodic_health_check()),
                asyncio.create_task(self.periodic_metrics_collection())
            ]
            logger.info("Started monitoring background tasks")

    async def stop_background_tasks(self):
        """Stop background monitoring tasks"""
        self._is_running = False
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
        self.background_tasks = []
        logger.info("Stopped monitoring background tasks")

    async def periodic_health_check(self):
        """Periodically check service health"""
        while self._is_running:
            try:
                await self.check_service_health()
                await asyncio.sleep(settings.MONITORING_HEALTH_CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic health check: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def periodic_metrics_collection(self):
        """Periodically collect system metrics"""
        while self._is_running:
            try:
                await self.get_current_metrics()
                await self.check_thresholds()
                await asyncio.sleep(settings.MONITORING_METRICS_COLLECTION_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic metrics collection: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def check_service_health(self) -> Dict[str, ServiceStatus]:
        """Check health of all services"""
        services = {
            "database": settings.DATABASE_URL,
            # Only include Redis if it's actually being used
            "api": settings.API_HEALTH_URL
        }
        
        # Add Redis service status with error handling
        try:
            from app.routes.auth import redis_client
            # Check if we're using the real Redis or the mock
            if hasattr(redis_client, 'ping') and callable(redis_client.ping):
                is_mock = hasattr(redis_client, 'blacklist') and isinstance(redis_client.blacklist, dict)
                if is_mock:
                    # Using mock Redis
                    self.service_status["redis"] = ServiceStatus(
                        name="redis",
                        status="mock",
                        last_check=datetime.now(),
                        response_time=0,
                        error_message="Using in-memory mock Redis"
                    )
                else:
                    # Try to ping the real Redis
                    try:
                        start_time = time.time()
                        redis_client.ping()
                        response_time = (time.time() - start_time) * 1000
                        self.service_status["redis"] = ServiceStatus(
                            name="redis",
                            status="up",
                            last_check=datetime.now(),
                            response_time=response_time,
                            error_message=None
                        )
                    except Exception as e:
                        self.service_status["redis"] = ServiceStatus(
                            name="redis",
                            status="down",
                            last_check=datetime.now(),
                            response_time=None,
                            error_message=str(e)
                        )
        except Exception as e:
            # Redis module not available or other error
            self.service_status["redis"] = ServiceStatus(
                name="redis",
                status="unknown",
                last_check=datetime.now(),
                response_time=None,
                error_message=str(e)
            )
        
        for service_name, url in services.items():
            try:
                start_time = time.time()
                # Mock service check - replace with actual health checks
                is_healthy = True
                response_time = (time.time() - start_time) * 1000
                
                self.service_status[service_name] = ServiceStatus(
                    name=service_name,
                    status="up" if is_healthy else "down",
                    last_check=datetime.now(),
                    response_time=response_time,
                    error_message=None
                )
            except Exception as e:
                self.service_status[service_name] = ServiceStatus(
                    name=service_name,
                    status="down",
                    last_check=datetime.now(),
                    response_time=None,
                    error_message=str(e)
                )
                
                await self.create_alert(
                    f"{service_name}_down",
                    "critical",
                    f"Service {service_name} is down: {str(e)}"
                )
        
        return self.service_status

    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Get process count safely
            try:
                process_count = len(psutil.pids())
            except Exception:
                process_count = 0
                
            # Get thread count safely
            try:
                thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if hasattr(p, 'num_threads'))
            except Exception:
                thread_count = 0
                
            # Get file descriptors safely - this may not work on all platforms
            try:
                open_file_descriptors = sum(p.num_fds() for p in psutil.process_iter(['num_fds']) if hasattr(p, 'num_fds'))
            except (AttributeError, psutil.AccessDenied, psutil.NoSuchProcess):
                # This might not be available on all platforms or might require elevated permissions
                open_file_descriptors = 0
                
            # Get active connections safely
            try:
                active_connections = len(psutil.net_connections())
            except (psutil.AccessDenied, Exception):
                active_connections = 0
            
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_connections=active_connections,
                response_time=150,  # Mock value
                error_rate=0.5,  # Mock value
                timestamp=datetime.now(),
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                },
                process_count=process_count,
                thread_count=thread_count,
                open_file_descriptors=open_file_descriptors
            )
            
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > settings.MONITORING_METRICS_HISTORY_SIZE:
                self.metrics_history.pop(0)
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            raise HTTPException(status_code=500, detail="Error getting system metrics")

    async def get_system_health(self) -> Dict:
        """Get system health status"""
        try:
            # Get current metrics
            metrics = await self.get_current_metrics()
            
            # Check service health
            services = await self.check_service_health()
            
            # Determine overall status
            active_alerts = [
                alert for alert in self.alerts 
                if not alert.resolved and alert.timestamp > datetime.now() - timedelta(hours=24)
            ]
            
            status = "healthy"
            if active_alerts:
                status = "degraded"
            
            # Check if any service is down
            for service_name, service_status in services.items():
                if service_status.status == "down":
                    status = "unhealthy"
                    break
            
            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "services": {name: status.status for name, status in services.items()},
                "metrics": {
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "disk_usage": metrics.disk_usage,
                    "active_connections": metrics.active_connections,
                    "response_time": metrics.response_time,
                    "error_rate": metrics.error_rate
                }
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting system health: {str(e)}")

    async def acknowledge_alert(self, alert_id: str, user_id: str, comment: str) -> Alert:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledgement = {
                    "user_id": user_id,
                    "timestamp": datetime.now(),
                    "comment": comment
                }
                return alert
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    async def resolve_alert(self, alert_id: str, user_id: str, resolution_note: str) -> Alert:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                alert.resolved_by = user_id
                alert.acknowledgement = {
                    "user_id": user_id,
                    "timestamp": datetime.now(),
                    "resolution_note": resolution_note
                }
                return alert
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    async def get_system_summary(self) -> Dict:
        """Get a comprehensive system summary"""
        metrics = await self.get_current_metrics()
        services = await self.check_service_health()
        
        active_alerts = [
            alert for alert in self.alerts 
            if not alert.resolved and alert.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "system_status": "healthy" if not active_alerts else "degraded",
            "current_metrics": metrics.dict(),
            "services": {name: status.dict() for name, status in services.items()},
            "active_alerts": len(active_alerts),
            "total_alerts_24h": len([
                alert for alert in self.alerts 
                if alert.timestamp > datetime.now() - timedelta(hours=24)
            ]),
            "uptime": time.time() - psutil.boot_time(),
            "last_updated": datetime.now()
        }

    async def get_system_logs(self, level: str = "INFO", limit: int = 100) -> List[Dict]:
        """
        Get system logs.
        
        Args:
            level: The minimum log level to include
            limit: The maximum number of logs to return
            
        Returns:
            A list of log entries
        """
        try:
            # If Logflare is enabled, return a message about logs being in Logflare
            if settings.USE_LOGFLARE:
                return [{
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Logs are being sent to Logflare. View them at https://logflare.app/sources/{settings.LOGFLARE_SOURCE_ID}"
                }]
            
            # Otherwise, read from the local log file
            log_dir = Path("logs")
            log_file = log_dir / "app.log"
            
            if not log_file.exists():
                return []
            
            # Read the log file
            logs = []
            level_value = get_log_level(level)
            
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        # Parse the log line
                        parts = line.strip().split(" - ", 3)
                        if len(parts) < 4:
                            continue
                            
                        timestamp_str, logger_name, level_str, message = parts
                        log_level_value = get_log_level(level_str)
                        
                        # Skip logs below the requested level
                        if log_level_value < level_value:
                            continue
                            
                        logs.append({
                            "timestamp": timestamp_str,
                            "logger": logger_name,
                            "level": level_str,
                            "message": message
                        })
                    except Exception as e:
                        continue
                        
            # Sort logs by timestamp (newest first) and limit
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting system logs: {str(e)}")
            return []

    async def create_alert(self, alert_type: str, severity: str, message: str) -> Alert:
        """
        Create a new system alert
        Args:
            alert_type: Type of alert
            severity: Alert severity
            message: Alert message
        Returns:
            Created Alert object
        """
        try:
            alert = Alert(
                id=f"alert_{int(time.time())}",
                type=alert_type,
                severity=severity,
                message=message,
                timestamp=datetime.now()
            )
            
            self.alerts.append(alert)
            logger.warning(f"New alert created: {alert.dict()}")
            
            return alert
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating alert")

    async def check_thresholds(self) -> Optional[Alert]:
        """
        Check system metrics against thresholds and create alerts if needed
        Returns:
            Alert if threshold exceeded, None otherwise
        """
        try:
            metrics = await self.get_current_metrics()
            
            if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
                return await self.create_alert(
                    "high_cpu_usage",
                    "warning",
                    f"CPU usage is {metrics.cpu_usage}%, above threshold of {self.alert_thresholds['cpu_usage']}%"
                )
            
            if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
                return await self.create_alert(
                    "high_memory_usage",
                    "warning",
                    f"Memory usage is {metrics.memory_usage}%, above threshold of {self.alert_thresholds['memory_usage']}%"
                )
            
            if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
                return await self.create_alert(
                    "high_disk_usage",
                    "warning",
                    f"Disk usage is {metrics.disk_usage}%, above threshold of {self.alert_thresholds['disk_usage']}%"
                )
            
            return None
        except Exception as e:
            logger.error(f"Error checking thresholds: {str(e)}")
            return None

    async def get_active_users_count(self) -> int:
        """Get the number of currently active users"""
        # Clean up expired sessions (older than 15 minutes)
        current_time = datetime.now()
        self.active_users = {
            user_id: last_seen for user_id, last_seen in self.active_users.items()
            if current_time - last_seen < timedelta(minutes=15)
        }
        return len(self.active_users)

    async def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        self.active_users[user_id] = datetime.now()

    async def get_open_issues_count(self) -> int:
        """Get the number of open issues/tickets"""
        return len([issue for issue in self.open_issues if not issue.get('resolved')])

    async def get_average_response_time(self, window_minutes: int = 5) -> float:
        """Get average response time over the last n minutes"""
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=window_minutes)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > window_start
        ]
        
        if not recent_metrics:
            return 0.0
            
        return sum(m.response_time for m in recent_metrics) / len(recent_metrics)

    async def get_performance_trend(self) -> Dict:
        """Get performance trends for the dashboard"""
        if not self.metrics_history:
            return {
                "cpu_trend": 0,
                "memory_trend": 0,
                "response_time_trend": 0
            }

        # Compare with metrics from 1 hour ago
        current = self.metrics_history[-1]
        hour_ago = next(
            (m for m in reversed(self.metrics_history) 
             if current.timestamp - m.timestamp >= timedelta(hours=1)),
            self.metrics_history[0]
        )

        return {
            "cpu_trend": ((current.cpu_usage - hour_ago.cpu_usage) / hour_ago.cpu_usage * 100) 
                if hour_ago.cpu_usage > 0 else 0,
            "memory_trend": ((current.memory_usage - hour_ago.memory_usage) / hour_ago.memory_usage * 100)
                if hour_ago.memory_usage > 0 else 0,
            "response_time_trend": ((current.response_time - hour_ago.response_time) / hour_ago.response_time * 100)
                if hour_ago.response_time > 0 else 0
        }

    async def get_error_summary(self) -> Dict:
        """Get error summary for the dashboard"""
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)
        last_day = current_time - timedelta(days=1)

        logs = await self.get_system_logs(level="ERROR", limit=1000)
        
        return {
            "total_errors": len(logs),
            "errors_last_hour": len([log for log in logs if datetime.fromisoformat(log['timestamp']) > last_hour]),
            "errors_last_day": len([log for log in logs if datetime.fromisoformat(log['timestamp']) > last_day]),
            "error_categories": self._categorize_errors(logs)
        }

    def _categorize_errors(self, logs: List[Dict]) -> Dict:
        """Categorize errors by type"""
        categories = {}
        for log in logs:
            error_type = log.get('category', 'unknown')
            categories[error_type] = categories.get(error_type, 0) + 1
        return categories

    async def get_dashboard_data(self) -> Dict:
        """Get all data needed for the support dashboard"""
        return {
            "active_users": await self.get_active_users_count(),
            "open_issues": await self.get_open_issues_count(),
            "system_status": await self.check_service_health(),
            "avg_response_time": await self.get_average_response_time(),
            "performance_metrics": await self.get_current_metrics(),
            "performance_trends": await self.get_performance_trend(),
            "error_summary": await self.get_error_summary(),
            "active_alerts": [alert for alert in self.alerts if not alert.resolved],
            "system_summary": await self.get_system_summary()
        }

# Create global instance
monitoring_service = MonitoringService() 