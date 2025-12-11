import logging
import sys
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.background import BackgroundTasks

from .config import settings
from .models import Base, get_engine, get_session
from .schemas import ProductCreate, ProductUpdate, ProductOut
from .crud import (
    create_product,
    get_product,
    get_products,
    update_product,
    delete_product,
)
from .monitoring import (
    get_resource_metrics,
    get_all_resources_metrics,
)
from .alerting import (
    get_alerts,
    resolve_alert,
    get_alert_by_id,
)
from .onboarding import (
    trigger_resource_onboarding,
)
from .audit import (
    get_audit_logs,
)
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("cloud-monitoring-api")

# Initialize FastAPI app
app = FastAPI(
    title="Cloud Resource Monitoring and Alerting System",
    description="API for monitoring, alerting, onboarding, and product management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
def on_startup():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created and application startup complete.")

# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred."},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )

# Dependency for DB session
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# --- Product CRUD Endpoints ---

@app.post("/products/", response_model=ProductOut, status_code=status.HTTP_201_CREATED, tags=["Products"])
def api_create_product(product: ProductCreate, db=Depends(get_db)):
    """
    Create a new product.
    """
    return create_product(db, product)

@app.get("/products/", response_model=list[ProductOut], tags=["Products"])
def api_get_products(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """
    Retrieve a list of products.
    """
    return get_products(db, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=ProductOut, tags=["Products"])
def api_get_product(product_id: int, db=Depends(get_db)):
    """
    Retrieve a product by ID.
    """
    return get_product(db, product_id)

@app.put("/products/{product_id}", response_model=ProductOut, tags=["Products"])
def api_update_product(product_id: int, product: ProductUpdate, db=Depends(get_db)):
    """
    Update a product by ID.
    """
    return update_product(db, product_id, product)

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def api_delete_product(product_id: int, db=Depends(get_db)):
    """
    Delete a product by ID.
    """
    delete_product(db, product_id)
    return

# --- Monitoring Endpoints ---

@app.get("/metrics/resources/", tags=["Monitoring"])
def api_get_all_resources_metrics():
    """
    Get metrics for all monitored resources.
    """
    return get_all_resources_metrics()

@app.get("/metrics/resources/{resource_id}", tags=["Monitoring"])
def api_get_resource_metrics(resource_id: str):
    """
    Get metrics for a specific resource.
    """
    return get_resource_metrics(resource_id)

# --- Alerting Endpoints ---

@app.get("/alerts/", tags=["Alerting"])
def api_get_alerts(status: str = None, severity: str = None, db=Depends(get_db)):
    """
    Get all alerts, optionally filtered by status or severity.
    """
    return get_alerts(db, status=status, severity=severity)

@app.get("/alerts/{alert_id}", tags=["Alerting"])
def api_get_alert_by_id(alert_id: int, db=Depends(get_db)):
    """
    Get a specific alert by ID.
    """
    return get_alert_by_id(db, alert_id)

@app.post("/alerts/{alert_id}/resolve", tags=["Alerting"])
def api_resolve_alert(alert_id: int, db=Depends(get_db)):
    """
    Resolve an alert and log the resolution.
    """
    return resolve_alert(db, alert_id)

# --- Resource Onboarding Endpoint ---

@app.post("/onboarding/resources/", status_code=status.HTTP_202_ACCEPTED, tags=["Onboarding"])
def api_trigger_resource_onboarding(background_tasks: BackgroundTasks):
    """
    Trigger onboarding for new cloud resources (runs in background).
    """
    background_tasks.add_task(trigger_resource_onboarding)
    return {"detail": "Resource onboarding triggered."}

# --- Audit Log Endpoint ---

@app.get("/audit/logs/", tags=["Audit"])
def api_get_audit_logs(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """
    Retrieve audit logs for alert generation and resolution.
    """
    return get_audit_logs(db, skip=skip, limit=limit)

# --- Health Check Endpoint ---

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

# --- Main entry point for Uvicorn ---

def run():
    """
    Run the FastAPI app with Uvicorn.
    """
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

# Exported for external use (e.g., for ASGI servers)
__all__ = ["app", "run"]