# Assignment Management System

This document provides an overview of the Assignment Management System implemented in the backend.

## Features

1. **Assignment Creation and Management**
   - Create, update, and delete assignments
   - Set due dates, points, and submission types
   - Configure late submission policies
   - Enable group submissions and peer reviews
   - Set up plagiarism detection

2. **Submission Handling**
   - Support for file uploads, text entries, and URL submissions
   - Draft submissions for work-in-progress
   - Automatic handling of late submissions with configurable penalties

3. **Grading System**
   - Grade submissions with feedback
   - Support for rubric-based grading
   - Batch grading capabilities

4. **Plagiarism Detection**
   - Basic text similarity detection
   - File comparison for code submissions

## API Documentation

All API endpoints are fully documented and available through the Swagger UI at `/docs` when the server is running. The Swagger documentation includes:

- Detailed descriptions of each endpoint
- Required and optional parameters
- Request and response models
- Authentication requirements
- Example requests and responses

### Assignments

- `GET /api/v1/assignments?course_id={courseId}` - Get all assignments for a course
- `POST /api/v1/assignments` - Create a new assignment
- `GET /api/v1/assignments/{assignmentId}` - Get assignment details
- `PUT /api/v1/assignments/{assignmentId}` - Update an assignment
- `DELETE /api/v1/assignments/{assignmentId}` - Delete an assignment

### Submissions

- `POST /api/v1/assignments/{assignmentId}/submit` - Submit an assignment
- `GET /api/v1/assignments/{assignmentId}/submissions` - Get all submissions for an assignment
- `GET /api/v1/assignments/{assignmentId}/my-submission` - Get current user's submission
- `GET /api/v1/assignments/{assignmentId}/submissions/{submissionId}` - Get submission details
- `PUT /api/v1/assignments/{assignmentId}/grade/{submissionId}` - Grade a submission
- `GET /api/v1/assignments/{assignmentId}/submissions/{submissionId}/download` - Download submission file
- `GET /api/v1/assignments/{assignmentId}/submissions/{submissionId}/plagiarism` - Get plagiarism report

## Setup Instructions

1. **Database Migrations**
   - Run database migrations to create the necessary tables:
     ```
     alembic revision --autogenerate -m "Add assignment tables"
     alembic upgrade head
     ```

2. **Dependencies**
   - Ensure `aiofiles` is installed for file handling:
     ```
     pip install aiofiles==23.2.1
     ```

3. **File Storage**
   - Make sure the upload directory exists and has proper permissions:
     ```
     mkdir -p uploads/assignments
     chmod 755 uploads/assignments
     ```

## Usage Examples

### Creating an Assignment

```python
assignment_data = {
    "title": "Introduction to Python",
    "description": "Create a simple Python program that demonstrates basic concepts",
    "course_id": "550e8400-e29b-41d4-a716-446655440000",
    "due_date": "2023-12-31T23:59:59",
    "points": 100,
    "status": "published",
    "submission_type": "file",
    "allow_late_submissions": True,
    "late_penalty": 10,
    "plagiarism_detection": True,
    "file_types": "py,txt",
    "max_file_size": 5
}

response = requests.post(
    "http://localhost:8000/api/v1/assignments",
    json=assignment_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Submitting an Assignment

```python
import requests

# For file submission
files = {"file": open("my_solution.py", "rb")}
data = {"status": "submitted"}

response = requests.post(
    "http://localhost:8000/api/v1/assignments/550e8400-e29b-41d4-a716-446655440000/submit",
    files=files,
    data=data,
    headers={"Authorization": f"Bearer {token}"}
)

# For text submission
data = {
    "content": "This is my submission text content",
    "status": "submitted"
}

response = requests.post(
    "http://localhost:8000/api/v1/assignments/550e8400-e29b-41d4-a716-446655440000/submit",
    data=data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Grading a Submission

```python
grading_data = {
    "grade": 85,
    "feedback": "Good work, but could improve code organization"
}

response = requests.put(
    "http://localhost:8000/api/v1/assignments/550e8400-e29b-41d4-a716-446655440000/grade/550e8400-e29b-41d4-a716-446655440001",
    json=grading_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

## Frontend Integration

The frontend has been updated to work with the new backend API. The following components are available:

1. **Assignment Store** - `frontend/src/stores/assignmentStore.js`
2. **Assignment Service** - `frontend/src/services/assignment.service.js`
3. **Assignment Builder** - `frontend/src/components/content/AssignmentBuilder.vue`
4. **Assignment Model** - `frontend/src/models/Assignment.js`

## Testing the API

You can test the API using the Swagger UI:

1. Start the backend server:
   ```
   cd backend
   uvicorn main:app --reload
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

3. Authenticate using the "Authorize" button with either:
   - JWT Bearer token
   - Google OAuth2

4. Test the endpoints directly from the Swagger UI interface

Make sure to restart both the frontend and backend servers after making these changes. 