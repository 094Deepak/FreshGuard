# FreshGuard

## Intelligent Food Shelf-Life Monitoring System

FreshGuard is an intelligent food shelf-life monitoring system designed to monitor environmental conditions affecting perishable food batches.

The system uses simulated sensor data such as temperature and humidity to assess environmental conditions, estimate remaining shelf life, classify batch risk, generate alerts, and support human intervention through a Human-in-the-Loop review mechanism.

---

# 1. Problem Statement

Perishable food products can deteriorate when environmental conditions such as temperature and humidity move outside acceptable ranges.

Traditional monitoring systems may provide sensor measurements but do not always provide an integrated mechanism for:

- estimating remaining shelf life,
- identifying environmental risk,
- generating actionable alerts,
- prioritizing critical batches,
- and incorporating human decisions into the monitoring process.

FreshGuard addresses this problem by combining environmental monitoring, shelf-life assessment, risk classification, alert generation, and human review in a single application.

---

# 2. Objectives

The main objectives of FreshGuard are:

1. Monitor environmental conditions of food batches.
2. Store historical temperature and humidity readings.
3. Assess environmental stress.
4. Estimate remaining shelf life.
5. Classify batches as Healthy, Warning, or Critical.
6. Generate alerts when attention is required.
7. Provide human review and escalation of alerts.
8. Present monitoring information through an interactive web dashboard.
9. Provide historical analytics for environmental and alert data.

---

# 3. Key Features

## Batch Management

FreshGuard allows users to manage food production batches.

Each batch can contain information such as:

- Batch code
- Product name
- Temperature
- Humidity
- Remaining shelf life
- Current status

---

## Sensor Simulation

The project includes a sensor simulator that continuously generates environmental readings.

Example:

    Batch TOM-001 | Tomato | Temperature: 7.9°C | Humidity: 75.4% | Risk: Healthy
    Batch TOM-002 | TOM-002 | Temperature: 7.5°C | Humidity: 76.4% | Risk: Healthy
    Batch STR-001 | Strawberry | Temperature: 4.2°C | Humidity: 68.2% | Risk: Critical
    Batch APP-001 | Apple | Temperature: 7.2°C | Humidity: 72.5% | Risk: Warning

The simulator stores readings in the database and continuously updates the monitoring state.

---

# 4. Shelf-Life and Risk Assessment

FreshGuard evaluates environmental conditions and produces an assessment for each monitored batch.

The assessment includes:

- Remaining shelf life
- Environmental stress score
- Risk level
- Recommended action

The system classifies conditions into three primary risk levels:

### Healthy

The batch is currently within the monitored healthy range.

### Warning

The batch requires closer monitoring.

### Critical

The batch requires immediate attention.

---

# 5. Human-in-the-Loop Alert Management

A key component of FreshGuard is its Human-in-the-Loop mechanism.

Instead of allowing an automated risk assessment to be the final decision, FreshGuard allows a human reviewer to evaluate generated alerts.

The workflow is:

    Sensor Data
          |
          v
    Environmental Assessment
          |
          v
    Risk Classification
          |
          v
        Alert
          |
          v
     Human Review
          |
       +--+--+
       |     |
       v     v
    Accepted Escalated
       |
       v
    Resolved

Human review information can include:

- Review status
- Human decision
- Review comment
- Resolved status

This allows automated monitoring to be combined with human judgment.

---

# 6. System Architecture

The major system flow is:

    Sensor Simulator
            |
            v
    Sensor Reading API
            |
            v
       SQLite Database
            |
            v
    Environmental Assessment
            |
            +----------------+
            |                |
            v                v
      Shelf-Life         Risk Level
      Assessment       Healthy/Warning/Critical
            |                |
            +--------+-------+
                     |
                     v
                   Alerts
                     |
                     v
              Human Review
                     |
                     v
          Dashboard / Analytics

---

# 7. Technology Stack

## Backend

- Python
- FastAPI
- Uvicorn

## Database

- SQLite
- SQLAlchemy
- aiosqlite

## Validation

- Pydantic

## Frontend

- HTML
- CSS
- JavaScript
- Jinja2 templates

## Runtime Environment

- Python 3.12
- Virtual environment (`.venv`)

---

# 8. Project Structure

    FreshGuard/
    |
    ├── app/
    │   ├── __init__.py
    │   └── main.py
    |
    ├── api/
    │   ├── __init__.py
    │   ├── alerts.py
    │   ├── batches.py
    │   └── monitoring.py
    |
    ├── database/
    │   ├── __init__.py
    │   ├── database.py
    │   ├── models.py
    │   ├── schemas.py
    │   └── sensor_models.py
    |
    ├── services/
    │   ├── __init__.py
    │   └── shelf_life.py
    |
    ├── templates/
    │   ├── dashboard.html
    │   ├── batches.html
    │   ├── batch_details.html
    │   ├── monitoring.html
    │   ├── analytics.html
    │   ├── alerts.html
    │   └── settings.html
    |
    ├── simulation.py
    ├── freshguard.db
    ├── requirements.txt
    └── README.md

---

# 9. Application Pages

FreshGuard provides the following main pages.

## Dashboard

Provides an overall view of:

- Active batches
- Healthy batches
- At-risk batches
- Average remaining shelf life
- Active alerts
- Recent batches
- Risk overview

---

## Batches

Provides batch management functionality and access to individual batch details.

---

## Monitoring

Provides real-time environmental monitoring for selected batches.

The page displays:

