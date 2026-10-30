from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import AsyncSessionLocal
from database.models import Batch, Alert
from database.sensor_models import SensorReading
from services.shelf_life import generate_shelf_life_assessment


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"],
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class HumanDecisionRequest(BaseModel):
    decision: str
    comment: str | None = None


async def create_or_update_alert(
    db: AsyncSession,
    batch: Batch,
    assessment: dict,
):
    risk_level = assessment["risk_level"]

    if risk_level not in ["Warning", "Critical"]:
        return None

    existing_result = await db.execute(
        select(Alert)
        .where(
            Alert.batch_id == batch.id,
            Alert.resolved == False,
            Alert.severity == risk_level,
        )
        .order_by(
            Alert.created_at.desc()
        )
    )

    existing_alert = existing_result.scalars().first()

    if existing_alert is not None:

        existing_alert.estimated_remaining_shelf_life = (
            assessment[
                "estimated_remaining_shelf_life"
            ]
        )

        existing_alert.environmental_stress_score = (
            assessment[
                "environmental_stress_score"
            ]
        )

        existing_alert.recommendation = (
            assessment["recommendation"]
        )

        return existing_alert

    if risk_level == "Critical":
        message = (
            "Immediate attention required. "
            "This batch is in a critical condition."
        )
    else:
        message = (
            "This batch is approaching "
            "a critical condition."
        )

    alert = Alert(
        batch_id=batch.id,
        batch_code=batch.batch_code,
        product_name=batch.product_name,
        severity=risk_level,
        message=message,
        estimated_remaining_shelf_life=(
            assessment[
                "estimated_remaining_shelf_life"
            ]
        ),
        environmental_stress_score=(
            assessment[
                "environmental_stress_score"
            ]
        ),
        recommendation=(
            assessment["recommendation"]
        ),
    )

    db.add(alert)

    return alert


@router.get("")
async def get_alerts(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert)
        .where(
            Alert.resolved == False
        )
        .order_by(
            Alert.created_at.desc()
        )
    )

    alerts = result.scalars().all()

    return [
        {
            "id": alert.id,
            "batch_id": alert.batch_id,
            "batch_code": alert.batch_code,
            "product_name": alert.product_name,
            "severity": alert.severity,
            "message": alert.message,
            "estimated_remaining_shelf_life": (
                alert.estimated_remaining_shelf_life
            ),
            "environmental_stress_score": (
                alert.environmental_stress_score
            ),
            "recommendation": (
                alert.recommendation
            ),
            "created_at": alert.created_at,
            "resolved": alert.resolved,
            "review_status": alert.review_status,
            "human_decision": alert.human_decision,
            "review_comment": alert.review_comment,
        }
        for alert in alerts
    ]


@router.post("/generate/{batch_id}")
async def generate_alert_for_batch(
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

    recorded_at = latest_reading.recorded_at

    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(timezone.utc)

    elapsed_hours = (
        now - recorded_at
    ).total_seconds() / 3600

    assessment = generate_shelf_life_assessment(
        current_shelf_life=(
            batch.remaining_shelf_life
        ),
        temperature=(
            latest_reading.temperature
        ),
        humidity=(
            latest_reading.humidity
        ),
        elapsed_hours=elapsed_hours,
    )

    alert = await create_or_update_alert(
        db=db,
        batch=batch,
        assessment=assessment,
    )

    await db.commit()

    if alert is None:
        return {
            "message": "No alert required.",
            "risk_level": assessment[
                "risk_level"
            ],
        }

    await db.refresh(alert)

    return {
        "message": "Alert generated successfully.",
        "alert": {
            "id": alert.id,
            "batch_id": alert.batch_id,
            "batch_code": alert.batch_code,
            "product_name": alert.product_name,
            "severity": alert.severity,
            "message": alert.message,
            "estimated_remaining_shelf_life": (
                alert.estimated_remaining_shelf_life
            ),
            "environmental_stress_score": (
                alert.environmental_stress_score
            ),
            "recommendation": (
                alert.recommendation
            ),
            "created_at": alert.created_at,
            "resolved": alert.resolved,
            "review_status": alert.review_status,
            "human_decision": alert.human_decision,
            "review_comment": alert.review_comment,
        },
    }


@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).where(
            Alert.id == alert_id
        )
    )

    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found.",
        )

    alert.resolved = True
    alert.review_status = "Reviewed"
    alert.human_decision = "Accepted"

    await db.commit()
    await db.refresh(alert)

    return {
        "message": "Alert resolved successfully.",
        "alert_id": alert.id,
        "resolved": alert.resolved,
        "review_status": alert.review_status,
        "human_decision": alert.human_decision,
    }


@router.put("/{alert_id}/decision")
async def record_human_decision(
    alert_id: int,
    decision_data: HumanDecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).where(
            Alert.id == alert_id
        )
    )

    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found.",
        )

    allowed_decisions = [
        "Accepted",
        "Rejected",
        "Escalated",
    ]

    if decision_data.decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid decision. "
                "Use Accepted, Rejected, or Escalated."
            ),
        )

    alert.human_decision = (
        decision_data.decision
    )

    alert.review_comment = (
        decision_data.comment
    )

    alert.review_status = (
        "Escalated"
        if decision_data.decision == "Escalated"
        else "Reviewed"
    )

    if decision_data.decision in [
        "Accepted",
        "Rejected",
    ]:
        alert.resolved = True

    await db.commit()
    await db.refresh(alert)

    return {
        "message": "Human decision recorded successfully.",
        "alert": {
            "id": alert.id,
            "batch_id": alert.batch_id,
            "batch_code": alert.batch_code,
            "product_name": alert.product_name,
            "severity": alert.severity,
            "review_status": alert.review_status,
            "human_decision": alert.human_decision,
            "review_comment": alert.review_comment,
            "resolved": alert.resolved,
        },
    }