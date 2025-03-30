#!/usr/bin/env python3
"""
Generate mock data for the database.

This script checks the database for existing data and generates mock data for all tables if they are empty.
It creates a comprehensive set of test data for users, courses, modules, lectures, FAQs, and related tables.
"""

import asyncio
import logging
import os
import random
import uuid
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
import bcrypt
import psycopg
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()

# Load environment variables
load_dotenv()

# Constants for data generation
USER_ROLES = ["student", "faculty", "admin", "support"]
COURSE_STATUSES = ["DRAFT", "ACTIVE", "ARCHIVED"]
ENROLLMENT_STATUSES = ["enrolled", "completed", "dropped", "waitlisted"]
COURSE_LEVELS = ["Beginner", "Intermediate", "Advanced"]
SEMESTERS = ["Fall", "Spring", "Summer"]
LECTURE_CONTENT_TYPES = ["lecture", "quiz", "assignment", "document"]
FAQ_CATEGORIES = ["general", "technical", "courses", "account", "faculty"]

# Mock data counts
NUM_USERS = 50
NUM_FACULTY = 10
NUM_COURSES = 20
NUM_STUDENTS_PER_COURSE = 15
NUM_MODULES_PER_COURSE = 4
NUM_LECTURES_PER_MODULE = 3
NUM_FAQS = 30

async def check_table_empty(conn, table_name):
    """
    Check if a table is empty.
    
    Args:
        conn: Database connection
        table_name: Name of the table to check
        
    Returns:
        bool: True if the table is empty, False otherwise
    """
    async with conn.cursor() as cur:
        try:
            await cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = await cur.fetchone()
            return count[0] == 0
        except Exception as e:
            logger.error(f"Error checking if {table_name} is empty: {str(e)}")
            return False

