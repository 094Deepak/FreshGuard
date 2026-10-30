from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse

from api.batches import router as batch_router

from api.monitoring import router as monitoring_router

from api.alerts import router as alerts_router

from database.database import Base, engine

from database.models import Batch

from database.sensor_models import SensorReading


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )

    yield


app = FastAPI(

    title="FreshGuard",

    description="Intelligent Food Shelf-Life Monitoring System",

    version="1.0.0",

    lifespan=lifespan,

)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    batch_router
)

app.include_router(
    monitoring_router
)

app.include_router(
    alerts_router
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def dashboard(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="dashboard.html",

        context={},

    )


# ============================================================
# BATCHES PAGE
# ============================================================

@app.get(
    "/batches",
    response_class=HTMLResponse
)
def batches_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="batches.html",

        context={},

    )


# ============================================================
# BATCH DETAILS PAGE
# ============================================================

@app.get(
    "/batches/{batch_id}",
    response_class=HTMLResponse
)
def batch_details_page(

    request: Request,

    batch_id: int,

):

    return templates.TemplateResponse(

        request=request,

        name="batch_details.html",

        context={

            "batch_id": batch_id,

        },

    )


# ============================================================
# MONITORING PAGE
# ============================================================

@app.get(
    "/monitoring",
    response_class=HTMLResponse
)
def monitoring_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="monitoring.html",

        context={},

    )


# ============================================================
# ALERTS PAGE
# ============================================================

@app.get(
    "/alerts",
    response_class=HTMLResponse
)
def alerts_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="alerts.html",

        context={},

    )


# ============================================================
# ANALYTICS PAGE
# ============================================================

@app.get(
    "/analytics",
    response_class=HTMLResponse
)
def analytics_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="analytics.html",

        context={},

    )


# ============================================================
# SETTINGS PAGE
# ============================================================

@app.get(
    "/settings",
    response_class=HTMLResponse
)
def settings_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="settings.html",

        context={},

    )