- Current temperature
- Current humidity
- Remaining shelf life
- Environmental stress score
- Current risk level
- Recommended action
- Environmental history

---

## Analytics

Provides historical system analysis including:

- Total batches
- Sensor readings
- Average temperature
- Minimum temperature
- Maximum temperature
- Average humidity
- Minimum humidity
- Maximum humidity
- Active alerts
- Critical alerts
- Warning alerts
- Resolved alerts

---

## Alerts

Provides an overview of active alerts.

Users can view:

- Alert severity
- Batch
- Product
- Remaining shelf life
- Environmental stress score
- Recommended action
- Review status
- Human decision

The system supports human review and escalation.

---

## Settings

Provides the application's settings interface.

---

# 10. API Components

FreshGuard is implemented using FastAPI routers.

### Batch APIs

Handled by:

    api/batches.py

Responsible for batch-related operations.

### Monitoring APIs

Handled by:

    api/monitoring.py

Responsible for:

- Creating sensor readings
- Retrieving sensor history
- Retrieving latest sensor readings
- Generating shelf-life assessments

### Alert APIs

Handled by:

    api/alerts.py

Responsible for:

- Alert retrieval
- Alert review
- Human decisions
- Alert resolution/escalation

---

# 11. Database

FreshGuard uses SQLite for persistent storage.

The database file is:

    freshguard.db

SQLAlchemy provides database models and asynchronous database access.

The project contains models for:

- Food batches
- Sensor readings
- Alerts

---

# 12. Installation

## Step 1: Clone or copy the project

Place the FreshGuard project on your computer.

---

## Step 2: Open the project directory

    cd FreshGuard

---

## Step 3: Create a virtual environment

If a virtual environment does not already exist:

    python -m venv .venv

---

## Step 4: Activate the virtual environment

On Git Bash / Windows:

    source .venv/Scripts/activate

---

## Step 5: Install dependencies

    pip install -r requirements.txt

---

# 13. Running FreshGuard

Start the FastAPI application:

    uvicorn app.main:app --reload

The application will normally be available at:

    http://127.0.0.1:8000

---

# 14. Running the Sensor Simulator

Open a second terminal.

Navigate to the project:

    cd FreshGuard

Activate the environment:

    source .venv/Scripts/activate

Run:

    python simulation.py

The simulator continuously generates sensor readings.

Example:

    FreshGuard Sensor Simulator Started

    Batch TOM-001 | Tomato | Temperature: 5.3°C | Humidity: 76.6% | Risk: Healthy
    Batch TOM-002 | TOM-002 | Temperature: 8.9°C | Humidity: 77.1% | Risk: Warning
    Batch STR-001 | Strawberry | Temperature: 8.3°C | Humidity: 77.6% | Risk: Critical
    Batch APP-001 | Apple | Temperature: 3.5°C | Humidity: 60.8% | Risk: Warning

The simulator can be stopped using:

    Ctrl + C

---

# 15. Demonstration Flow

A recommended demonstration sequence is:

1. Start the FastAPI server.
2. Open the FreshGuard Dashboard.
3. Show the available batches.
4. Open Monitoring.
5. Select a batch.
6. Show temperature and humidity.
7. Show remaining shelf life.
8. Show environmental stress.
9. Show risk classification.
10. Open Alerts.
11. Demonstrate a human review.
12. Show Accepted or Escalated status.
13. Open Analytics.
14. Show historical sensor and alert statistics.
15. Open Settings.
16. Return to Dashboard.

---

# 16. Example System Results

During testing, FreshGuard successfully demonstrated multiple risk states.

Example monitored batches:

| Batch | Product | Temperature | Humidity | Risk |
|---|---|---:|---:|---|
| TOM-001 | Tomato | 7.9°C | 75.4% | Healthy |
| TOM-002 | TOM-002 | 7.5°C | 76.4% | Healthy |
| STR-001 | Strawberry | 4.2°C | 68.2% | Critical |
| APP-001 | Apple | 7.2°C | 72.5% | Warning |

The system also successfully generated and displayed active alerts.

---

# 17. Human Review Example

FreshGuard was tested with human alert decisions.

Example accepted decision:

    Human decision: Accepted

Example escalated decision:

    Human decision: Escalated

The system records the review state and whether the alert has been resolved.

This demonstrates the Human-in-the-Loop component of the system.

---

# 18. Project Outcome

FreshGuard successfully integrates:

    Environmental Monitoring
            +
    Shelf-Life Assessment
            +
    Risk Classification
            +
    Alert Generation
            +
    Human Review
            +
    Analytics
            =
    Intelligent Food Shelf-Life Monitoring

The project demonstrates how automated environmental monitoring can be combined with human intervention to support safer and more informed decisions for perishable food batches.

---

# 19. Future Enhancements

Potential future improvements include:

- Real IoT sensor integration
- Cloud-based deployment
- Machine-learning-based shelf-life prediction
- More advanced time-series analysis
- Predictive spoilage detection
- Notification services
- Role-based access control
- Authentication
- More advanced analytics and visualizations
- Integration with warehouse management systems

---

# 20. Conclusion

FreshGuard provides an integrated platform for monitoring food batches and identifying environmental conditions that may affect shelf life.

The system combines automated sensor simulation and environmental assessment with a Human-in-the-Loop alert workflow. This allows automated risk detection to be supplemented by human judgment before critical operational decisions are made.

The completed system provides a functional foundation for intelligent food quality and shelf-life monitoring.