async def create_users(conn):
    """
    Create mock users with various roles.
    
    Args:
        conn: Database connection
    """
    if not await check_table_empty(conn, "users"):
        logger.info("Users table is not empty, skipping")
        # Return some default values from existing data
        async with conn.cursor() as cur:
            # Get an admin user
            await cur.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
            admin_result = await cur.fetchone()
            admin_id = admin_result[0] if admin_result else str(uuid.uuid4())
            
            # Get faculty users
            await cur.execute("SELECT id FROM users WHERE role = 'faculty' LIMIT %s", (NUM_FACULTY,))
            faculty_results = await cur.fetchall()
            faculty_ids = [row[0] for row in faculty_results]
            
            # Get student users
            await cur.execute("SELECT id FROM users WHERE role = 'student' LIMIT %s", (NUM_USERS - NUM_FACULTY - 1,))
            student_results = await cur.fetchall()
            student_ids = [row[0] for row in student_results]
            
            return admin_id, faculty_ids, student_ids
    
    logger.info(f"Creating {NUM_USERS} mock users...")
    
    # Create admin user with known credentials
    admin_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    
    async with conn.cursor() as cur:
        await cur.execute("""
            INSERT INTO users (id, email, name, hashed_password, is_google_user, picture, created_at, updated_at, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            admin_id,
            "admin@example.com",
            "Admin User",
            hashed_password,
            False,
            fake.image_url(),
            datetime.now(UTC),
            datetime.now(UTC),
            "admin"
        ))
    
    # Create faculty users
    faculty_ids = []
    for i in range(NUM_FACULTY):
        user_id = str(uuid.uuid4())
        faculty_ids.append(user_id)
        hashed_password = bcrypt.hashpw(f"faculty{i}".encode(), bcrypt.gensalt()).decode()
        
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO users (id, email, name, hashed_password, is_google_user, picture, created_at, updated_at, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                f"faculty{i}@example.com",
                f"Faculty Member {i}",
                hashed_password,
                False,
                fake.image_url(),
                datetime.now(UTC),
                datetime.now(UTC),
                "faculty"
            ))
    
    # Create regular student users
    student_ids = []
    for i in range(NUM_USERS - NUM_FACULTY - 1):  # -1 for admin
        user_id = str(uuid.uuid4())
        student_ids.append(user_id)
        hashed_password = bcrypt.hashpw(f"student{i}".encode(), bcrypt.gensalt()).decode()
        
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO users (id, email, name, hashed_password, is_google_user, picture, created_at, updated_at, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                f"student{i}@example.com",
                fake.name(),
                hashed_password,
                random.choice([True, False]),
                fake.image_url(),
                datetime.now(UTC),
                datetime.now(UTC),
                "student"
            ))
    
    logger.info(f"Created {NUM_USERS} mock users")
    return admin_id, faculty_ids, student_ids

async def create_courses(conn, admin_id, faculty_ids):
    """
    Create mock courses.
    
    Args:
        conn: Database connection
        admin_id: ID of the admin user
        faculty_ids: List of faculty user IDs
    """
    if not await check_table_empty(conn, "courses"):
        logger.info("Courses table is not empty, skipping")
        # Return existing course IDs
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM courses LIMIT %s", (NUM_COURSES,))
            course_results = await cur.fetchall()
            course_ids = [row[0] for row in course_results]
            return course_ids
    
    logger.info(f"Creating {NUM_COURSES} mock courses...")
    
    course_ids = []
    for i in range(NUM_COURSES):
        course_id = str(uuid.uuid4())
        course_ids.append(course_id)
        
        # Pick random faculty
        faculty_id = random.choice(faculty_ids)
        
        # Generate course dates
        current_year = datetime.now().year
        start_date = fake.date_time_between(start_date="-1y", end_date="+1y", tzinfo=UTC)
        end_date = start_date + timedelta(days=random.randint(90, 180))
        
        # Generate course
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO courses (
                    id, name, code, title, syllabus, description, credits, duration, 
                    semester, year, status, level, start_date, end_date, 
                    enrollment_limit, waitlist_limit, image, created_at, updated_at, 
                    created_by, faculty_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                course_id,
                f"Course {i}",
                f"CS{100+i}",
                fake.catch_phrase(),
                fake.paragraph(nb_sentences=5),
                fake.paragraph(nb_sentences=10),
                random.randint(1, 4),
                random.randint(8, 16),  # weeks
                random.choice(SEMESTERS),
                current_year,
                random.choice(COURSE_STATUSES),
                random.choice(COURSE_LEVELS),
                start_date,
                end_date,
                random.randint(30, 100),
                random.randint(5, 20),
                fake.image_url(),
                datetime.now(UTC),
                datetime.now(UTC),
                admin_id,
                faculty_id
            ))
    
    logger.info(f"Created {NUM_COURSES} mock courses")
    return course_ids

async def create_modules(conn, course_ids):
    """
    Create mock modules for courses.
    
    Args:
        conn: Database connection
        course_ids: List of course IDs
    """
    if not await check_table_empty(conn, "module"):
        logger.info("Modules table is not empty, skipping")
        # Return existing module IDs organized by course
        module_ids = {}
        async with conn.cursor() as cur:
            for course_id in course_ids:
                await cur.execute("SELECT id FROM module WHERE course_id = %s", (course_id,))
                module_results = await cur.fetchall()
                module_ids[course_id] = [row[0] for row in module_results]
        return module_ids
    
    logger.info(f"Creating modules for {len(course_ids)} courses...")
    
    module_ids = {}  # {course_id: [module_ids]}
    
    for course_id in course_ids:
        module_ids[course_id] = []
        
        for i in range(NUM_MODULES_PER_COURSE):
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO module (course_id, title, position)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (
                    course_id,
                    f"Module {i+1}: {fake.bs()}",
                    i+1
                ))
                module_id = await cur.fetchone()
                module_ids[course_id].append(module_id[0])
    
    logger.info(f"Created modules for {len(course_ids)} courses")
    return module_ids

async def create_lectures(conn, module_ids):
    """
    Create mock lectures for modules.
    
    Args:
        conn: Database connection
        module_ids: Dictionary mapping course IDs to lists of module IDs
    """
    if not await check_table_empty(conn, "lecture"):
        logger.info("Lectures table is not empty, skipping")
        # Return existing lecture IDs organized by module
        lecture_ids = {}
        async with conn.cursor() as cur:
            for course_id, modules in module_ids.items():
                for module_id in modules:
                    await cur.execute("SELECT id FROM lecture WHERE module_id = %s", (module_id,))
                    lecture_results = await cur.fetchall()
                    lecture_ids[module_id] = [row[0] for row in lecture_results]
        return lecture_ids
    
    logger.info("Creating lectures for modules...")
    
    lecture_ids = {}  # {module_id: [lecture_ids]}
    
    for course_id, modules in module_ids.items():
        for module_id in modules:
            lecture_ids[module_id] = []
            
            for i in range(NUM_LECTURES_PER_MODULE):
                content_type = random.choice(LECTURE_CONTENT_TYPES)
                
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO lecture (module_id, content_type, position)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (
                        module_id,
                        content_type,
                        i+1
                    ))
                    lecture_id = await cur.fetchone()
                    lecture_ids[module_id].append(lecture_id[0])
    
    logger.info("Created lectures for modules")
    return lecture_ids

async def create_lecture_content(conn, lecture_ids):
    """
    Create mock lecture content.
    
    Args:
        conn: Database connection
        lecture_ids: Dictionary mapping module IDs to lists of lecture IDs
    """
    if not await check_table_empty(conn, "lecture_content"):
        logger.info("Lecture content table is not empty, skipping")
        return
    
    logger.info("Creating lecture content...")
    
    for module_id, lectures in lecture_ids.items():
        for lecture_id in lectures:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO lecture_content (lecture_id, title, content_url, content_desc)
                    VALUES (%s, %s, %s, %s)
                """, (
                    lecture_id,
                    fake.catch_phrase(),
                    fake.url(),
                    fake.paragraph(nb_sentences=3)
                ))
    
    logger.info("Created lecture content")

