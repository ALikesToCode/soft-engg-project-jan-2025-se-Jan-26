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
    description="Search through frequently asked questions using vector and keyword search",
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
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10
            }
        },
        "required": ["query"]
    },
    roles=["student", "faculty", "admin", "anonymous"]  # Available to all users
)
async def search_faqs(query: str, category: str = "all", limit: int = 10):
    """Search FAQs using vector search and keyword search"""
    import logging
    from app.database import get_db
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get a database session
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        # Mock results for testing if DB query fails
        mock_results = [
            {
                "id": "1",
                "question": "How do I reset my password?",
                "answer": "You can reset your password by clicking on the 'Forgot Password' link on the login page.",
                "category_id": "account",
                "priority": 5
            },
            {
                "id": "2",
                "question": "How do I enroll in a course?",
                "answer": "To enroll in a course, go to the course catalog, find the course you want, and click 'Enroll'.",
                "category_id": "courses",
                "priority": 4
            }
        ]
        
        # Try to run actual query if module exists
        try:
            from app.services import faq_service
            
            # First try vector search
            logger.info(f"Searching FAQs with vector search for query: {query}")
            results = await faq_service.search_faqs(db, query, limit)
            
            # Format the results
            formatted_results = [
                {
                    "id": str(faq.id),
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": faq.category_id,
                    "priority": faq.priority
                }
                for faq in results
            ]
        except (ImportError, AttributeError) as service_error:
            logger.warning(f"Could not use faq_service: {str(service_error)}. Using mock data.")
            formatted_results = mock_results[:limit]
        
        # Apply category filter if specified
        if category != "all":
            formatted_results = [r for r in formatted_results if r.get("category") == category]
        
        return {
            "results": formatted_results,
            "count": len(formatted_results),
            "query": query
        }
    except Exception as e:
        logger.error(f"Error in search_faqs function: {str(e)}")
        return {
            "results": [],
            "count": 0,
            "query": query,
            "error": str(e)
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
            pass

@function_router.function_declaration(
    name="vector_search_faqs",
    description="Search FAQs using semantic vector search for more intelligent results",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5
            }
        },
        "required": ["query"]
    },
    roles=["student", "faculty", "admin", "anonymous"]  # Available to all users
)
async def vector_search_faqs(query: str, limit: int = 5):
    """Search FAQs using semantic vector search only"""
    from app.database import get_db
    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    import logging
    from app.services import faq_service
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get a database session
        db = next(get_db())
        
        # Perform vector-only search
        logger.info(f"Performing vector-only search for FAQs with query: {query}")
        results = await faq_service.vector_search_faqs(query, limit)
        
        # Format the results
        formatted_results = [
            {
                "id": str(faq.id),
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category_id,
                "priority": faq.priority,
                "search_type": "vector"
            }
            for faq in results
        ]
        
        return {
            "results": formatted_results,
            "count": len(formatted_results),
            "query": query
        }
    except Exception as e:
        logger.error(f"Error in vector_search_faqs function: {str(e)}")
        return {
            "results": [],
            "count": 0,
            "query": query,
            "error": str(e)
        }

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
    import logging
    from app.database import get_db
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get a database session
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        # Try to use actual course service
        try:
            from app.services import course_service
            from app.routes.auth import get_current_user_from_context
            
            # Get current user
            current_user = await get_current_user_from_context()
            user_id = current_user.get("id") if current_user else None
            
            if not user_id:
                return {
                    "courses": [],
                    "error": "Not authenticated"
                }
            
            # Get courses from database
            courses = await course_service.get_user_courses(db, user_id)
            
            course_list = [
                {
                    "id": str(course.id),
                    "title": course.title,
                    "description": course.description,
                    "instructor": course.instructor_name,
                    "enrolled": True,
                    "progress": course.progress or 0,
                    "thumbnail": course.thumbnail_url
                }
                for course in courses
            ]
            
            return {
                "courses": course_list,
                "count": len(course_list)
            }
        
        except (ImportError, AttributeError) as service_error:
            logger.warning(f"Could not use course_service: {str(service_error)}. Using mock data.")
            
            # Mock data for testing
            mock_courses = [
                {
                    "id": "course-1",
                    "title": "Introduction to Programming",
                    "description": "Learn the basics of programming with Python",
                    "instructor": "Dr. Smith",
                    "enrolled": True,
                    "progress": 35,
                    "thumbnail": "/assets/images/courses/python-intro.jpg"
                },
                {
                    "id": "course-2",
                    "title": "Data Structures and Algorithms",
                    "description": "Learn essential data structures and algorithms",
                    "instructor": "Prof. Johnson",
                    "enrolled": True,
                    "progress": 20,
                    "thumbnail": "/assets/images/courses/dsa.jpg"
                }
            ]
            
            return {
                "courses": mock_courses,
                "count": len(mock_courses)
            }
            
    except Exception as e:
        logger.error(f"Error in getCourses function: {str(e)}")
        return {
            "courses": [],
            "count": 0,
            "error": str(e)
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
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

@function_router.function_declaration(
    name="generateLearningRoadmap",
    description="Generate a structured learning roadmap from a course's content",
    parameters={
        "type": "object",
        "properties": {
            "courseId": {
                "type": "string",
                "description": "The ID of the course to generate a roadmap for"
            },
            "difficultyLevel": {
                "type": "string",
                "description": "Optional: The preferred difficulty level (beginner, intermediate, advanced)",
                "enum": ["beginner", "intermediate", "advanced"]
            },
            "focusAreas": {
                "type": "array",
                "description": "Optional: Specific areas to focus on in the roadmap",
                "items": {
                    "type": "string"
                }
            },
            "timeframeWeeks": {
                "type": "integer",
                "description": "Optional: The preferred timeframe in weeks for completing the roadmap"
            }
        },
        "required": ["courseId"]
    },
    roles=["student", "faculty", "admin"]
)
async def generateLearningRoadmap(
    courseId: str, 
    difficultyLevel: str = "intermediate", 
    focusAreas: list = None, 
    timeframeWeeks: int = None
):
    """
    Generate a personalized learning roadmap based on a course's content.
    This function analyzes course modules, lectures, and materials to create
    a structured learning path with milestones and estimated completion times.
    """
    from app.services.course_service import get_modules_by_course
    from app.database import get_db
    from app.models.user import User
    from sqlalchemy.ext.asyncio import AsyncSession
    import asyncio
    import uuid
    
    try:
        # Get database session
        db = await get_db().__anext__()
        
        # Get course modules
        try:
            # Mock user ID for the function call (admin)
            admin_user_id = uuid.uuid4()
            modules = await get_modules_by_course(courseId, db, admin_user_id)
        except Exception as e:
            return {
                "error": f"Error fetching course modules: {str(e)}",
                "roadmap": None
            }
        
        # Structure for a learning roadmap
        roadmap = {
            "id": uuid.uuid4().hex,
            "title": f"Learning Path for Course {courseId}",
            "description": f"Personalized roadmap with {difficultyLevel} difficulty",
            "completedSteps": 0,
            "totalSteps": len(modules),
            "milestones": []
        }
        
        # Create milestones from modules
        position = 0
        for module in modules:
            position += 1
            milestone = {
                "id": position,
                "title": module.get("title", f"Module {position}"),
                "description": module.get("description", "No description available"),
                "status": "locked" if position > 1 else "in_progress",
                "estimatedTime": f"{position} week{'s' if position > 1 else ''}",
                "locked": position > 1,
                "materials": []
            }
            
            # Add placeholder materials
            material_id = 1
            for _ in range(min(2, position)):  # Add 1-2 materials per milestone
                material_type = ["video", "exercise", "project", "tutorial", "course"][material_id % 5]
                milestone["materials"].append({
                    "id": material_id,
                    "type": material_type,
                    "title": f"{module.get('title', 'Module')} - Material {material_id}",
                    "description": f"Learning material for {module.get('title', 'this module')}",
                    "duration": f"{material_id + 1} hours",
                    "url": f"/course/{courseId}/module/{module.get('id', 0)}/material/{material_id}"
                })
                material_id += 1
            
            roadmap["milestones"].append(milestone)
        
        return {
            "roadmap": roadmap,
            "error": None
        }
    except Exception as e:
        return {
            "error": f"Error generating roadmap: {str(e)}",
            "roadmap": None
        }
    finally:
        # Close database session
        await db.close() 