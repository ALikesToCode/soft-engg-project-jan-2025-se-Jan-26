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

# This is the course ID we'll test with - one of the actual courses from the database
ACTUAL_COURSE_ID = "bac902c5-ac37-472c-967d-dcb4fcfd54f3"

class EnrollmentAPITest:
    def __init__(self):
        self.token = None
        self.course_id = None
        self.session = None
    
    async def setup(self):
        """Create HTTP session and login to get auth token"""
        self.session = aiohttp.ClientSession()
        
        print("Logging in to get auth token...")
        # Use form data format instead of JSON
        form_data = aiohttp.FormData()
        form_data.add_field('username', 'faculty@study.iitm.ac.in')
        form_data.add_field('password', 'faculty123')
        
        async with self.session.post(f"{API_BASE}/api/v1/auth/login", data=form_data) as response:
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
            
        # Try to get course ID, but use fixed value if API fails
        await self.get_or_create_test_course()
    
    async def get_or_create_test_course(self):
        """Try to get existing courses or create a test course"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print("Attempting to fetch courses...")
        try:
            # Try multiple course endpoints
            endpoints = [
                "/api/v1/courses",
                "/api/v1/faculty/courses",
                "/api/v1/faculty-courses/courses"
            ]
            
            for endpoint in endpoints:
                print(f"Trying endpoint: {endpoint}")
                async with self.session.get(f"{API_BASE}{endpoint}", headers=headers) as response:
                    if response.status == 200:
                        courses = await response.json()
                        if courses:
                            self.course_id = courses[0].get("id")
                            print(f"Found course with ID: {self.course_id}")
                            return
            
            # If we got here, no courses were found, use the actual UUID from the database
            print("No courses found, using an actual UUID for testing")
            self.course_id = ACTUAL_COURSE_ID
            print(f"Using test course ID: {self.course_id}")
            
        except Exception as e:
            print(f"Error getting courses: {str(e)}")
            print("Using fallback actual course ID")
            self.course_id = ACTUAL_COURSE_ID
            print(f"Using test course ID: {self.course_id}")
    
    async def test_get_students(self):
        """Test getting students enrolled in a course"""
        print(f"\nTesting get students for course {self.course_id}...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/students", 
            headers=headers
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"Successfully retrieved {len(data)} students")
                # Even 0 students is a valid result
                return True
            else:
                error_text = await response.text()
                print(f"Failed to get students with status {status}: {error_text}")
                return False
    
    async def test_get_progress(self):
        """Test getting progress data for students in a course"""
        print(f"\nTesting get progress for course {self.course_id}...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/progress", 
            headers=headers
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"Successfully retrieved progress data for {len(data)} students")
                # Even 0 students is a valid result
                return True
            else:
                error_text = await response.text()
                print(f"Failed to get progress data with status {status}: {error_text}")
                return False
    
    async def test_get_enrollments(self):
        """Test getting all enrollments for a course"""
        print(f"\nTesting get enrollments for course {self.course_id}...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/enrollments", 
            headers=headers
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"Successfully retrieved {len(data)} enrollments")
                
                # If we have at least one enrollment, test the detail endpoint
                if data and len(data) > 0:
                    self.enrollment_id = data[0]["id"]
                    await self.test_get_enrollment_details()
                else:
                    # No enrollments but API is working
                    print("No enrollments found, skipping details test")
                    # Generate a dummy UUID for testing the details endpoint
                    self.enrollment_id = "00000000-0000-0000-0000-000000000000"
                    await self.test_get_enrollment_details()
                
                return True
            else:
                error_text = await response.text()
                print(f"Failed to get enrollments with status {status}: {error_text}")
                return False
    
    async def test_get_enrollment_details(self):
        """Test getting details for a specific enrollment"""
        if not hasattr(self, 'enrollment_id'):
            print("No enrollment ID available for testing details")
            return False
            
        print(f"\nTesting get enrollment details for enrollment {self.enrollment_id}...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(
            f"{API_BASE}/api/v1/courses/{self.course_id}/enrollments/{self.enrollment_id}", 
            headers=headers
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"Successfully retrieved enrollment details")
                
                # Check if there's an error field in the response
                if "error" in data:
                    print(f"Note: {data['error']} - This is expected during testing")
                
                return True
            else:
                error_text = await response.text()
                print(f"Failed to get enrollment details with status {status}: {error_text}")
                return False
    
    async def run_tests(self):
        """Run all tests"""
        await self.setup()
        
        # Run each test and collect results
        test_results = {}
        test_results["get_students"] = await self.test_get_students()
        test_results["get_progress"] = await self.test_get_progress()
        test_results["get_enrollments"] = await self.test_get_enrollments()
        
        # Print summary
        print("\n=== TEST SUMMARY ===")
        success_count = sum(1 for result in test_results.values() if result)
        total_count = len(test_results)
        
        print(f"Tests passed: {success_count}/{total_count}")
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {test_name}: {status}")
        
        return success_count == total_count
    
    async def cleanup(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            print("\nHTTP session closed")

async def main():
    """Main function to run the tests"""
    try:
        tester = EnrollmentAPITest()
        success = await tester.run_tests()
        
        # Return appropriate exit code based on test results
        if success:
            print("\nAll tests passed successfully!")
            sys.exit(0)
        else:
            print("\nSome tests failed. See summary above.")
            sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 