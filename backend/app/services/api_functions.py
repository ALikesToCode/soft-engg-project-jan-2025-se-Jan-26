from app.services.function_router import function_router
import logging

logger = logging.getLogger(__name__)

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
    logger.info(f"Function call: login_user with email: {email}")
    return {
        "message": "This function is executed by the authentication endpoint directly",
        "status": "redirect_to_auth"
    }

@function_router.function_declaration(
    name="get_user_info",
    description="Get information about the current logged-in user",
    parameters={
        "type": "object",
        "properties": {}
    },
    roles=["student", "faculty", "admin"]  # Requires authentication
)
async def get_user_info():
    """Get information about the current logged-in user"""
    logger.info("Function call: get_user_info")
    
    try:
        # Use user from auth context
        from app.dependencies import get_current_user
        
        # Check if we're in a request context
        try:
            from fastapi import Request
            from app.auth.context import get_request
            
            # Try to get the current request to access the user
            request = get_request()
            if not request:
                raise ValueError("No active request context")
                
            # Get current user from request
            user = request.state.user
            if not user:
                raise ValueError("User not found in request state")
                
            # Return user info
            return {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "created_at": str(user.created_at),
                "last_login": str(user.last_login) if user.last_login else None,
                "is_active": user.is_active
            }
        except Exception as req_error:
            logger.warning(f"Could not get user from request context: {str(req_error)}")
            
            # Fallback to mock data for testing
            return {
                "id": "12345",
                "username": "test_user",
                "email": "test@example.com",
                "role": "student",
                "full_name": "Test User",
                "created_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-02T00:00:00",
                "is_active": True,
                "note": "This is mock data as user context is unavailable"
            }
    except Exception as e:
        logger.error(f"Error in get_user_info function: {str(e)}")
        return {
            "error": str(e)
        }

@function_router.function_declaration(
    name="update_password",
    description="Update the password for the current user",
    parameters={
        "type": "object",
        "properties": {
            "current_password": {
                "type": "string",
                "description": "Current password for verification"
            },
            "new_password": {
                "type": "string",
                "description": "New password to set"
            }
        },
        "required": ["current_password", "new_password"]
    }
)
async def update_password(current_password: str, new_password: str):
    """Update user password"""
    logger.info("Function call: update_password")
    return {
        "message": "This function is executed by the authentication endpoint directly",
        "status": "redirect_to_auth",
        "action": "update_password"
    }

