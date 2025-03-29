from app.services.function_router import function_router

# Auth Functions
@function_router.function_declaration(
    name="login_user",
    description="Login a user with email and password",
    parameters={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "User's email address"
            },
            "password": {
                "type": "string",
                "description": "User's password"
            }
        },
        "required": ["email", "password"]
    }
)
async def login_user(email: str, password: str):
    """Login with email and password"""
    # Implementation will be handled by the actual endpoint
    pass

@function_router.function_declaration(
    name="get_user_info",
    description="Get information about the currently authenticated user",
    parameters={
        "type": "object",
        "properties": {}  # No parameters needed as it uses the auth token
    }
)
async def get_user_info():
    """Get current user information"""
    pass

@function_router.function_declaration(
    name="update_password",
    description="Update the password for the current user",
    parameters={
        "type": "object",
        "properties": {
            "new_password": {
                "type": "string",
                "description": "New password to set"
            }
        },
        "required": ["new_password"]
    }
)
async def update_password(new_password: str):
    """Update user password"""
    pass

# Course Functions
@function_router.function_declaration(
    name="get_user_course_history",
    description="Get the course history for the current user",
    parameters={
        "type": "object",
        "properties": {
            "include_grades": {
                "type": "boolean",
                "description": "Whether to include grade information",
                "default": True
            }
        }
    }
)
async def get_user_course_history(include_grades: bool = True):
    """Get user's course history"""
    pass

@function_router.function_declaration(
    name="get_course_enrollment",
    description="Get enrollment information for a specific course (faculty only)",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "UUID of the course"
            }
        },
        "required": ["course_id"]
    },
    roles=["faculty", "admin"]  # Faculty-only function
)
async def get_course_enrollment(course_id: str):
    """Get course enrollment details"""
    pass

@function_router.function_declaration(
    name="get_course_assignments",
    description="Get all assignments for a course",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "UUID of the course"
            },
            "include_submissions": {
                "type": "boolean",
                "description": "Whether to include submission information",
                "default": False
            }
        },
        "required": ["course_id"]
    },
    roles=["student", "faculty", "admin"]  # Available to all authenticated users
)
async def get_course_assignments(course_id: str, include_submissions: bool = False):
    """Get course assignments"""
    pass

# FAQ Functions
@function_router.function_declaration(
    name="search_faqs",
    description="Search through frequently asked questions",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string"
            },
            "category": {
                "type": "string",
                "description": "Optional category to filter by",
                "default": "all"
            }
        },
        "required": ["query"]
    },
    roles=["student", "faculty", "admin", "anonymous"]  # Available to all users
)
async def search_faqs(query: str, category: str = "all"):
    """Search FAQs"""
    pass

@function_router.function_declaration(
    name="get_faq_categories",
    description="Get all available FAQ categories",
    parameters={
        "type": "object",
        "properties": {}
    }
)
async def get_faq_categories():
    """Get FAQ categories"""
    pass

# System Settings Functions
@function_router.function_declaration(
    name="get_system_settings",
    description="Get current system settings",
    parameters={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Settings category (e.g., 'notifications', 'security')",
                "default": "all"
            }
        }
    }
)
async def get_system_settings(category: str = "all"):
    """Get system settings"""
    pass

# Assignment Functions
@function_router.function_declaration(
    name="get_assignment_details",
    description="Get detailed information about a specific assignment",
    parameters={
        "type": "object",
        "properties": {
            "assignment_id": {
                "type": "string",
                "description": "UUID of the assignment"
            }
        },
        "required": ["assignment_id"]
    }
)
async def get_assignment_details(assignment_id: str):
    """Get assignment details"""
    pass

@function_router.function_declaration(
    name="get_assignment_submission_status",
    description="Get submission status for an assignment",
    parameters={
        "type": "object",
        "properties": {
            "assignment_id": {
                "type": "string",
                "description": "UUID of the assignment"
            }
        },
        "required": ["assignment_id"]
    }
)
async def get_assignment_submission_status(assignment_id: str):
    """Get assignment submission status"""
    pass

# User Management Functions
@function_router.function_declaration(
    name="get_user_profile",
    description="Get detailed profile information for a user",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "UUID of the user (optional, defaults to current user)",
                "default": "current"
            }
        }
    }
)
async def get_user_profile(user_id: str = "current"):
    """Get user profile information"""
    pass

