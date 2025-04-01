import asyncio
from app.database import async_session
from sqlalchemy import text

async def update_user_role():
    async with async_session() as session:
        # Check current user role
        query = text('SELECT id, email, name, role FROM users WHERE id = :user_id')
        result = await session.execute(query, {'user_id': 'ad9163ed-65e5-4920-94bb-25d7b5633b63'})
        user = result.fetchone()
        print(f'User: {user}')
        
        # Update user to support role if needed
        if user and user.role != 'support':
            update = text('UPDATE users SET role = :role WHERE id = :user_id')
            await session.execute(update, {'role': 'support', 'user_id': 'ad9163ed-65e5-4920-94bb-25d7b5633b63'})
            await session.commit()
            print('Updated user role to support')
            
        # Alternative: Update the support@study.iitm.ac.in user
        query = text('SELECT id, email, name, role FROM users WHERE email = :email')
        result = await session.execute(query, {'email': 'support@study.iitm.ac.in'})
        support_user = result.fetchone()
        
        if support_user:
            print(f'Support user: {support_user}')
            if support_user.role != 'support':
                update = text('UPDATE users SET role = :role WHERE email = :email')
                await session.execute(update, {'role': 'support', 'email': 'support@study.iitm.ac.in'})
                await session.commit()
                print('Updated support user role to support')
        else:
            print('Support user not found')

if __name__ == "__main__":
    asyncio.run(update_user_role()) 