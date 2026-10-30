import asyncio
import random

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Batch, Alert
from database.sensor_models import SensorReading
from services.shelf_life import generate_shelf_life_assessment


async def generate_sensor_readings():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Batch).order_by(
                Batch.id.asc()
            )
        )

        batches = result.scalars().all()

        if not batches:
            print("No batches found.")
            return

        for batch in batches:

            temperature = round(
                random.uniform(3.0, 9.0),
                1
            )

            humidity = round(
                random.uniform(60.0, 85.0),
                1
            )

            reading = SensorReading(
                batch_id=batch.id,
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

            risk_level = assessment["risk_level"]

            print(
                f"Batch {batch.batch_code} | "
                f"{batch.product_name} | "
                f"Temperature: {temperature}°C | "
                f"Humidity: {humidity}% | "
                f"Risk: {risk_level}"
            )

            # =================================
            # AUTOMATIC ALERT GENERATION
            # =================================

            if risk_level in ["Warning", "Critical"]:

                alert_result = await db.execute(
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

                existing_alert = (
                    alert_result.scalars().first()
                )

                if existing_alert is None:

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
                            assessment[
                                "recommendation"
                            ]
                        ),
                    )

                    db.add(alert)

                    print(
                        f"  🚨 ALERT CREATED | "
                        f"{batch.batch_code} | "
                        f"{risk_level}"
                    )

        await db.commit()


async def main():

    print(
        "FreshGuard Sensor Simulator Started"
    )

    while True:

        await generate_sensor_readings()

        await asyncio.sleep(10)


if __name__ == "__main__":

    asyncio.run(main())