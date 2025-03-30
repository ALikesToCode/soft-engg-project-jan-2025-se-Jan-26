#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import sys
from uuid import UUID
import os
from datetime import datetime

# Get API base URL from environment or use default
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

class EnrollmentAPITest:
    def __init__(self):
        self.token = None
        self.course_id = None
        self.session = None
    
    async def setup(self):
        """Create HTTP session and login to get auth token"""
        self.session = aiohttp.ClientSession()
        
        print("Logging in to get auth token...")
        login_data = {
            "username": "faculty@example.com",
            "password": "faculty123"
        }
        
        async with self.session.post(f"{API_BASE}/api/v1/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"Login failed with status {response.status}")
                body = await response.text()
                print(f"Response: {body}")
                sys.exit(1)
            
            data = await response.json()
            self.token = data.get("access_token")
            if not self.token:
                print("No token received in response")
                sys.exit(1)
            
            print("Successfully logged in")
            
        # Get a course ID to test with
        print("Fetching courses...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(f"{API_BASE}/api/v1/courses", headers=headers) as response:
            if response.status != 200:
                print(f"Failed to fetch courses with status {response.status}")
                sys.exit(1)
            
            courses = await response.json()
            if not courses:
                print("No courses found")
                sys.exit(1)
            
            self.course_id = courses[0].get("id")
            print(f"Using course ID: {self.course_id}")
    
    async def test_get_students(self):
        """Test the students endpoint"""
        print("\n--- Testing GET /api/v1/courses/{course_id}/students ---")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/students", 
            headers=headers
        ) as response:
            status = response.status
            body = await response.text()
            
            print(f"Status: {status}")
            if status == 200:
                data = json.loads(body)
                print(f"Found {len(data)} students")
                if data:
                    print("Sample student data:")
                    print(json.dumps(data[0], indent=2))
            else:
                print(f"Response: {body}")
    
    async def test_get_progress(self):
        """Test the progress endpoint"""
        print("\n--- Testing GET /api/v1/courses/{course_id}/progress ---")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/progress", 
            headers=headers
        ) as response:
            status = response.status
            body = await response.text()
            
            print(f"Status: {status}")
            if status == 200:
                data = json.loads(body)
                print(f"Found progress data for {len(data)} students")
                if data:
                    print("Sample progress data:")
                    print(json.dumps(data[0], indent=2))
            else:
                print(f"Response: {body}")
    
    async def test_get_enrollments(self):
        """Test the enrollments endpoint"""
        print("\n--- Testing GET /api/v1/courses/{course_id}/enrollments ---")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/enrollments", 
            headers=headers
        ) as response:
            status = response.status
            body = await response.text()
            
            print(f"Status: {status}")
            if status == 200:
                data = json.loads(body)
                print(f"Found {len(data)} enrollments")
                if data:
                    enrollment_id = data[0].get("id")
                    print(f"Using enrollment ID: {enrollment_id} for next test")
                    print("Sample enrollment data:")
                    print(json.dumps(data[0], indent=2))
                    
                    # Test the enrollment details endpoint
                    await self.test_get_enrollment_details(enrollment_id)
            else:
                print(f"Response: {body}")
    
    async def test_get_enrollment_details(self, enrollment_id):
        """Test the enrollment details endpoint"""
        print(f"\n--- Testing GET /api/v1/courses/{self.course_id}/enrollments/{enrollment_id} ---")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/enrollments/{enrollment_id}", 
            headers=headers
        ) as response:
            status = response.status
            body = await response.text()
            
            print(f"Status: {status}")
            if status == 200:
                data = json.loads(body)
                print("Enrollment details:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Response: {body}")
    
    async def run_tests(self):
        """Run all API tests"""
        await self.setup()
        await self.test_get_students()
        await self.test_get_progress()
        await self.test_get_enrollments()
        # Note: test_get_enrollment_details is called from test_get_enrollments
    
    async def cleanup(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            print("\nClosed HTTP session")

async def main():
    test = EnrollmentAPITest()
    try:
        await test.run_tests()
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 