async def create_lecture_content_docs(conn, lecture_ids):
    """
    Create mock lecture content documents.
    
    Args:
        conn: Database connection
        lecture_ids: Dictionary mapping module IDs to lists of lecture IDs
    """
    if not await check_table_empty(conn, "lecture_content_doc"):
        logger.info("Lecture content doc table is not empty, skipping")
        return
    
    logger.info("Creating lecture content docs...")
    
    file_types = ["application/pdf", "application/vnd.ms-powerpoint", "application/msword"]
    
    for module_id, lectures in lecture_ids.items():
        for lecture_id in lectures:
            # Only create docs for some lectures
            if random.choice([True, False]):
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO lecture_content_doc (lecture_id, title, content_desc, content_doc, file_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        lecture_id,
                        fake.catch_phrase(),
                        fake.paragraph(nb_sentences=2),
                        fake.file_path(extension=random.choice(["pdf", "ppt", "doc"])),
                        random.choice(file_types)
                    ))
    
    logger.info("Created lecture content docs")

async def create_enrollments(conn, course_ids, student_ids):
    """
    Create mock course enrollments.
    
    Args:
        conn: Database connection
        course_ids: List of course IDs
        student_ids: List of student user IDs
    """
    if not await check_table_empty(conn, "course_enrollments"):
        logger.info("Course enrollments table is not empty, skipping")
        return
    
    logger.info("Creating course enrollments...")
    
    for course_id in course_ids:
        # Select random students for this course
        course_students = random.sample(student_ids, min(NUM_STUDENTS_PER_COURSE, len(student_ids)))
        
        for student_id in course_students:
            status = random.choice(ENROLLMENT_STATUSES)
            enrollment_date = datetime.now(UTC) - timedelta(days=random.randint(1, 90))
            completion_date = None
            
            if status == "completed":
                completion_date = enrollment_date + timedelta(days=random.randint(30, 90))
            
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO course_enrollments (
                        id, course_id, student_id, user_id, status, enrollment_date, 
                        completion_date, grade, created_at, updated_at, 
                        certificate_url, progress, last_activity, is_favorited
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    course_id,
                    student_id,
                    student_id,  # user_id same as student_id
                    status,
                    enrollment_date,
                    completion_date,
                    random.choice(["A", "B", "C", "D", "F", None]),
                    enrollment_date,
                    datetime.now(UTC),
                    fake.url() if status == "completed" else None,
                    random.uniform(0, 100),
                    datetime.now(UTC) - timedelta(days=random.randint(0, 30)),
                    random.choice([True, False])
                ))
    
    logger.info("Created course enrollments")

