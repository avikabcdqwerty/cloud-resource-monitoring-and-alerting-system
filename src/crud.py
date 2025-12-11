import logging
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from .models import Product, Resource, Alert, AuditLog, AlertStatus
from .schemas import (
    ProductCreate,
    ProductUpdate,
    ResourceCreate,
    ResourceUpdate,
    AlertCreate,
    AlertUpdate,
    AuditLogCreate,
)

logger = logging.getLogger("crud")

# --- Product CRUD Operations ---

def create_product(db: Session, product_in: ProductCreate) -> Product:
    """
    Create a new product.
    """
    try:
        product = Product(**product_in.dict())
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info(f"Product created: {product.name} (id={product.id})")
        return product
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this name already exists."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product."
        )

def get_product(db: Session, product_id: int) -> Product:
    """
    Retrieve a product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found: id={product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    return product

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """
    Retrieve a list of products.
    """
    return db.query(Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product_in: ProductUpdate) -> Product:
    """
    Update an existing product.
    """
    product = get_product(db, product_id)
    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.commit()
        db.refresh(product)
        logger.info(f"Product updated: id={product_id}")
        return product
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this name already exists."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product."
        )

def delete_product(db: Session, product_id: int) -> None:
    """
    Delete a product by ID.
    """
    product = get_product(db, product_id)
    try:
        db.delete(product)
        db.commit()
        logger.info(f"Product deleted: id={product_id}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product."
        )

# --- Resource CRUD Operations ---

def create_resource(db: Session, resource_in: ResourceCreate) -> Resource:
    """
    Create a new resource.
    """
    try:
        resource = Resource(**resource_in.dict())
        db.add(resource)
        db.commit()
        db.refresh(resource)
        logger.info(f"Resource created: {resource.resource_id} (id={resource.id})")
        return resource
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource with this ID already exists."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create resource."
        )

def get_resource(db: Session, resource_id: int) -> Resource:
    """
    Retrieve a resource by DB ID.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        logger.warning(f"Resource not found: id={resource_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found."
        )
    return resource

def get_resource_by_resource_id(db: Session, resource_id: str) -> Optional[Resource]:
    """
    Retrieve a resource by its cloud resource_id.
    """
    return db.query(Resource).filter(Resource.resource_id == resource_id).first()

def get_resources(db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
    """
    Retrieve a list of resources.
    """
    return db.query(Resource).offset(skip).limit(limit).all()

def update_resource(db: Session, resource_id: int, resource_in: ResourceUpdate) -> Resource:
    """
    Update an existing resource.
    """
    resource = get_resource(db, resource_id)
    for field, value in resource_in.dict(exclude_unset=True).items():
        setattr(resource, field, value)
    try:
        db.commit()
        db.refresh(resource)
        logger.info(f"Resource updated: id={resource_id}")
        return resource
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource with this ID already exists."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resource."
        )

def delete_resource(db: Session, resource_id: int) -> None:
    """
    Delete a resource by ID.
    """
    resource = get_resource(db, resource_id)
    try:
        db.delete(resource)
        db.commit()
        logger.info(f"Resource deleted: id={resource_id}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource."
        )

# --- Alert CRUD Operations ---

def create_alert(db: Session, alert_in: AlertCreate) -> Alert:
    """
    Create a new alert.
    """
    try:
        alert = Alert(**alert_in.dict())
        db.add(alert)
        db.commit()
        db.refresh(alert)
        logger.info(f"Alert created: id={alert.id} for resource_id={alert.resource_id}")
        return alert
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert."
        )

def get_alert(db: Session, alert_id: int) -> Alert:
    """
    Retrieve an alert by ID.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        logger.warning(f"Alert not found: id={alert_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
    return alert

def get_alerts(db: Session, status: Optional[str] = None, severity: Optional[str] = None) -> List[Alert]:
    """
    Retrieve a list of alerts, optionally filtered by status and severity.
    """
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    return query.order_by(Alert.triggered_at.desc()).all()

def update_alert(db: Session, alert_id: int, alert_in: AlertUpdate) -> Alert:
    """
    Update an alert (e.g., resolve).
    """
    alert = get_alert(db, alert_id)
    for field, value in alert_in.dict(exclude_unset=True).items():
        setattr(alert, field, value)
    try:
        db.commit()
        db.refresh(alert)
        logger.info(f"Alert updated: id={alert_id}")
        return alert
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert."
        )

def delete_alert(db: Session, alert_id: int) -> None:
    """
    Delete an alert by ID.
    """
    alert = get_alert(db, alert_id)
    try:
        db.delete(alert)
        db.commit()
        logger.info(f"Alert deleted: id={alert_id}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert."
        )

# --- Audit Log CRUD Operations ---

def create_audit_log(db: Session, audit_in: AuditLogCreate) -> AuditLog:
    """
    Create a new audit log entry.
    """
    try:
        audit_log = AuditLog(**audit_in.dict())
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        logger.info(f"Audit log created: id={audit_log.id} for alert_id={audit_log.alert_id}")
        return audit_log
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audit log."
        )

def get_audit_log(db: Session, audit_log_id: int) -> AuditLog:
    """
    Retrieve an audit log entry by ID.
    """
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    if not audit_log:
        logger.warning(f"Audit log not found: id={audit_log_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found."
        )
    return audit_log

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
    """
    Retrieve a list of audit logs.
    """
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

# --- Exports ---
__all__ = [
    "create_product",
    "get_product",
    "get_products",
    "update_product",
    "delete_product",
    "create_resource",
    "get_resource",
    "get_resource_by_resource_id",
    "get_resources",
    "update_resource",
    "delete_resource",
    "create_alert",
    "get_alert",
    "get_alerts",
    "update_alert",
    "delete_alert",
    "create_audit_log",
    "get_audit_log",
    "get_audit_logs",
]