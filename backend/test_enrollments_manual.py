import asyncio
import httpx
import json
from uuid import UUID

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
COURSE_ID = "bac902c5-ac37-472c-967d-dcb4fcfd54f3"  # Software Engineering course
TEST_USER = {
    "username": "kchauras.in@gmail.com",
    "password": "Complexpassword@123"
}

async def login():
    """Login to get access token"""
    try:
        # Set a timeout for the request
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{BASE_URL}/auth/login", 
                json=TEST_USER
            )
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return None
            data = response.json()
            return data.get("access_token")
    except httpx.TimeoutException:
        print("Request timed out. The server might be unreachable or overloaded.")
        return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None
        
async def get_course_students(token):
    """Test getting students enrolled in a course"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/courses/{COURSE_ID}/students",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"\n=== COURSE STUDENTS ===")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} students")
            for student in data:
                print(f"- {student['name']} ({student['email']}): {student['status']}")
        else:
            print(f"Error: {response.text}")
            
async def get_course_enrollments(token):
    """Test getting enrollments for a course"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/courses/{COURSE_ID}/enrollments",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"\n=== COURSE ENROLLMENTS ===")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} enrollments")
            for enrollment in data:
                print(f"- {enrollment['name']} ({enrollment['email']}): {enrollment['status']}")
                
                # Test getting enrollment details for the first enrollment
                if enrollment == data[0]:
                    enrollment_id = enrollment['id']
                    await get_enrollment_details(token, enrollment_id)
        else:
            print(f"Error: {response.text}")
            
async def get_enrollment_details(token, enrollment_id):
    """Test getting details for a specific enrollment"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/courses/{COURSE_ID}/enrollments/{enrollment_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"\n=== ENROLLMENT DETAILS ===")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Student: {data['name']} ({data['email']})")
            print(f"Status: {data['status']}")
            print(f"Progress: {data['progress']}")
            print(f"Assignments: {len(data['assignments'])}")
        else:
            print(f"Error: {response.text}")
            
async def get_course_progress(token):
    """Test getting progress data for a course"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/courses/{COURSE_ID}/progress",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"\n=== COURSE PROGRESS ===")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found progress data for {len(data)} students")
            for progress in data:
                print(f"- Student {progress['student_id']}: {progress['progress']}% complete, {progress['completed_assignments']}/{progress['total_assignments']} assignments")
        else:
            print(f"Error: {response.text}")

async def main():
    # Login first
    token = await login()
    if not token:
        print("Could not login, aborting tests")
        return
        
    print("Login successful!")
    
    # Run tests in sequence
    await get_course_students(token)
    await get_course_enrollments(token)
    await get_course_progress(token)
    
if __name__ == "__main__":
    asyncio.run(main()) 