async def create_faqs(conn):
    """
    Create mock FAQs.
    
    Args:
        conn: Database connection
    """
    if not await check_table_empty(conn, "faqs"):
        logger.info("FAQs table is not empty, skipping")
        return
    
    logger.info(f"Creating {NUM_FAQS} mock FAQs...")
    
    # Common FAQ questions and answers
    faq_data = [
        {
            "question": "How do I reset my password?",
            "answer": "You can reset your password by clicking on the 'Forgot Password' link on the login page.",
            "category_id": "account",
            "priority": 10
        },
        {
            "question": "How do I enroll in a course?",
            "answer": "To enroll in a course, navigate to the course catalog, find the course you're interested in, and click the 'Enroll' button.",
            "category_id": "courses",
            "priority": 9
        },
        {
            "question": "Can I get a refund for a course?",
            "answer": "Refund policies vary by course. Please check the specific course details or contact support for more information.",
            "category_id": "courses",
            "priority": 8
        },
        {
            "question": "What is the grading policy?",
            "answer": "Grading policies are set by individual instructors and are outlined in the course syllabus.",
            "category_id": "courses",
            "priority": 7
        },
        {
            "question": "How do I contact my instructor?",
            "answer": "You can contact your instructor through the messaging system within the course dashboard.",
            "category_id": "faculty",
            "priority": 7
        }
    ]
    
    # Insert pre-defined FAQs
    for faq in faq_data:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO faqs (id, question, answer, category_id, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                faq["question"],
                faq["answer"],
                faq["category_id"],
                faq["priority"],
                datetime.now(UTC)
            ))
    
    # Generate additional random FAQs
    for i in range(NUM_FAQS - len(faq_data)):
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO faqs (id, question, answer, category_id, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                fake.sentence(nb_words=6, variable_nb_words=True).rstrip(".") + "?",
                fake.paragraph(nb_sentences=random.randint(2, 5)),
                random.choice(FAQ_CATEGORIES),
                random.randint(0, 10),
                datetime.now(UTC)
            ))
    
    logger.info(f"Created {NUM_FAQS} mock FAQs")

async def create_user_recommended_courses(conn, student_ids):
    """
    Create mock recommended courses for users.
    
    Args:
        conn: Database connection
        student_ids: List of student user IDs
    """
    if not await check_table_empty(conn, "user_recommended_courses"):
        logger.info("User recommended courses table is not empty, skipping")
        return
    
    logger.info("Creating user recommended courses...")
    
    recommendation_types = ["course", "tutorial", "resource"]
    
    for student_id in student_ids:
        # Create 1-3 recommendations per student
        for _ in range(random.randint(1, 3)):
            rec_type = random.choice(recommendation_types)
            
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO user_recommended_courses (
                        user_id, title, type, progress, thumbnail_path, reason, tutorial_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    student_id,
                    fake.catch_phrase(),
                    rec_type,
                    random.randint(0, 100),
                    fake.image_url(),
                    fake.paragraph(nb_sentences=1),
                    fake.url() if rec_type == "tutorial" else None
                ))
    
    logger.info("Created user recommended courses")