# Course Functions
@function_router.function_declaration(
    name="get_courses",
    description="Get a list of available courses",
    parameters={
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
                "description": "Page number for pagination",
                "default": 1
            },
            "page_size": {
                "type": "integer",
                "description": "Number of courses per page",
                "default": 10
            },
            "search": {
                "type": "string",
                "description": "Search term to filter courses",
                "default": ""
            },
            "sort_by": {
                "type": "string",
                "description": "Field to sort by (title, created_at, instructor)",
                "default": "title"
            },
            "sort_order": {
                "type": "string",
                "description": "Sort order (asc or desc)",
                "default": "asc"
            }
        }
    },
    roles=["student", "faculty", "admin", "anonymous"]  # Available to all users
)
async def get_courses(page: int = 1, page_size: int = 10, search: str = "", sort_by: str = "title", sort_order: str = "asc"):
    """Get a list of available courses with optional filtering and sorting"""
    logger.info(f"Function call: get_courses with page={page}, page_size={page_size}, search='{search}'")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Use SQLAlchemy to query courses
            from sqlalchemy import select, func, or_
            from app.models.course import Course
            from app.models.user import User
            
            # Start building query
            query = select(Course)
            
            # Add search filter
            if search:
                search_term = f"%{search.lower()}%"
                query = query.where(
                    or_(
                        func.lower(Course.title).like(search_term),
                        func.lower(Course.description).like(search_term)
                    )
                )
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count_result = await db.execute(count_query)
            total_count = total_count_result.scalar_one()
            
            # Add sorting
            if sort_by == "title":
                query = query.order_by(Course.title.asc() if sort_order == "asc" else Course.title.desc())
            elif sort_by == "created_at":
                query = query.order_by(Course.created_at.asc() if sort_order == "asc" else Course.created_at.desc())
            else:
                # Default to title
                query = query.order_by(Course.title.asc() if sort_order == "asc" else Course.title.desc())
            
            # Add pagination
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            # Execute query
            result = await db.execute(query)
            courses = result.scalars().all()
            
            # Format results
            course_list = []
            for course in courses:
                # Get instructor info
                instructor_query = select(User).where(User.id == course.instructor_id)
                instructor_result = await db.execute(instructor_query)
                instructor = instructor_result.scalar_one_or_none()
                
                course_data = {
                    "id": str(course.id),
                    "title": course.title,
                    "description": course.description,
                    "instructor": {
                        "id": str(course.instructor_id),
                        "name": instructor.full_name if instructor else "Unknown"
                    },
                    "created_at": str(course.created_at),
                    "status": course.status,
                    "enrollment_count": course.enrollment_count
                }
                course_list.append(course_data)
            
            # Return paginated results
            return {
                "courses": course_list,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        except Exception as db_error:
            logger.error(f"Database error in get_courses: {str(db_error)}")
            
            # Fallback to mock data for testing
            mock_courses = [
                {
                    "id": "1",
                    "title": "Introduction to Computer Science",
                    "description": "A foundational course covering basic computer science concepts and programming.",
                    "instructor": {
                        "id": "101",
                        "name": "Dr. Alan Turing"
                    },
                    "created_at": "2023-01-15T10:00:00",
                    "status": "active",
                    "enrollment_count": 120
                },
                {
                    "id": "2",
                    "title": "Advanced Machine Learning",
                    "description": "Explore the cutting edge of machine learning algorithms and applications.",
                    "instructor": {
                        "id": "102",
                        "name": "Dr. Ada Lovelace"
                    },
                    "created_at": "2023-02-01T09:30:00",
                    "status": "active",
                    "enrollment_count": 75
                }
            ]
            
            # Apply search filter to mock data
            if search:
                search_term = search.lower()
                mock_courses = [
                    course for course in mock_courses
                    if search_term in course["title"].lower() or search_term in course["description"].lower()
                ]
            
            # Apply sorting to mock data
            if sort_by == "title":
                mock_courses.sort(key=lambda c: c["title"], reverse=(sort_order == "desc"))
            elif sort_by == "created_at":
                mock_courses.sort(key=lambda c: c["created_at"], reverse=(sort_order == "desc"))
            
            # Apply pagination to mock data
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_courses = mock_courses[start_idx:end_idx]
            
            return {
                "courses": paginated_courses,
                "total": len(mock_courses),
                "page": page,
                "page_size": page_size,
                "total_pages": (len(mock_courses) + page_size - 1) // page_size,
                "note": "This is mock data as database query failed"
            }
    except Exception as e:
        logger.error(f"Error in get_courses function: {str(e)}")
        return {
            "courses": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "error": str(e)
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
            pass

@function_router.function_declaration(
    name="get_course_details",
    description="Get detailed information about a specific course",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "ID of the course to retrieve details for"
            }
        },
        "required": ["course_id"]
    },
    roles=["student", "faculty", "admin"]  # Requires authentication
)
async def get_course_details(course_id: str):
    """Get detailed information about a specific course"""
    logger.info(f"Function call: get_course_details with course_id={course_id}")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Use SQLAlchemy to query course details
            from sqlalchemy import select
            from app.models.course import Course
            from app.models.user import User
            from app.models.enrollment import Enrollment
            from app.models.assignment import Assignment
            
            # Get course
            course_query = select(Course).where(Course.id == course_id)
            course_result = await db.execute(course_query)
            course = course_result.scalar_one_or_none()
            
            if not course:
                return {
                    "error": f"Course with ID {course_id} not found"
                }
            
            # Get instructor
            instructor_query = select(User).where(User.id == course.instructor_id)
            instructor_result = await db.execute(instructor_query)
            instructor = instructor_result.scalar_one_or_none()
            
            # Get enrollment count
            enrollment_count_query = select(func.count()).select_from(Enrollment).where(Enrollment.course_id == course_id)
            enrollment_count_result = await db.execute(enrollment_count_query)
            enrollment_count = enrollment_count_result.scalar_one()
            
            # Get assignments
            assignment_query = select(Assignment).where(Assignment.course_id == course_id)
            assignment_result = await db.execute(assignment_query)
            assignments = assignment_result.scalars().all()
            
            # Format course details
            course_details = {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "instructor": {
                    "id": str(course.instructor_id),
                    "name": instructor.full_name if instructor else "Unknown",
                    "email": instructor.email if instructor else "Unknown"
                },
                "created_at": str(course.created_at),
                "status": course.status,
                "enrollment_count": enrollment_count,
                "assignments": [
                    {
                        "id": str(assignment.id),
                        "title": assignment.title,
                        "description": assignment.description,
                        "due_date": str(assignment.due_date),
                        "points": assignment.points
                    }
                    for assignment in assignments
                ],
                "syllabus": course.syllabus,
                "schedule": course.schedule,
                "requirements": course.requirements
            }
            
            return course_details
        except Exception as db_error:
            logger.error(f"Database error in get_course_details: {str(db_error)}")
            
            # Fallback to mock data for testing
            mock_course = {
                "id": course_id,
                "title": "Introduction to Computer Science",
                "description": "A foundational course covering basic computer science concepts and programming.",
                "instructor": {
                    "id": "101",
                    "name": "Dr. Alan Turing",
                    "email": "turing@example.com"
                },
                "created_at": "2023-01-15T10:00:00",
                "status": "active",
                "enrollment_count": 120,
                "assignments": [
                    {
                        "id": "a1",
                        "title": "Basic Programming Concepts",
                        "description": "Implement basic algorithms in Python.",
                        "due_date": "2023-02-15T23:59:59",
                        "points": 100
                    },
                    {
                        "id": "a2",
                        "title": "Data Structures",
                        "description": "Implement and analyze common data structures.",
                        "due_date": "2023-03-01T23:59:59",
                        "points": 150
                    }
                ],
                "syllabus": "Weekly lecture topics include: Introduction to Programming, Variables and Data Types, Control Structures, Functions, Object-Oriented Programming, Data Structures, Algorithms.",
                "schedule": "Lectures: Monday and Wednesday 10:00-11:30, Lab: Friday 14:00-16:00",
                "requirements": "No prior programming experience required. Basic computer skills necessary.",
                "note": "This is mock data as database query failed"
            }
            
            return mock_course
    except Exception as e:
        logger.error(f"Error in get_course_details function: {str(e)}")
        return {
            "error": str(e)
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
            pass

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
    logger.info(f"Function call: get_user_course_history with include_grades={include_grades}")
    try:
        from app.routes.auth import get_current_user_from_context
        from app.database import get_db
        from app.services import enrollment_service
        
        # Get current user
        current_user = await get_current_user_from_context()
        if not current_user:
            return {"error": "Not authenticated", "courses": []}
        
        user_id = current_user.get("id")
        
        # Get database session
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Get enrollments
            enrollments = await enrollment_service.get_user_enrollments(db, user_id)
            
            # Format course history
            courses = []
            for enrollment in enrollments:
                course_data = {
                    "id": str(enrollment.course_id),
                    "title": enrollment.course.title if hasattr(enrollment, "course") else "Unknown Course",
                    "enrollment_date": enrollment.created_at.isoformat() if enrollment.created_at else None,
                    "status": enrollment.status,
                    "progress": enrollment.progress
                }
                
                # Add grades if requested
                if include_grades:
                    course_data["grade"] = enrollment.grade
                    course_data["grade_last_updated"] = enrollment.updated_at.isoformat() if enrollment.updated_at else None
                
                courses.append(course_data)
            
            return {
                "courses": courses,
                "count": len(courses)
            }
        finally:
            await db.close()
    except Exception as e:
        logger.error(f"Error in get_user_course_history: {str(e)}")
        return {
            "error": str(e),
            "courses": []
        }

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
    logger.info(f"Function call: get_course_enrollment for course_id={course_id}")
    try:
        from app.database import get_db
        from app.services import enrollment_service
        from app.routes.auth import get_current_user_from_context
        
        # Get database connection
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        # Get current user to verify permissions
        current_user = await get_current_user_from_context()
        if not current_user:
            return {"error": "Not authenticated"}
        
        user_role = current_user.get("role", "").lower()
        user_id = current_user.get("id")
        
        # Get enrollments for the specified course
        try:
            if user_role == "admin":
                # Admins can see all enrollments
                enrollments = await enrollment_service.get_course_enrollments(db, course_id)
            elif user_role == "faculty":
                # Faculty can only see enrollments for courses they teach
                is_course_instructor = await enrollment_service.is_faculty_for_course(db, user_id, course_id)
                if not is_course_instructor:
                    return {
                        "error": "Permission denied",
                        "message": "You are not the instructor for this course"
                    }
                enrollments = await enrollment_service.get_course_enrollments(db, course_id)
            else:
                return {
                    "error": "Permission denied",
                    "message": "Only faculty and admin users can access enrollment information"
                }
            
            # Format enrollment data
            enrollment_data = []
            for enrollment in enrollments:
                enrollment_data.append({
                    "student_id": str(enrollment.user_id),
                    "student_name": enrollment.user.name if hasattr(enrollment, "user") else "Unknown",
                    "student_email": enrollment.user.email if hasattr(enrollment, "user") else "Unknown",
                    "enrollment_date": enrollment.created_at.isoformat() if enrollment.created_at else None,
                    "status": enrollment.status,
                    "progress": enrollment.progress,
                    "grade": enrollment.grade
                })
            
            return {
                "course_id": course_id,
                "enrollments": enrollment_data,
                "count": len(enrollment_data)
            }
        finally:
            await db.close()
    except Exception as e:
        logger.error(f"Error in get_course_enrollment: {str(e)}")
        return {
            "error": str(e)
        }

@function_router.function_declaration(
    name="get_course_assignments",
    description="Get all assignments for a specific course",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "ID of the course to get assignments for"
            },
            "include_details": {
                "type": "boolean",
                "description": "Whether to include detailed information about each assignment",
                "default": False
            }
        },
        "required": ["course_id"]
    },
    roles=["student", "faculty", "admin"]  # Requires authentication
)
async def get_course_assignments(course_id: str, include_details: bool = False):
    """Get all assignments for a specific course"""
    logger.info(f"Function call: get_course_assignments with course_id={course_id}, include_details={include_details}")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Use SQLAlchemy to query assignments
            from sqlalchemy import select
            from app.models.assignment import Assignment
            from app.models.course import Course
            
            # Check if course exists
            course_query = select(Course).where(Course.id == course_id)
            course_result = await db.execute(course_query)
            course = course_result.scalar_one_or_none()
            
            if not course:
                return {
                    "error": f"Course with ID {course_id} not found",
                    "assignments": []
                }
            
            # Get assignments for course
            assignment_query = select(Assignment).where(Assignment.course_id == course_id)
            assignment_result = await db.execute(assignment_query)
            assignments = assignment_result.scalars().all()
            
            # Format assignments
            if include_details:
                assignment_list = [
                    {
                        "id": str(assignment.id),
                        "title": assignment.title,
                        "description": assignment.description,
                        "due_date": str(assignment.due_date),
                        "created_at": str(assignment.created_at),
                        "updated_at": str(assignment.updated_at),
                        "points": assignment.points,
                        "status": assignment.status,
                        "submission_type": assignment.submission_type,
                        "instructions": assignment.instructions,
                        "resources": assignment.resources,
                        "is_group_assignment": assignment.is_group_assignment,
                        "allow_late_submissions": assignment.allow_late_submissions,
                        "late_submission_penalty": assignment.late_submission_penalty
                    }
                    for assignment in assignments
                ]
            else:
                assignment_list = [
                    {
                        "id": str(assignment.id),
                        "title": assignment.title,
                        "due_date": str(assignment.due_date),
                        "points": assignment.points,
                        "status": assignment.status
                    }
                    for assignment in assignments
                ]
            
            return {
                "course_id": course_id,
                "course_title": course.title,
                "assignments": assignment_list,
                "count": len(assignment_list)
            }
        except Exception as db_error:
            logger.error(f"Database error in get_course_assignments: {str(db_error)}")
            
            # Fallback to mock data for testing
            mock_assignments = [
                {
                    "id": "a1",
                    "title": "Basic Programming Concepts",
                    "due_date": "2023-02-15T23:59:59",
                    "points": 100,
                    "status": "active",
                    "submission_type": "file",
                    "instructions": "Submit a single Python file with your implementation of the required algorithms.",
                    "resources": ["lecture_notes.pdf", "example_code.py"],
                    "is_group_assignment": False,
                    "allow_late_submissions": True,
                    "late_submission_penalty": 10
                },
                {
                    "id": "a2",
                    "title": "Data Structures",
                    "due_date": "2023-03-01T23:59:59",
                    "points": 150,
                    "status": "active",
                    "submission_type": "repository",
                    "instructions": "Submit a GitHub repository link with your implementation.",
                    "resources": ["data_structures.pdf", "analysis_template.docx"],
                    "is_group_assignment": True,
                    "allow_late_submissions": False,
                    "late_submission_penalty": 0
                }
            ]
            
            # Filter based on include_details
            if not include_details:
                mock_assignments = [
                    {
                        "id": a["id"],
                        "title": a["title"],
                        "due_date": a["due_date"],
                        "points": a["points"],
                        "status": a["status"]
                    }
                    for a in mock_assignments
                ]
            
            return {
                "course_id": course_id,
                "course_title": "Mock Course Title",
                "assignments": mock_assignments,
                "count": len(mock_assignments),
                "note": "This is mock data as database query failed"
            }
    except Exception as e:
        logger.error(f"Error in get_course_assignments function: {str(e)}")
        return {
            "course_id": course_id,
            "assignments": [],
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
    name="get_assignment_details",
    description="Get detailed information about a specific assignment",
    parameters={
        "type": "object",
        "properties": {
            "assignment_id": {
                "type": "string",
                "description": "ID of the assignment to retrieve details for"
            }
        },
        "required": ["assignment_id"]
    },
    roles=["student", "faculty", "admin"]  # Requires authentication
)
async def get_assignment_details(assignment_id: str):
    """Get detailed information about a specific assignment"""
    logger.info(f"Function call: get_assignment_details with assignment_id={assignment_id}")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Use SQLAlchemy to query assignment details
            from sqlalchemy import select
            from app.models.assignment import Assignment
            from app.models.course import Course
            
            # Get assignment
            assignment_query = select(Assignment).where(Assignment.id == assignment_id)
            assignment_result = await db.execute(assignment_query)
            assignment = assignment_result.scalar_one_or_none()
            
            if not assignment:
                return {
                    "error": f"Assignment with ID {assignment_id} not found"
                }
            
            # Get course
            course_query = select(Course).where(Course.id == assignment.course_id)
            course_result = await db.execute(course_query)
            course = course_result.scalar_one_or_none()
            
            # Format assignment details
            assignment_details = {
                "id": str(assignment.id),
                "title": assignment.title,
                "description": assignment.description,
                "due_date": str(assignment.due_date),
                "created_at": str(assignment.created_at),
                "updated_at": str(assignment.updated_at),
                "points": assignment.points,
                "status": assignment.status,
                "submission_type": assignment.submission_type,
                "instructions": assignment.instructions,
                "resources": assignment.resources,
                "is_group_assignment": assignment.is_group_assignment,
                "allow_late_submissions": assignment.allow_late_submissions,
                "late_submission_penalty": assignment.late_submission_penalty,
                "course": {
                    "id": str(course.id) if course else None,
                    "title": course.title if course else "Unknown"
                }
            }
            
            # Get submission status if in request context
            try:
                from app.auth.context import get_request
                
                request = get_request()
                if request and hasattr(request.state, "user"):
                    user = request.state.user
                    
                    # Get submission status
                    from app.models.submission import Submission
                    
                    submission_query = select(Submission).where(
                        Submission.assignment_id == assignment_id,
                        Submission.user_id == user.id
                    )
                    submission_result = await db.execute(submission_query)
                    submission = submission_result.scalar_one_or_none()
                    
                    if submission:
                        assignment_details["submission_status"] = {
                            "id": str(submission.id),
                            "status": submission.status,
                            "submitted_at": str(submission.submitted_at),
                            "grade": submission.grade,
                            "feedback": submission.feedback
                        }
                    else:
                        assignment_details["submission_status"] = {
                            "status": "not_submitted"
                        }
            except Exception as sub_error:
                logger.warning(f"Could not get submission status: {str(sub_error)}")
            
            return assignment_details
        except Exception as db_error:
            logger.error(f"Database error in get_assignment_details: {str(db_error)}")
            
            # Fallback to mock data for testing
            mock_assignment = {
                "id": assignment_id,
                "title": "Data Structures Assignment",
                "description": "Implement and analyze common data structures.",
                "due_date": "2023-03-01T23:59:59",
                "created_at": "2023-01-25T14:30:00",
                "updated_at": "2023-01-26T09:15:00",
                "points": 150,
                "status": "active",
                "submission_type": "repository",
                "instructions": "Submit a GitHub repository link with your implementation.",
                "resources": ["data_structures.pdf", "analysis_template.docx"],
                "is_group_assignment": True,
                "allow_late_submissions": False,
                "late_submission_penalty": 0,
                "course": {
                    "id": "c1",
                    "title": "Introduction to Computer Science"
                },
                "submission_status": {
                    "status": "not_submitted"
                },
                "note": "This is mock data as database query failed"
            }
            
            return mock_assignment
    except Exception as e:
        logger.error(f"Error in get_assignment_details function: {str(e)}")
        return {
            "error": str(e)
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
            pass

@function_router.function_declaration(
    name="get_user_assignments",
    description="Get all assignments for the current logged-in user across all enrolled courses",
    parameters={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter assignments by status (upcoming, past, all)",
                "default": "all"
            },
            "sort_by": {
                "type": "string",
                "description": "Field to sort by (due_date, course, title)",
                "default": "due_date"
            },
            "sort_order": {
                "type": "string",
                "description": "Sort order (asc or desc)",
                "default": "asc"
            }
        }
    },
    roles=["student", "faculty", "admin"]  # Requires authentication
)
async def get_user_assignments(status: str = "all", sort_by: str = "due_date", sort_order: str = "asc"):
    """Get all assignments for the current logged-in user across all enrolled courses"""
    logger.info(f"Function call: get_user_assignments with status={status}, sort_by={sort_by}, sort_order={sort_order}")
    
    try:
        # Try to get user from request context
        from app.auth.context import get_request
        
        request = get_request()
        user = None
        
        if request and hasattr(request.state, "user"):
            user = request.state.user
        
        if not user:
            logger.warning("No user found in request context, using mock data")
            
            # Mock data for testing
            mock_assignments = [
                {
                    "id": "a1",
                    "title": "Basic Programming Concepts",
                    "due_date": "2023-02-15T23:59:59",
                    "points": 100,
                    "status": "upcoming",
                    "course": {
                        "id": "c1",
                        "title": "Introduction to Computer Science"
                    },
                    "submission_status": "not_submitted"
                },
                {
                    "id": "a2",
                    "title": "Data Structures",
                    "due_date": "2023-03-01T23:59:59",
                    "points": 150,
                    "status": "upcoming",
                    "course": {
                        "id": "c1",
                        "title": "Introduction to Computer Science"
                    },
                    "submission_status": "not_submitted"
                },
                {
                    "id": "a3",
                    "title": "Database Design",
                    "due_date": "2023-01-20T23:59:59",
                    "points": 120,
                    "status": "past",
                    "course": {
                        "id": "c2",
                        "title": "Database Systems"
                    },
                    "submission_status": "submitted",
                    "grade": 95
                }
            ]
            
            # Apply status filter
            if status != "all":
                mock_assignments = [a for a in mock_assignments if a["status"] == status]
            
            # Apply sorting
            if sort_by == "due_date":
                mock_assignments.sort(key=lambda a: a["due_date"], reverse=(sort_order == "desc"))
            elif sort_by == "course":
                mock_assignments.sort(key=lambda a: a["course"]["title"], reverse=(sort_order == "desc"))
            elif sort_by == "title":
                mock_assignments.sort(key=lambda a: a["title"], reverse=(sort_order == "desc"))
            
            return {
                "assignments": mock_assignments,
                "count": len(mock_assignments),
                "note": "This is mock data as user context is unavailable"
            }
            
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Use SQLAlchemy to query assignments for enrolled courses
            from sqlalchemy import select, join
            from sqlalchemy.sql import func
            from app.models.assignment import Assignment
            from app.models.course import Course
            from app.models.enrollment import Enrollment
            from app.models.submission import Submission
            from datetime import datetime
            
            # Get current time
            now = datetime.utcnow()
            
            # Get user enrollments
            enrollments_query = select(Enrollment.course_id).where(Enrollment.user_id == user.id)
            enrollments_result = await db.execute(enrollments_query)
            enrolled_course_ids = [str(r) for r in enrollments_result.scalars().all()]
            
            if not enrolled_course_ids:
                return {
                    "assignments": [],
                    "count": 0,
                    "message": "User is not enrolled in any courses"
                }
            
            # Build query for assignments in enrolled courses
            assignments_query = select(
                Assignment,
                Course.title.label("course_title"),
                Course.id.label("course_id")
            ).join(
                Course, Assignment.course_id == Course.id
            ).where(
                Assignment.course_id.in_(enrolled_course_ids)
            )
            
            # Apply status filter
            if status == "upcoming":
                assignments_query = assignments_query.where(Assignment.due_date > now)
            elif status == "past":
                assignments_query = assignments_query.where(Assignment.due_date <= now)
            
            # Apply sorting
            if sort_by == "due_date":
                if sort_order == "asc":
                    assignments_query = assignments_query.order_by(Assignment.due_date.asc())
                else:
                    assignments_query = assignments_query.order_by(Assignment.due_date.desc())
            elif sort_by == "course":
                if sort_order == "asc":
                    assignments_query = assignments_query.order_by(Course.title.asc())
                else:
                    assignments_query = assignments_query.order_by(Course.title.desc())
            elif sort_by == "title":
                if sort_order == "asc":
                    assignments_query = assignments_query.order_by(Assignment.title.asc())
                else:
                    assignments_query = assignments_query.order_by(Assignment.title.desc())
            
            # Execute query
            assignments_result = await db.execute(assignments_query)
            assignments_data = assignments_result.all()
            
            # Format assignments
            assignments_list = []
            for assignment_row in assignments_data:
                assignment = assignment_row[0]
                course_title = assignment_row.course_title
                course_id = assignment_row.course_id
                
                # Get submission status
                submission_query = select(Submission).where(
                    Submission.assignment_id == assignment.id,
                    Submission.user_id == user.id
                )
                submission_result = await db.execute(submission_query)
                submission = submission_result.scalar_one_or_none()
                
                # Determine status
                assignment_status = "upcoming" if assignment.due_date > now else "past"
                submission_status = "not_submitted"
                grade = None
                
                if submission:
                    submission_status = submission.status
                    grade = submission.grade
                
                assignment_data = {
                    "id": str(assignment.id),
                    "title": assignment.title,
                    "due_date": str(assignment.due_date),
                    "points": assignment.points,
                    "status": assignment_status,
                    "course": {
                        "id": str(course_id),
                        "title": course_title
                    },
                    "submission_status": submission_status
                }
                
                if grade is not None:
                    assignment_data["grade"] = grade
                
                assignments_list.append(assignment_data)
            
            return {
                "assignments": assignments_list,
                "count": len(assignments_list)
            }
        except Exception as db_error:
            logger.error(f"Database error in get_user_assignments: {str(db_error)}")
            
            # Fallback to mock data
            mock_assignments = [
                {
                    "id": "a1",
                    "title": "Basic Programming Concepts",
                    "due_date": "2023-02-15T23:59:59",
                    "points": 100,
                    "status": "upcoming",
                    "course": {
                        "id": "c1",
                        "title": "Introduction to Computer Science"
                    },
                    "submission_status": "not_submitted"
                },
                {
                    "id": "a3",
                    "title": "Database Design",
                    "due_date": "2023-01-20T23:59:59",
                    "points": 120,
                    "status": "past",
                    "course": {
                        "id": "c2",
                        "title": "Database Systems"
                    },
                    "submission_status": "submitted",
                    "grade": 95
                }
            ]
            
            # Apply status filter
            if status != "all":
                mock_assignments = [a for a in mock_assignments if a["status"] == status]
            
            # Apply sorting
            if sort_by == "due_date":
                mock_assignments.sort(key=lambda a: a["due_date"], reverse=(sort_order == "desc"))
            elif sort_by == "course":
                mock_assignments.sort(key=lambda a: a["course"]["title"], reverse=(sort_order == "desc"))
            elif sort_by == "title":
                mock_assignments.sort(key=lambda a: a["title"], reverse=(sort_order == "desc"))
            
            return {
                "assignments": mock_assignments,
                "count": len(mock_assignments),
                "note": "This is mock data as database query failed"
            }
    except Exception as e:
        logger.error(f"Error in get_user_assignments function: {str(e)}")
        return {
            "error": str(e),
            "assignments": [],
            "count": 0
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
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
    logger.info(f"Function call: search_faqs with query='{query}', category='{category}', limit={limit}")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
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
                    "priority": faq.priority,
                    "relevance_score": getattr(faq, "relevance_score", None)
                }
                for faq in results
            ]
            
            # Apply category filter if specified
            if category != "all":
                formatted_results = [r for r in formatted_results if r.get("category") == category]
            
            return {
                "results": formatted_results,
                "count": len(formatted_results),
                "query": query,
                "search_type": "vector"
            }
        except ImportError as service_error:
            logger.warning(f"Could not use faq_service: {str(service_error)}. Using keyword search fallback.")
            
            # Fallback to keyword search
            try:
                # Use SQLAlchemy directly for keyword search
                from sqlalchemy import or_, select, func
                from app.models.faq import FAQ
                
                # Create query
                query_obj = select(FAQ)
                
                # Add search conditions
                search_words = query.lower().split()
                search_conditions = []
                for word in search_words:
                    search_conditions.append(func.lower(FAQ.question).contains(word))
                    search_conditions.append(func.lower(FAQ.answer).contains(word))
                
                if search_conditions:
                    query_obj = query_obj.where(or_(*search_conditions))
                
                # Add category filter
                if category != "all":
                    query_obj = query_obj.where(FAQ.category_id == category)
                
                # Execute query
                result = await db.execute(query_obj.limit(limit))
                faqs = result.scalars().all()
                
                # Format results
                formatted_results = [
                    {
                        "id": str(faq.id),
                        "question": faq.question,
                        "answer": faq.answer,
                        "category": faq.category_id,
                        "priority": faq.priority
                    }
                    for faq in faqs
                ]
                
                return {
                    "results": formatted_results,
                    "count": len(formatted_results),
                    "query": query,
                    "search_type": "keyword"
                }
            except Exception as sql_error:
                logger.error(f"SQL keyword search failed: {str(sql_error)}. Using mock data.")
                
                # Mock results for testing if everything fails
                mock_results = [
                    {
                        "id": "1",
                        "question": "How do I reset my password?",
                        "answer": "You can reset your password by clicking on the 'Forgot Password' link on the login page.",
                        "category": "account",
                        "priority": 5
                    },
                    {
                        "id": "2",
                        "question": "How do I enroll in a course?",
                        "answer": "To enroll in a course, go to the course catalog, find the course you want, and click 'Enroll'.",
                        "category": "courses",
                        "priority": 4
                    }
                ]
                
                # Apply category filter if specified
                if category != "all":
                    mock_results = [r for r in mock_results if r.get("category") == category]
                
                return {
                    "results": mock_results[:limit],
                    "count": len(mock_results[:limit]),
                    "query": query,
                    "search_type": "mock"
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
    logger.info(f"Function call: vector_search_faqs with query='{query}', limit={limit}")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Import vector search service
            from app.services import faq_service
            
            # Perform vector-only search
            logger.info(f"Performing vector-only search for FAQs with query: {query}")
            results = await faq_service.vector_search_faqs(db, query, limit)
            
            # Format the results
            formatted_results = [
                {
                    "id": str(faq.id),
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": faq.category_id,
                    "priority": faq.priority,
                    "relevance_score": getattr(faq, "relevance_score", None),
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
            logger.error(f"Vector search failed: {str(e)}. Returning empty results.")
            return {
                "results": [],
                "count": 0,
                "query": query,
                "error": f"Vector search unavailable: {str(e)}"
            }
    except Exception as e:
        logger.error(f"Error in vector_search_faqs function: {str(e)}")
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
    name="get_faq_categories",
    description="Get all available FAQ categories",
    parameters={
        "type": "object",
        "properties": {}
    }
)
async def get_faq_categories():
    """Get FAQ categories"""
    logger.info("Function call: get_faq_categories")
    
    try:
        # Get a database session
        from app.database import get_db
        
        db_generator = get_db()
        db = await db_generator.__anext__()
        
        try:
            # Get categories from database
            from sqlalchemy import select
            from app.models.faq import FAQCategory
            
            query = select(FAQCategory)
            result = await db.execute(query)
            categories = result.scalars().all()
            
            return {
                "categories": [
                    {
                        "id": category.id,
                        "name": category.name,
                        "description": category.description
                    }
                    for category in categories
                ],
                "count": len(categories)
            }
        except Exception as e:
            logger.error(f"Error fetching FAQ categories: {str(e)}")
            
            # Return mock categories if database query fails
            mock_categories = [
                {"id": "account", "name": "Account Management", "description": "Questions about account settings and management"},
                {"id": "courses", "name": "Courses", "description": "Questions about finding and enrolling in courses"},
                {"id": "assignments", "name": "Assignments", "description": "Questions about assignments and submissions"},
                {"id": "technical", "name": "Technical Support", "description": "Technical issues and troubleshooting"}
            ]
            
            return {
                "categories": mock_categories,
                "count": len(mock_categories),
                "note": "Using mock data due to database error"
            }
    except Exception as e:
        logger.error(f"Error in get_faq_categories function: {str(e)}")
        return {
            "categories": [],
            "count": 0,
            "error": str(e)
        }
    finally:
        # Close the database session
        try:
            await db.close()
        except:
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