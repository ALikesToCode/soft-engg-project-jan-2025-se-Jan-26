import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.begin() as conn:
        # Get table columns
        print("=== TABLE SCHEMAS ===")
        tables = ["course_enrollments", "users", "courses"]
        
        for table in tables:
            query = text(f"""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = :table
            ORDER BY ordinal_position;
            """)
            
            result = await conn.execute(query, {"table": table})
            rows = result.fetchall()
            
            print(f"\n{table}:")
            for row in rows:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  - {row[0]}: {row[1]} {nullable}")
        
        # Get foreign key relationships
        print("\n=== FOREIGN KEY RELATIONSHIPS ===")
        fk_query = text("""
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS referenced_table, 
            ccu.column_name AS referenced_column
        FROM 
            information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE 
            tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name IN ('course_enrollments', 'users', 'courses');
        """)
        
        result = await conn.execute(fk_query)
        for row in result:
            print(f"{row[0]}.{row[1]} -> {row[2]}.{row[3]}")

if __name__ == "__main__":
    asyncio.run(main()) 