async def create_bookmarked_materials(conn, student_ids, course_ids):
    """
    Create mock bookmarked materials.
    
    Args:
        conn: Database connection
        student_ids: List of student user IDs
        course_ids: List of course IDs
    """
    if not await check_table_empty(conn, "bookmarked_materials"):
        logger.info("Bookmarked materials table is not empty, skipping")
        return
    
    logger.info("Creating bookmarked materials...")
    
    material_types = ["document", "video", "link", "article"]
    
    # Create random bookmarks for students
    for _ in range(min(30, len(student_ids) * len(course_ids) // 2)):
        student_id = random.choice(student_ids)
        course_id = random.choice(course_ids)
        material_type = random.choice(material_types)
            
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO bookmarked_materials (
                    user_id, title, type, author, date_bookmarked, course_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                fake.catch_phrase(),
                material_type,
                fake.name() if random.choice([True, False]) else None,
                datetime.now(UTC) - timedelta(days=random.randint(0, 60)),
                course_id
            ))
    
    logger.info("Created bookmarked materials")

async def create_assignments(conn, course_ids, faculty_ids):
    """
    Create mock assignments for courses.
    
    Args:
        conn: Database connection
        course_ids: List of course IDs
        faculty_ids: List of faculty user IDs
    """
    if not await check_table_empty(conn, "assignments"):
        logger.info("Assignments table is not empty, skipping")
        return
    
    logger.info("Creating assignments...")
    
    submission_types = ["file", "text", "url", "quiz", "project"]
    statuses = ["draft", "published", "archived"]
    
    # Get module IDs
    module_ids_by_course = {}
    async with conn.cursor() as cur:
        for course_id in course_ids:
            try:
                # Validate course_id is a valid UUID
                if not isinstance(course_id, str) or not uuid.UUID(course_id, version=4):
                    logger.warning(f"Invalid course_id format: {course_id}, skipping")
                    continue
                
                await cur.execute("SELECT id FROM module WHERE course_id = %s", (course_id,))
                results = await cur.fetchall()
                if results:
                    # Validate each module ID is a proper UUID
                    valid_module_ids = []
                    for row in results:
                        module_id = row[0]
                        if isinstance(module_id, uuid.UUID):
                            valid_module_ids.append(str(module_id))
                        elif isinstance(module_id, str):
                            try:
                                # Validate it's a valid UUID
                                uuid.UUID(module_id, version=4)
                                valid_module_ids.append(module_id)
                            except ValueError:
                                logger.warning(f"Skipping invalid module_id: {module_id}")
                        else:
                            logger.warning(f"Skipping module_id with unexpected type: {type(module_id)}")
                    
                    if valid_module_ids:
                        module_ids_by_course[course_id] = valid_module_ids
            except ValueError as e:
                logger.warning(f"Error processing course {course_id}: {str(e)}")
    
    logger.info(f"Found modules for {len(module_ids_by_course)} courses")
    
    # Create assignments for each course
    for course_id in course_ids:
        try:
            # Create 1-5 assignments per course
            for _ in range(random.randint(1, 5)):
                assignment_id = str(uuid.uuid4())
                faculty_id = random.choice(faculty_ids)
                
                # Determine if assignment belongs to a module
                module_id = None
                if course_id in module_ids_by_course and module_ids_by_course[course_id] and random.choice([True, False]):
                    module_id = random.choice(module_ids_by_course[course_id])
                    logger.debug(f"Selected module_id: {module_id} for assignment")
                
                # Set dates
                created_at = datetime.now(UTC) - timedelta(days=random.randint(10, 60))
                updated_at = created_at + timedelta(days=random.randint(1, 5))
                due_date = created_at + timedelta(days=random.randint(14, 30))
                
                # Determine if peer review is enabled
                enable_peer_review = random.choice([True, False])
                peer_review_due_date = due_date + timedelta(days=7) if enable_peer_review else None
                
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO assignments (
                            id, title, description, course_id, module_id, created_by, created_at, updated_at,
                            due_date, points, status, submission_type, allow_late_submissions, late_penalty,
                            group_submission, max_group_size, enable_peer_review, peer_reviewers_count,
                            peer_review_due_date, plagiarism_detection, file_types, max_file_size, settings
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        assignment_id,
                        fake.sentence(nb_words=6),
                        fake.paragraph(nb_sentences=random.randint(3, 8)),
                        course_id,
                        module_id,
                        faculty_id,
                        created_at,
                        updated_at,
                        due_date,
                        random.randint(5, 100),
                        random.choice(statuses),
                        random.choice(submission_types),
                        random.choice([True, False]),
                        random.uniform(0, 0.5) if random.choice([True, False]) else None,
                        random.choice([True, False]),
                        random.randint(2, 5) if random.choice([True, False]) else None,
                        enable_peer_review,
                        random.randint(1, 3) if enable_peer_review else None,
                        peer_review_due_date,
                        random.choice([True, False]),
                        ','.join(random.sample(['.pdf', '.doc', '.docx', '.zip', '.pptx'], random.randint(1, 3))),
                        random.randint(1, 25) * 1024 * 1024,  # 1-25 MB
                        '{"rubric": {"enabled": true, "criteria": []}}' if random.choice([True, False]) else None
                    ))
        except Exception as e:
            logger.error(f"Error creating assignment for course {course_id}: {str(e)}")
    
    logger.info("Created assignments")

