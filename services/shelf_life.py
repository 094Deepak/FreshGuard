def calculate_environmental_stress(
    temperature: float,
    humidity: float,
) -> float:

    temperature_stress = 0.0
    humidity_stress = 0.0

    # Temperature stress
    if temperature <= 6:
        temperature_stress = 1.0
    elif temperature <= 8:
        temperature_stress = 1.25
    elif temperature <= 10:
        temperature_stress = 1.6
    else:
        temperature_stress = 2.0

    # Humidity stress
    if humidity <= 75:
        humidity_stress = 1.0
    elif humidity <= 85:
        humidity_stress = 1.15
    elif humidity <= 90:
        humidity_stress = 1.4
    else:
        humidity_stress = 1.7

    combined_stress = (
        temperature_stress *
        humidity_stress
    )

    return round(combined_stress, 3)


def estimate_remaining_shelf_life(
    current_shelf_life: float,
    temperature: float,
    humidity: float,
    elapsed_hours: float,
) -> float:

    stress = calculate_environmental_stress(
        temperature=temperature,
        humidity=humidity,
    )

    normal_decay = (
        elapsed_hours / 24
    )

    adjusted_decay = (
        normal_decay *
        stress
    )

    estimated_life = (
        current_shelf_life -
        adjusted_decay
    )

    return round(
        max(estimated_life, 0.0),
        2
    )


def determine_risk_level(
    remaining_shelf_life: float,
    stress_score: float,
) -> str:

    if (
        remaining_shelf_life <= 1.5
        or stress_score >= 2.0
    ):
        return "Critical"

    if (
        remaining_shelf_life <= 3
        or stress_score >= 1.6
    ):
        return "Warning"

    return "Healthy"


def generate_shelf_life_assessment(
    current_shelf_life: float,
    temperature: float,
    humidity: float,
    elapsed_hours: float,
) -> dict:

    stress_score = calculate_environmental_stress(
        temperature=temperature,
        humidity=humidity,
    )

    estimated_remaining_life = (
        estimate_remaining_shelf_life(
            current_shelf_life=current_shelf_life,
            temperature=temperature,
            humidity=humidity,
            elapsed_hours=elapsed_hours,
        )
    )

    risk_level = determine_risk_level(
        remaining_shelf_life=estimated_remaining_life,
        stress_score=stress_score,
    )

    if risk_level == "Critical":

        recommendation = (
            "Prioritize this batch immediately "
            "for processing or distribution."
        )

    elif risk_level == "Warning":

        recommendation = (
            "Increase monitoring frequency "
            "and prioritize this batch."
        )

    else:

        recommendation = (
            "Continue normal monitoring."
        )

    return {
        "estimated_remaining_shelf_life":
            estimated_remaining_life,

        "environmental_stress_score":
            stress_score,

        "risk_level":
            risk_level,

        "recommendation":
            recommendation,
    }