import pytest
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Test constants
BASE_URL = "/api/v1"
COURSES_ENDPOINT = f"{BASE_URL}/courses"

# Test fixtures
@pytest.fixture
async def test_course(db_session, test_users):
    """Create a test course for testing"""
    from app.models.course import Course, CourseStatus
    
    course = Course(
        id=uuid.uuid4(),
        name="Test Course",
        code="TEST101",
        title="Test Course Title",
        credits=3,
        duration=16,
        semester="Fall",
        year=2025,
        faculty_id=test_users["faculty"].id,
        created_by=test_users["faculty"].id,
        syllabus="Test syllabus",
        description="Test description",
        status=CourseStatus.ACTIVE
    )
    
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    
    return course

# Fixture for course enrollment
@pytest.fixture
async def test_enrollment(db_session, test_course, test_users):
    """Create a test course enrollment for testing"""
    from app.models.course import CourseEnrollment
    
    enrollment = CourseEnrollment(
        id=uuid.uuid4(),
        course_id=test_course.id,
        student_id=test_users["student"].id
    )
    
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)
    
    return enrollment

# Mock course data for testing
@pytest.fixture
def course_data():
    return {
        "name": "New Test Course",
        "code": "TEST102",
        "title": "New Test Course Title",
        "credits": 4,
        "duration": 12,
        "semester": "Spring",
        "year": 2025,
        "syllabus": "New test syllabus",
        "description": "New test description"
    }