async def create_roles_and_user_roles(conn, admin_id, faculty_ids, student_ids):
    """
    Create roles and assign them to users.
    
    Args:
        conn: Database connection
        admin_id: Admin user ID
        faculty_ids: List of faculty user IDs
        student_ids: List of student user IDs
    """
    # Check if roles table is empty
    if not await check_table_empty(conn, "roles"):
        logger.info("Roles table is not empty, skipping")
    else:
        logger.info("Creating roles...")
        
        role_names = ["admin", "faculty", "student", "support"]
        
        for role_name in role_names:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO roles (name)
                    VALUES (%s)
                """, (role_name,))
        
        logger.info("Created roles")
    
    # Check if user_roles table is empty
    if not await check_table_empty(conn, "user_roles"):
        logger.info("User roles table is not empty, skipping")
        return
    
    logger.info("Creating user role assignments...")
    
    # Get role IDs
    role_ids = {}
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, name FROM roles")
        role_results = await cur.fetchall()
        for role_id, role_name in role_results:
            role_ids[role_name] = role_id
    
    if not role_ids:
        logger.error("No roles found, skipping user role assignments")
        return
    
    # Assign admin role
    if "admin" in role_ids:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (%s, %s)
            """, (
                admin_id,
                role_ids["admin"]
            ))
    
    # Assign faculty roles
    if "faculty" in role_ids:
        for faculty_id in faculty_ids:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (%s, %s)
                """, (
                    faculty_id,
                    role_ids["faculty"]
                ))
    
    # Assign student roles
    if "student" in role_ids:
        for student_id in student_ids:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (%s, %s)
                """, (
                    student_id,
                    role_ids["student"]
                ))
    
    logger.info("Created user role assignments")

