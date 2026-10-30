from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import AsyncSessionLocal
from database.models import Batch, Alert
from database.sensor_models import SensorReading
from services.shelf_life import generate_shelf_life_assessment


router = APIRouter(
    prefix="/api/monitoring",
    tags=["Monitoring"],
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/readings/{batch_id}")
async def create_sensor_reading(
    batch_id: int,
    temperature: float,
    humidity: float,
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

    reading = SensorReading(
        batch_id=batch_id,
        temperature=temperature,
        humidity=humidity,
    )

    db.add(reading)

    batch.temperature = temperature
    batch.humidity = humidity

    assessment = generate_shelf_life_assessment(
        current_shelf_life=batch.remaining_shelf_life,
        temperature=temperature,
        humidity=humidity,
        elapsed_hours=0,
    )

    batch.status = assessment["risk_level"]

    await db.commit()
    await db.refresh(reading)

    return {
        "reading": reading,
        "assessment": assessment,
    }


@router.get("/readings/{batch_id}")
async def get_sensor_readings(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SensorReading)
        .where(
            SensorReading.batch_id == batch_id
        )
        .order_by(
            SensorReading.recorded_at.asc()
        )
    )

    return result.scalars().all()


@router.get("/latest/{batch_id}")
async def get_latest_reading(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SensorReading)
        .where(
            SensorReading.batch_id == batch_id
        )
        .order_by(
            SensorReading.recorded_at.desc()
        )
    )

    reading = result.scalars().first()

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings found.",
        )

    return reading


@router.get("/assessment/{batch_id}")
async def get_shelf_life_assessment(
    batch_id: int,
    db: AsyncSession = Depends(get_db),
):
    batch_result = await db.execute(
        select(Batch).where(
            Batch.id == batch_id
        )
    )

    batch = batch_result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found.",
        )

    reading_result = await db.execute(
        select(SensorReading)
        .where(
            SensorReading.batch_id == batch_id
        )
        .order_by(
            SensorReading.recorded_at.desc()
        )
    )

    latest_reading = reading_result.scalars().first()

    if latest_reading is None:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings found.",
        )

    now = datetime.now(timezone.utc)

    recorded_at = latest_reading.recorded_at

    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(
            tzinfo=timezone.utc
        )

    elapsed_hours = (
        now - recorded_at
    ).total_seconds() / 3600

    assessment = generate_shelf_life_assessment(
        current_shelf_life=batch.remaining_shelf_life,
        temperature=latest_reading.temperature,
        humidity=latest_reading.humidity,
        elapsed_hours=elapsed_hours,
    )

    return {
        "batch_id": batch.id,
        "batch_code": batch.batch_code,
        "product_name": batch.product_name,
        "temperature": latest_reading.temperature,
        "humidity": latest_reading.humidity,
        **assessment,
    }


# ============================================================
# ANALYTICS
# ============================================================

@router.get("/analytics")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
):
    """
    Return overall FreshGuard analytics.

    Uses historical sensor readings and alert records
    already stored in the database.
    """

    # --------------------------------------------------------
    # Total sensor readings
    # --------------------------------------------------------

    reading_count_result = await db.execute(
        select(
            func.count(SensorReading.id)
        )
    )

    total_readings = (
        reading_count_result.scalar() or 0
    )

    # --------------------------------------------------------
    # Average temperature
    # --------------------------------------------------------

    temperature_result = await db.execute(
        select(
            func.avg(
                SensorReading.temperature
            )
        )
    )

    average_temperature = (
        temperature_result.scalar()
    )

    # --------------------------------------------------------
    # Average humidity
    # --------------------------------------------------------

    humidity_result = await db.execute(
        select(
            func.avg(
                SensorReading.humidity
            )
        )
    )

    average_humidity = (
        humidity_result.scalar()
    )

    # --------------------------------------------------------
    # Temperature extremes
    # --------------------------------------------------------

    temperature_min_result = await db.execute(
        select(
            func.min(
                SensorReading.temperature
            )
        )
    )

    temperature_max_result = await db.execute(
        select(
            func.max(
                SensorReading.temperature
            )
        )
    )

    minimum_temperature = (
        temperature_min_result.scalar()
    )

    maximum_temperature = (
        temperature_max_result.scalar()
    )

    # --------------------------------------------------------
    # Humidity extremes
    # --------------------------------------------------------

    humidity_min_result = await db.execute(
        select(
            func.min(
                SensorReading.humidity
            )
        )
    )

    humidity_max_result = await db.execute(
        select(
            func.max(
                SensorReading.humidity
            )
        )
    )

    minimum_humidity = (
        humidity_min_result.scalar()
    )

    maximum_humidity = (
        humidity_max_result.scalar()
    )

    # --------------------------------------------------------
    # Batch count
    # --------------------------------------------------------

    batch_count_result = await db.execute(
        select(
            func.count(Batch.id)
        )
    )

    total_batches = (
        batch_count_result.scalar() or 0
    )

    # --------------------------------------------------------
    # Active alerts
    # --------------------------------------------------------

    active_alert_result = await db.execute(
        select(
            func.count(Alert.id)
        )
        .where(
            Alert.resolved == False
        )
    )

    active_alerts = (
        active_alert_result.scalar() or 0
    )

    # --------------------------------------------------------
    # Critical alerts
    # --------------------------------------------------------

    critical_alert_result = await db.execute(
        select(
            func.count(Alert.id)
        )
        .where(
            Alert.severity == "Critical",
            Alert.resolved == False,
        )
    )

    critical_alerts = (
        critical_alert_result.scalar() or 0
    )

    # --------------------------------------------------------
    # Warning alerts
    # --------------------------------------------------------

    warning_alert_result = await db.execute(
        select(
            func.count(Alert.id)
        )
        .where(
            Alert.severity == "Warning",
            Alert.resolved == False,
        )
    )

    warning_alerts = (
        warning_alert_result.scalar() or 0
    )

    # --------------------------------------------------------
    # Resolved alerts
    # --------------------------------------------------------

    resolved_alert_result = await db.execute(
        select(
            func.count(Alert.id)
        )
        .where(
            Alert.resolved == True
        )
    )

    resolved_alerts = (
        resolved_alert_result.scalar() or 0
    )

    # --------------------------------------------------------
    # Return analytics
    # --------------------------------------------------------

    return {
        "total_batches": total_batches,

        "total_sensor_readings": total_readings,

        "temperature": {
            "average": (
                round(
                    float(average_temperature),
                    2,
                )
                if average_temperature is not None
                else None
            ),
            "minimum": (
                round(
                    float(minimum_temperature),
                    2,
                )
                if minimum_temperature is not None
                else None
            ),
            "maximum": (
                round(
                    float(maximum_temperature),
                    2,
                )
                if maximum_temperature is not None
                else None
            ),
        },

        "humidity": {
            "average": (
                round(
                    float(average_humidity),
                    2,
                )
                if average_humidity is not None
                else None
            ),
            "minimum": (
                round(
                    float(minimum_humidity),
                    2,
                )
                if minimum_humidity is not None
                else None
            ),
            "maximum": (
                round(
                    float(maximum_humidity),
                    2,
                )
                if maximum_humidity is not None
                else None
            ),
        },

        "alerts": {
            "active": active_alerts,
            "critical": critical_alerts,
            "warning": warning_alerts,
            "resolved": resolved_alerts,
        },
    }