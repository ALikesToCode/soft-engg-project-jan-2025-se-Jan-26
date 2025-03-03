from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.system_settings import SystemSettings, Integration
from app.schemas.system_settings import SystemSettings as SystemSettingsSchema
from app.schemas.system_settings import Integration as IntegrationSchema
from app.schemas.system_settings import IntegrationCreate, IntegrationUpdate
import json


async def get_system_settings(db: AsyncSession):
    """Get all system settings"""
    # Get auth settings
    auth_result = await db.execute(select(SystemSettings).where(SystemSettings.key == "auth"))
    auth_settings = auth_result.scalars().first()
    
    # Get notification settings
    notification_result = await db.execute(select(SystemSettings).where(SystemSettings.key == "notifications"))
    notification_settings = notification_result.scalars().first()
    
    # Get API settings
    api_result = await db.execute(select(SystemSettings).where(SystemSettings.key == "api"))
    api_settings = api_result.scalars().first()
    
    # Get integrations
    integrations_result = await db.execute(select(Integration))
    integrations = integrations_result.scalars().all()
    
    # Create default settings if not found
    if not auth_settings:
        auth_settings = SystemSettings(
            key="auth",
            value={
                "jwt_expiry": 24,
                "oauth_provider": "google",
                "mfa_enabled": False
            }
        )
        db.add(auth_settings)
        await db.commit()
    
    if not notification_settings:
        notification_settings = SystemSettings(
            key="notifications",
            value={
                "email_frequency": "immediate",
                "smtp_server": "smtp.example.com"
            }
        )
        db.add(notification_settings)
        await db.commit()
    
    if not api_settings:
        api_settings = SystemSettings(
            key="api",
            value={
                "rate_limit": 100,
                "data_retention_days": 30
            }
        )
        db.add(api_settings)
        await db.commit()
    
    # Construct the response
    return SystemSettingsSchema(
        auth=auth_settings.value if auth_settings else {},
        notifications=notification_settings.value if notification_settings else {},
        api=api_settings.value if api_settings else {},
        integrations=[
            IntegrationSchema(
                id=integration.id,
                name=integration.name,
                type=integration.type,
                endpoint=integration.endpoint,
                api_key=integration.api_key,
                status=integration.status
            ) for integration in integrations
        ]
    )


async def update_system_settings(db: AsyncSession, settings: SystemSettingsSchema):
    """Update system settings"""
    # Update auth settings
    auth_result = await db.execute(select(SystemSettings).where(SystemSettings.key == "auth"))
    auth_settings = auth_result.scalars().first()
    
    if auth_settings:
        auth_settings.value = settings.auth.dict()
        db.add(auth_settings)
    else:
        auth_settings = SystemSettings(
            key="auth",
            value=settings.auth.dict()
        )
        db.add(auth_settings)
    
    # Update notification settings
    notification_result = await db.execute(select(SystemSettings).where(SystemSettings.key == "notifications"))
    notification_settings = notification_result.scalars().first()
    
    if notification_settings:
        notification_settings.value = settings.notifications.dict()
        db.add(notification_settings)
    else:
        notification_settings = SystemSettings(
            key="notifications",
            value=settings.notifications.dict()
        )
        db.add(notification_settings)
    
    # Update API settings
    api_result = await db.execute(select(SystemSettings).where(SystemSettings.key == "api"))
    api_settings = api_result.scalars().first()
    
    if api_settings:
        api_settings.value = settings.api.dict()
        db.add(api_settings)
    else:
        api_settings = SystemSettings(
            key="api",
            value=settings.api.dict()
        )
        db.add(api_settings)
    
    await db.commit()
    
    return await get_system_settings(db)


async def get_integrations(db: AsyncSession):
    """Get all integrations"""
    result = await db.execute(select(Integration))
    integrations = result.scalars().all()
    
    return [
        IntegrationSchema(
            id=integration.id,
            name=integration.name,
            type=integration.type,
            endpoint=integration.endpoint,
            api_key=integration.api_key,
            status=integration.status
        ) for integration in integrations
    ]


async def get_integration(db: AsyncSession, integration_id: int):
    """Get integration by ID"""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    integration = result.scalars().first()
    
    if not integration:
        return None
    
    return IntegrationSchema(
        id=integration.id,
        name=integration.name,
        type=integration.type,
        endpoint=integration.endpoint,
        api_key=integration.api_key,
        status=integration.status
    )


async def create_integration(db: AsyncSession, integration: IntegrationCreate):
    """Create a new integration"""
    db_integration = Integration(
        name=integration.name,
        type=integration.type,
        endpoint=integration.endpoint,
        api_key=integration.api_key,
        status=integration.status
    )
    
    db.add(db_integration)
    await db.commit()
    await db.refresh(db_integration)
    
    return IntegrationSchema(
        id=db_integration.id,
        name=db_integration.name,
        type=db_integration.type,
        endpoint=db_integration.endpoint,
        api_key=db_integration.api_key,
        status=db_integration.status
    )


async def update_integration(db: AsyncSession, integration_id: int, integration: IntegrationUpdate):
    """Update an integration"""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    db_integration = result.scalars().first()
    
    if not db_integration:
        return None
    
    # Update fields if provided
    if integration.name is not None:
        db_integration.name = integration.name
    if integration.type is not None:
        db_integration.type = integration.type
    if integration.endpoint is not None:
        db_integration.endpoint = integration.endpoint
    if integration.api_key is not None:
        db_integration.api_key = integration.api_key
    if integration.status is not None:
        db_integration.status = integration.status
    
    db.add(db_integration)
    await db.commit()
    await db.refresh(db_integration)
    
    return IntegrationSchema(
        id=db_integration.id,
        name=db_integration.name,
        type=db_integration.type,
        endpoint=db_integration.endpoint,
        api_key=db_integration.api_key,
        status=db_integration.status
    )


async def delete_integration(db: AsyncSession, integration_id: int):
    """Delete an integration"""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    db_integration = result.scalars().first()
    
    if not db_integration:
        return False
    
    await db.execute(delete(Integration).where(Integration.id == integration_id))
    await db.commit()
    
    return True 