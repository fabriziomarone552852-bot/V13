from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

async def ensure_system_ready(db: AsyncSession) -> None:
    repo = SystemBootRepository(db)
    metadata = await repo.get_system_metadata()

    if not metadata or metadata["boot_status"] != "READY":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System boot not completed",
        )