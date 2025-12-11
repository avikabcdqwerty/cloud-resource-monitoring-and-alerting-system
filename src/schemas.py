from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, constr

from .models import AlertStatus, AlertSeverity, ResourceType

# --- Product Schemas ---

class ProductBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=128)
    description: Optional[str] = None

class ProductCreate(ProductBase):
    """
    Schema for creating a new product.
    """
    pass

class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.
    """
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=128)] = None
    description: Optional[str] = None

class ProductOut(ProductBase):
    """
    Schema for returning product data.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Resource Schemas ---

class ResourceBase(BaseModel):
    resource_id: constr(strip_whitespace=True, min_length=1, max_length=128)
    name: constr(strip_whitespace=True, min_length=1, max_length=128)
    type: ResourceType
    cloud_provider: constr(strip_whitespace=True, min_length=1, max_length=64)
    onboarded: Optional[bool] = True
    monitoring_enabled: Optional[bool] = True

class ResourceCreate(ResourceBase):
    """
    Schema for creating a new resource.
    """
    pass

class ResourceUpdate(BaseModel):
    """
    Schema for updating an existing resource.
    """
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=128)] = None
    type: Optional[ResourceType] = None
    cloud_provider: Optional[constr(strip_whitespace=True, min_length=1, max_length=64)] = None
    onboarded: Optional[bool] = None
    monitoring_enabled: Optional[bool] = None

class ResourceOut(ResourceBase):
    """
    Schema for returning resource data.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Alert Schemas ---

class AlertBase(BaseModel):
    resource_id: int
    status: AlertStatus = AlertStatus.OPEN
    severity: AlertSeverity = AlertSeverity.INFO
    message: str
    delivered_via: Optional[str] = None
    incident_details: Optional[Any] = None

class AlertCreate(AlertBase):
    """
    Schema for creating a new alert.
    """
    pass

class AlertUpdate(BaseModel):
    """
    Schema for updating an alert (e.g., resolving).
    """
    status: Optional[AlertStatus] = None
    resolved_at: Optional[datetime] = None

class AlertOut(AlertBase):
    """
    Schema for returning alert data.
    """
    id: int
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- Audit Log Schemas ---

class AuditLogBase(BaseModel):
    alert_id: int
    event_type: str
    event_details: Optional[Any] = None
    actor: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    """
    Schema for creating an audit log entry.
    """
    pass

class AuditLogOut(AuditLogBase):
    """
    Schema for returning audit log data.
    """
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Metrics Schemas ---

class MetricData(BaseModel):
    """
    Schema for a single metric data point.
    """
    timestamp: datetime
    cpu: Optional[float] = None
    memory: Optional[float] = None
    network: Optional[float] = None
    storage: Optional[float] = None

class ResourceMetrics(BaseModel):
    """
    Schema for resource metrics response.
    """
    resource_id: str
    metrics: List[MetricData]

# --- Exports ---
__all__ = [
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductOut",
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceOut",
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertOut",
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogOut",
    "MetricData",
    "ResourceMetrics",
]