# 4.1 Create Course Endpoint Tests
@pytest.mark.asyncio
class TestCreateCourse:
    
    async def test_create_course_with_faculty_token(self, client, tokens, course_data):
        """Test creating a course with a faculty token"""
        # Add faculty_id and created_by to course_data
        response = client.post(
            COURSES_ENDPOINT, 
            json=course_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        
    async def test_create_course_with_student_token(self, client, tokens, course_data):
        """Test creating a course with a student token should return 403 Forbidden"""
        response = client.post(
            COURSES_ENDPOINT, 
            json=course_data, 
            headers={"Authorization": f"Bearer {tokens['student']}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_create_course_with_invalid_data(self, client, tokens, course_data):
        """Test creating a course with invalid data should return 422 Unprocessable Entity"""
        # Remove required field
        invalid_data = course_data.copy()
        invalid_data.pop("name")
        
        response = client.post(
            COURSES_ENDPOINT, 
            json=invalid_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# 4.2 Get Courses Endpoint Tests
@pytest.mark.asyncio
class TestGetCourses:
    
    async def test_get_courses_with_faculty_token(self, client, tokens, test_course):
        """Test getting courses with a faculty token should return a list of faculty's courses"""
        response = client.get(
            COURSES_ENDPOINT, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
    async def test_get_courses_with_student_token(self, client, tokens, test_enrollment):
        """Test getting courses with a student token should return a list of enrolled courses"""
        response = client.get(
            COURSES_ENDPOINT, 
            headers={"Authorization": f"Bearer {tokens['student']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
    async def test_get_courses_with_invalid_token(self, client):
        """Test getting courses with an invalid token should return 401 Unauthorized"""
        response = client.get(
            COURSES_ENDPOINT, 
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

# 4.3 Get Course by ID Endpoint Tests
@pytest.mark.asyncio
class TestGetCourseById:
    
    async def test_get_course_with_faculty_token(self, client, tokens, test_course):
        """Test getting a course by ID with a faculty token (owner) should return the course details"""
        course_id = str(test_course.id)
        response = client.get(
            f"{COURSES_ENDPOINT}/{course_id}",
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == course_id
        
    async def test_get_course_with_student_token(self, client, tokens, test_enrollment):
        """Test getting a course by ID with a student token (enrolled) should return the course details"""
        course_id = str(test_enrollment.course_id)
        response = client.get(
            f"{COURSES_ENDPOINT}/{course_id}", 
            headers={"Authorization": f"Bearer {tokens['student']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == course_id
        
    async def test_get_course_with_unauthorized_user(self, client, tokens, test_course):
        """Test getting a course by ID with an unauthorized user should return 403 Forbidden"""
        # Create a new user who is not enrolled or the owner
        support_token = tokens["support"]
        course_id = str(test_course.id)
        
        response = client.get(
            f"{COURSES_ENDPOINT}/{course_id}", 
            headers={"Authorization": f"Bearer {support_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_get_course_with_invalid_id(self, client, tokens):
        """Test getting a course by ID with an invalid ID should return 404 Not Found"""
        invalid_id = str(uuid.uuid4())
        response = client.get(
            f"{COURSES_ENDPOINT}/{invalid_id}", 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

# 4.4 Update Course Endpoint Tests
@pytest.mark.asyncio
class TestUpdateCourse:
    
    async def test_update_course_with_faculty_token(self, client, tokens, test_course):
        """Test updating a course with a faculty token (owner) should return success message"""
        course_id = str(test_course.id)
        update_data = {
            "name": "Updated Course Name",
            "description": "Updated description"
        }
        
        response = client.put(
            f"{COURSES_ENDPOINT}/{course_id}", 
            json=update_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
    async def test_update_course_with_student_token(self, client, tokens, test_course):
        """Test updating a course with a student token should return 403 Forbidden"""
        course_id = str(test_course.id)
        update_data = {
            "name": "Unauthorized Update",
            "description": "This shouldn't work"
        }
        
        response = client.put(
            f"{COURSES_ENDPOINT}/{course_id}", 
            json=update_data, 
            headers={"Authorization": f"Bearer {tokens['student']}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_update_course_with_different_faculty(self, client, tokens, test_course):
        """Test updating a course with a different faculty token should return 403 Forbidden"""
        # For this test, we'll use support user to simulate a different faculty
        course_id = str(test_course.id)
        update_data = {
            "name": "Unauthorized Update",
            "description": "This shouldn't work"
        }
        
        response = client.put(
            f"{COURSES_ENDPOINT}/{course_id}", 
            json=update_data, 
            headers={"Authorization": f"Bearer {tokens['support']}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_update_course_with_invalid_id(self, client, tokens):
        """Test updating a course with an invalid ID should return 404 Not Found"""
        invalid_id = str(uuid.uuid4())
        update_data = {
            "name": "Update Invalid Course",
            "description": "This course doesn't exist"
        }
        
        response = client.put(
            f"{COURSES_ENDPOINT}/{invalid_id}", 
            json=update_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

# 4.5 Delete Course Endpoint Tests
@pytest.mark.asyncio
class TestDeleteCourse:
    
    async def test_delete_course_with_faculty_token(self, client, tokens, test_course):
        """Test deleting a course with a faculty token (owner) should return success message"""
        course_id = str(test_course.id)
        
        response = client.delete(
            f"{COURSES_ENDPOINT}/{course_id}", 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
    async def test_delete_course_with_student_token(self, client, tokens, test_course):
        """Test deleting a course with a student token should return 403 Forbidden"""
        course_id = str(test_course.id)
        
        response = client.delete(
            f"{COURSES_ENDPOINT}/{course_id}", 
            headers={"Authorization": f"Bearer {tokens['student']}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_delete_course_with_different_faculty(self, client, tokens, test_course):
        """Test deleting a course with a different faculty token should return 403 Forbidden"""
        # For this test, we'll use support user to simulate a different faculty
        course_id = str(test_course.id)
        
        response = client.delete(
            f"{COURSES_ENDPOINT}/{course_id}", 
            headers={"Authorization": f"Bearer {tokens['support']}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_delete_course_with_invalid_id(self, client, tokens):
        """Test deleting a course with an invalid ID should return 404 Not Found"""
        invalid_id = str(uuid.uuid4())
        
        response = client.delete(
            f"{COURSES_ENDPOINT}/{invalid_id}", 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

# 4.6 Enroll Student Endpoint Tests
@pytest.mark.asyncio
class TestEnrollStudent:
    
    async def test_enroll_student_with_faculty_token(self, client, tokens, test_course, test_users):
        """Test enrolling a student with a faculty token should return success message"""
        course_id = str(test_course.id)
        enrollment_data = {
            "student_id": str(test_users["student"].id)
        }
        
        response = client.post(
            f"{COURSES_ENDPOINT}/{course_id}/enroll", 
            json=enrollment_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
    async def test_enroll_student_with_student_token(self, client, tokens, test_course, test_users):
        """Test enrolling a student with a student token should return 403 Forbidden"""
        course_id = str(test_course.id)
        enrollment_data = {
            "student_id": str(test_users["student"].id)
        }
        
        response = client.post(
            f"{COURSES_ENDPOINT}/{course_id}/enroll", 
            json=enrollment_data, 
            headers={"Authorization": f"Bearer {tokens['student']}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    async def test_enroll_student_with_invalid_course_id(self, client, tokens, test_users):
        """Test enrolling a student with an invalid course ID should return 404 Not Found"""
        invalid_id = str(uuid.uuid4())
        enrollment_data = {
            "student_id": str(test_users["student"].id)
        }
        
        response = client.post(
            f"{COURSES_ENDPOINT}/{invalid_id}/enroll", 
            json=enrollment_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    async def test_enroll_student_with_invalid_student_id(self, client, tokens, test_course):
        """Test enrolling a student with an invalid student ID should return 404 Not Found"""
        course_id = str(test_course.id)
        enrollment_data = {
            "student_id": str(uuid.uuid4())
        }
        
        response = client.post(
            f"{COURSES_ENDPOINT}/{course_id}/enroll", 
            json=enrollment_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    async def test_enroll_already_enrolled_student(self, client, tokens, test_enrollment):
        """Test enrolling an already enrolled student should return 400 Bad Request"""
        course_id = str(test_enrollment.course_id)
        enrollment_data = {
            "student_id": str(test_enrollment.student_id)
        }
        
        response = client.post(
            f"{COURSES_ENDPOINT}/{course_id}/enroll", 
            json=enrollment_data, 
            headers={"Authorization": f"Bearer {tokens['faculty']}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST 