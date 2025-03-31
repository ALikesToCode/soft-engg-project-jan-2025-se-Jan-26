import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.begin() as conn:
        # Get the actual table definition from PostgreSQL
        query = text('''
        SELECT 
            column_name, 
            data_type, 
            is_nullable
        FROM 
            information_schema.columns
        WHERE 
            table_name = 'course_enrollments'
        ORDER BY 
            ordinal_position;
        ''')
        
        result = await conn.execute(query)
        columns = result.fetchall()
        
        print('=== COURSE_ENROLLMENTS TABLE DEFINITION ===')
        for col in columns:
            print(f'Column: {col[0]}, Type: {col[1]}, Nullable: {col[2]}')
        
        # Get foreign key relationships
        query = text('''
        SELECT
            tc.table_schema, 
            tc.constraint_name, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='course_enrollments';
        ''')
        
        result = await conn.execute(query)
        fkeys = result.fetchall()
        
        print('\n=== COURSE_ENROLLMENTS FOREIGN KEYS ===')
        for fk in fkeys:
            print(f'Column {fk[3]} -> {fk[5]}.{fk[6]}')
        
        # Get a sample of data
        query = text('''
        SELECT * FROM course_enrollments LIMIT 5;
        ''')
        
        result = await conn.execute(query)
        rows = result.fetchall()
        
        print('\n=== SAMPLE DATA (max 5 rows) ===')
        for row in rows:
            print(f"ID: {row[0]}, Course: {row[1]}, Student: {row[2]}, Status: {row[3]}")
            
        # SQL query that fails in the API
        print('\n=== TESTING THE SQL QUERY THAT FAILS IN API ===')
        try:
            query = text('''
            SELECT 
                u.id, 
                u.name, 
                u.email, 
                ce.status, 
                ce.enrollment_date 
            FROM 
                users u 
            JOIN 
                course_enrollments ce ON u.id = ce.student_id 
            WHERE 
                ce.course_id = :course_id
            ''')
            
            result = await conn.execute(query, {'course_id': 'bac902c5-ac37-472c-967d-dcb4fcfd54f3'})
            students = result.fetchall()
            
            print(f"Found {len(students)} students for course")
            for i, student in enumerate(students[:3]):  # Show up to 3 students
                print(f"Student {i+1}: ID={student[0]}, Name={student[1]}, Email={student[2]}, Status={student[3]}")
                
            if len(students) > 3:
                print(f"...and {len(students) - 3} more")
                
        except Exception as e:
            print(f"Query failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 