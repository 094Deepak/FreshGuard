from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import AsyncSessionLocal
from database.models import Batch
from database.schemas import (
    BatchCreate,
    BatchResponse,
    BatchUpdate,
)


router = APIRouter(
    prefix="/api/batches",
    tags=["Batches"],
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post(
    "",
    response_model=BatchResponse,
    status_code=201,
)
async def create_batch(
    batch_data: BatchCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Batch).where(
            Batch.batch_code == batch_data.batch_code
        )
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Batch code already exists.",
        )

    if batch_data.remaining_shelf_life <= 1.5:
        status = "Critical"
    elif batch_data.remaining_shelf_life <= 3:
        status = "Warning"
    else:
        status = "Healthy"

    batch = Batch(
        batch_code=batch_data.batch_code,
        product_name=batch_data.product_name,
        temperature=batch_data.temperature,
        humidity=batch_data.humidity,
        remaining_shelf_life=batch_data.remaining_shelf_life,
        status=status,
    )

    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    return batch


@router.get(
    "",
    response_model=list[BatchResponse],
)
async def get_batches(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Batch).order_by(
            Batch.created_at.desc()
        )
    )

    return result.scalars().all()


@router.get(
    "/{batch_id}",
    response_model=BatchResponse,
)
async def get_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Batch).where(
            Batch.id == batch_id
        )
    )

    batch = result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found.",
        )

    return batch


@router.put(
    "/{batch_id}",
    response_model=BatchResponse,
)
async def update_batch(
    batch_id: int,
    batch_data: BatchUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Batch).where(
            Batch.id == batch_id
        )
    )

    batch = result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found.",
        )

    if batch_data.remaining_shelf_life <= 1.5:
        status = "Critical"
    elif batch_data.remaining_shelf_life <= 3:
        status = "Warning"
    else:
        status = "Healthy"

    batch.product_name = batch_data.product_name
    batch.temperature = batch_data.temperature
    batch.humidity = batch_data.humidity
    batch.remaining_shelf_life = batch_data.remaining_shelf_life
    batch.status = status

    await db.commit()
    await db.refresh(batch)

    return batch


@router.delete(
    "/{batch_id}",
)
async def delete_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Batch).where(
            Batch.id == batch_id
        )
    )

    batch = result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found.",
        )

    await db.delete(batch)
    await db.commit()

    return {
        "message": "Batch deleted successfully."
    }