# Monitoring Functions
@function_router.function_declaration(
    name="get_system_health",
    description="Get current system health status and metrics",
    parameters={
        "type": "object",
        "properties": {}
    },
    roles=["admin"]  # Admin-only function
)
async def get_system_health():
    """Get system health status"""
    pass

@function_router.function_declaration(
    name="get_system_metrics",
    description="Get detailed system performance metrics with optional history",
    parameters={
        "type": "object",
        "properties": {
            "include_history": {
                "type": "boolean",
                "description": "Whether to include historical metrics",
                "default": False
            },
            "history_limit": {
                "type": "integer",
                "description": "Number of historical records to return",
                "default": 10
            }
        }
    }
)
async def get_system_metrics(include_history: bool = False, history_limit: int = 10):
    """Get system metrics"""
    pass

@function_router.function_declaration(
    name="get_system_logs",
    description="Get system logs with filtering options",
    parameters={
        "type": "object",
        "properties": {
            "level": {
                "type": "string",
                "description": "Log level filter (INFO, WARNING, ERROR, etc.)",
                "default": "INFO"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of logs to return",
                "default": 100
            }
        }
    }
)
async def get_system_logs(level: str = "INFO", limit: int = 100):
    """Get system logs"""
    pass

@function_router.function_declaration(
    name="create_system_alert",
    description="Create a new system alert",
    parameters={
        "type": "object",
        "properties": {
            "alert_type": {
                "type": "string",
                "description": "Type of alert (e.g., high_cpu_usage, service_down)"
            },
            "severity": {
                "type": "string",
                "description": "Alert severity (info, warning, error, critical)"
            },
            "message": {
                "type": "string",
                "description": "Alert message"
            }
        },
        "required": ["alert_type", "severity", "message"]
    }
)
async def create_system_alert(alert_type: str, severity: str, message: str):
    """Create system alert"""
    pass

@function_router.function_declaration(
    name="get_system_alerts",
    description="Get system alerts with filtering options",
    parameters={
        "type": "object",
        "properties": {
            "alert_type": {
                "type": "string",
                "description": "Filter by alert type",
                "default": None
            },
            "severity": {
                "type": "string",
                "description": "Filter by severity level",
                "default": None
            },
            "resolved": {
                "type": "boolean",
                "description": "Filter by resolution status",
                "default": None
            }
        }
    }
)
async def get_system_alerts(alert_type: str = None, severity: str = None, resolved: bool = None):
    """Get system alerts"""
    pass

@function_router.function_declaration(
    name="web_search",
    description="Search the web for current information",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5
            }
        },
        "required": ["query"]
    },
    roles=["student", "faculty", "admin", "anonymous"]  # Available to all users including unauthenticated
)
async def web_search(query: str, num_results: int = 5):
    """Search the web for current information"""
    return await function_router.web_search(query, num_results)

# Add new function declarations for frontend compatibility
@function_router.function_declaration(
    name="getCourses",
    description="Get all available courses for the current user",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    },
    roles=["student", "faculty", "admin"]
)
async def getCourses():
    """Get all courses available to the current user"""
    pass

@function_router.function_declaration(
    name="getCourseById",
    description="Get details of a specific course by ID",
    parameters={
        "type": "object",
        "properties": {
            "courseId": {
                "type": "string",
                "description": "The ID of the course to retrieve"
            }
        },
        "required": ["courseId"]
    },
    roles=["student", "faculty", "admin"]
)
async def getCourseById(courseId: str):
    """Get a specific course by ID"""
    pass

@function_router.function_declaration(
    name="getAssignments",
    description="Get all assignments for the current user",
    parameters={
        "type": "object",
        "properties": {
            "courseId": {
                "type": "string",
                "description": "Optional: Filter assignments by course ID"
            }
        },
        "required": []
    },
    roles=["student", "faculty", "admin"]
)
async def getAssignments(courseId: str = None):
    """Get assignments, optionally filtered by course"""
    pass

@function_router.function_declaration(
    name="getUserProfile",
    description="Get the current user's profile information",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    },
    roles=["student", "faculty", "admin"]
)
async def getUserProfile():
    """Get current user profile information"""
    pass 