from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.system_settings import SystemSettings, Integration, IntegrationCreate, IntegrationUpdate
from app.services.system_settings_service import (
    get_system_settings,
    update_system_settings,
    get_integrations,
    get_integration,
    create_integration,
    update_integration,
    delete_integration
)
from app.routes.auth import require_role

# Remove the prefix from the router, it will be added in main.py
router = APIRouter()


@router.get("/admin/settings", response_model=SystemSettings)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Get all system settings
    """
    return await get_system_settings(db)


@router.put("/admin/settings", response_model=SystemSettings)
async def update_settings(
    settings: SystemSettings,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Update system settings
    """
    return await update_system_settings(db, settings)


@router.get("/admin/integrations", response_model=list[Integration])
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Get all integrations
    """
    return await get_integrations(db)


@router.get("/admin/integrations/{integration_id}", response_model=Integration)
async def get_integration_by_id(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Get integration by ID
    """
    integration = await get_integration(db, integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    return integration


@router.post("/admin/integrations", response_model=Integration, status_code=status.HTTP_201_CREATED)
async def add_integration(
    integration: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Create a new integration
    """
    return await create_integration(db, integration)


@router.put("/admin/integrations/{integration_id}", response_model=Integration)
async def update_integration_by_id(
    integration_id: int,
    integration: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Update an integration
    """
    updated_integration = await update_integration(db, integration_id, integration)
    if not updated_integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    return updated_integration


@router.delete("/admin/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration_by_id(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_role("support"))
):
    """
    Delete an integration
    """
    success = await delete_integration(db, integration_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    return None 