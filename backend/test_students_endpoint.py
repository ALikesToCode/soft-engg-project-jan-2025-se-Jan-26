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

async def test_students_endpoint():
    """Test the students endpoint specifically"""
    session = None
    try:
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        
        print("Logging in to get auth token...")
        # Use form data format instead of JSON
        form_data = aiohttp.FormData()
        form_data.add_field('username', 'faculty@study.iitm.ac.in')
        form_data.add_field('password', 'faculty123')
        
        async with session.post(f"{API_BASE}/api/v1/auth/login", data=form_data) as response:
            if response.status != 200:
                print(f"Login failed with status {response.status}")
                body = await response.text()
                print(f"Response: {body}")
                return False
            
            data = await response.json()
            token = data.get("access_token")
            if not token:
                print("No token received in response")
                return False
            
            print("Successfully logged in")
        
        # Use a hardcoded test course ID
        course_id = "123e4567-e89b-12d3-a456-426614174000"
        print(f"Using test course ID: {course_id}")
        
        # Test students endpoint
        print(f"\nTesting get students for course {course_id}...")
        headers = {"Authorization": f"Bearer {token}"}
        
        async with session.get(
            f"{API_BASE}/api/v1/courses/{course_id}/students", 
            headers=headers
        ) as response:
            status = response.status
            body = await response.text()
            
            print(f"Status: {status}")
            if status == 200:
                try:
                    data = json.loads(body)
                    print(f"Successfully retrieved {len(data)} students")
                    return True
                except json.JSONDecodeError:
                    print(f"Error decoding JSON response: {body}")
                    return False
            else:
                print(f"Failed to get students with status {status}: {body}")
                return False
                
    except Exception as e:
        print(f"Error testing students endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if session and not session.closed:
            await session.close()
            print("HTTP session closed")

async def main():
    """Main function to run the tests"""
    success = await test_students_endpoint()
    if success:
        print("\nTest passed successfully!")
        sys.exit(0)
    else:
        print("\nTest failed. See output above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 