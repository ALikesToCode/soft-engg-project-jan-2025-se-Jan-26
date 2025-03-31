import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.begin() as conn:
        # Get column names for course_enrollments
        query = text('''
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'course_enrollments'
        ORDER BY ordinal_position;
        ''')
        
        result = await conn.execute(query)
        columns = result.fetchall()
        
        print('=== COURSE_ENROLLMENTS COLUMNS ===')
        for col in columns:
            print(f'- {col[0]}')
            
        # Check for existence of course ID for testing
        query = text('''
        SELECT id, title, status FROM courses WHERE id = :course_id
        ''')
        
        result = await conn.execute(query, {'course_id': 'bac902c5-ac37-472c-967d-dcb4fcfd54f3'})
        course = result.fetchone()
        
        print('\n=== TEST COURSE INFO ===')
        print(f'Course exists: {course is not None}')
        if course:
            print(f'Title: {course[1]}, Status: {course[2]}')
        
        # Check for students enrolled in the course
        query = text('''
        SELECT 
            ce.id, 
            ce.student_id, 
            u.name as student_name,
            ce.status,
            ce.enrollment_date
        FROM 
            course_enrollments ce
        JOIN 
            users u ON ce.student_id = u.id
        WHERE 
            ce.course_id = :course_id
        ''')
        
        result = await conn.execute(query, {'course_id': 'bac902c5-ac37-472c-967d-dcb4fcfd54f3'})
        enrollments = result.fetchall()
        
        print('\n=== ENROLLMENTS FOR TEST COURSE ===')
        if not enrollments:
            print('No enrollments found for this course')
        else:
            for enr in enrollments:
                print(f'ID: {enr[0]}, Student ID: {enr[1]}, Name: {enr[2]}, Status: {enr[3]}, Date: {enr[4]}')

if __name__ == "__main__":
    asyncio.run(main()) 