async def create_submissions(conn, student_ids):
    """
    Create mock assignment submissions.
    
    Args:
        conn: Database connection
        student_ids: List of student user IDs
    """
    if not await check_table_empty(conn, "submissions"):
        logger.info("Submissions table is not empty, skipping")
        return
    
    logger.info("Creating submissions...")
    
    # Get assignments
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, course_id, due_date FROM assignments")
        assignments = await cur.fetchall()
    
    if not assignments:
        logger.info("No assignments found, skipping submissions creation")
        return
    
    # Get course enrollments to match students with their courses
    enrollments = {}  # {course_id: [student_ids]}
    async with conn.cursor() as cur:
        await cur.execute("SELECT course_id, student_id FROM course_enrollments")
        enrollment_results = await cur.fetchall()
        
        for course_id, student_id in enrollment_results:
            if course_id not in enrollments:
                enrollments[course_id] = []
            enrollments[course_id].append(student_id)
    
    # Create submissions
    submission_statuses = ["submitted", "graded", "late", "pending_review"]
    file_types = [".pdf", ".doc", ".docx", ".zip", ".pptx", ".txt"]
    
    for assignment_id, course_id, due_date in assignments:
        # Skip if no enrollments for this course
        if course_id not in enrollments or not enrollments[course_id]:
            continue
        
        # Not all students submit assignments
        submitting_students = random.sample(
            enrollments[course_id], 
            min(len(enrollments[course_id]), random.randint(1, len(enrollments[course_id])))
        )
        
        for student_id in submitting_students:
            submission_id = str(uuid.uuid4())
            
            # Determine submission time (before or after due date)
            is_late = random.choice([True, False, False, False])  # 25% chance of late submission
            
            if due_date:
                if is_late:
                    submitted_at = due_date + timedelta(hours=random.randint(1, 72))
                else:
                    submitted_at = due_date - timedelta(hours=random.randint(1, 48))
            else:
                submitted_at = datetime.now(UTC) - timedelta(days=random.randint(1, 30))
            
            # Determine if graded
            status = random.choice(submission_statuses)
            graded_at = None
            grade = None
            feedback = None
            
            if status == "graded":
                graded_at = submitted_at + timedelta(days=random.randint(1, 7))
                grade = random.randint(60, 100)
                feedback = fake.paragraph(nb_sentences=random.randint(1, 3))
            
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO submissions (
                        id, assignment_id, student_id, submitted_at, content, file_path, 
                        file_type, status, grade, feedback, graded_at, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    submission_id,
                    assignment_id,
                    student_id,
                    submitted_at,
                    fake.paragraph() if random.choice([True, False]) else None,  # Some submissions have text content
                    f"/uploads/assignments/{assignment_id}/{student_id}/{fake.file_name()}" if random.choice([True, False]) else None,
                    random.choice(file_types) if random.choice([True, False]) else None,
                    status,
                    grade,
                    feedback,
                    graded_at,
                    submitted_at,
                    graded_at if graded_at else submitted_at
                ))
    
    logger.info("Created submissions")

async def main():
    """
    Main function to generate all mock data.
    """
    # Load environment variables
    load_dotenv()
    
    # Get connection string
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        logger.error("DATABASE_URL environment variable is not set")
        return
    
    # Ensure sslmode=require is present
    if "sslmode=require" not in connection_string:
        if "?" in connection_string:
            connection_string += "&sslmode=require"
        else:
            connection_string += "?sslmode=require"
    
    # Convert SQLAlchemy URL format to psycopg format if needed
    if "postgresql+asyncpg://" in connection_string:
        connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info(f"Connecting to database...")
    
    try:
        # Connect to the database
        async with await psycopg.AsyncConnection.connect(connection_string) as conn:
            # Create mock data
            admin_id, faculty_ids, student_ids = await create_users(conn)
            course_ids = await create_courses(conn, admin_id, faculty_ids)
            module_ids = await create_modules(conn, course_ids)
            lecture_ids = await create_lectures(conn, module_ids)
            await create_lecture_content(conn, lecture_ids)
            await create_lecture_content_docs(conn, lecture_ids)
            await create_enrollments(conn, course_ids, student_ids)
            await create_faqs(conn)
            await create_user_recommended_courses(conn, student_ids)
            await create_bookmarked_materials(conn, student_ids, course_ids)
            await create_assignments(conn, course_ids, faculty_ids)
            await create_roles_and_user_roles(conn, admin_id, faculty_ids, student_ids)
            await create_submissions(conn, student_ids)
            
            # Commit changes
            await conn.commit()
            
            logger.info("Successfully generated mock data for all tables")
    
    except Exception as e:
        logger.error(f"Error generating mock data: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting mock data generation...")
    asyncio.run(main()) 