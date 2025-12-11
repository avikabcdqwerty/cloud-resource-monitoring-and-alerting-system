from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
    create_engine,
    Text,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    scoped_session,
)
import enum

from .config import settings

# --- SQLAlchemy Base ---
Base = declarative_base()

# --- Database Engine and Session ---
def get_engine():
    """
    Returns a SQLAlchemy engine instance.
    """
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

def get_session():
    """
    Returns a SQLAlchemy session instance.
    """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return scoped_session(session_factory)

# --- Enums ---
class AlertStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"

class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SECURITY = "security"

class ResourceType(str, enum.Enum):
    VM = "vm"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    OTHER = "other"

# --- Product Model ---
class Product(Base):
    """
    Product entity for CRUD operations.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # Add more fields as needed

# --- Resource Model ---
class Resource(Base):
    """
    Cloud resource being monitored.
    """
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    type = Column(Enum(ResourceType), nullable=False)
    cloud_provider = Column(String(64), nullable=False)
    onboarded = Column(Boolean, default=False, nullable=False)
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # Relationships
    alerts = relationship("Alert", back_populates="resource", cascade="all, delete-orphan")

# --- Alert Model ---
class Alert(Base):
    """
    Alert generated for resource threshold breach or security event.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.OPEN, nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.INFO, nullable=False, index=True)
    message = Column(Text, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    delivered_via = Column(String(64), nullable=True)  # e.g., 'email', 'slack'
    incident_details = Column(JSON, nullable=True)
    # Relationships
    resource = relationship("Resource", back_populates="alerts")
    audit_logs = relationship("AuditLog", back_populates="alert", cascade="all, delete-orphan")

# --- Audit Log Model ---
class AuditLog(Base):
    """
    Immutable audit log for alert generation and resolution.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    event_type = Column(String(64), nullable=False)  # e.g., 'generated', 'resolved', 'security'
    event_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor = Column(String(128), nullable=True)  # e.g., system, user, service
    # Relationships
    alert = relationship("Alert", back_populates="audit_logs")

# --- Exports ---
__all__ = [
    "Base",
    "get_engine",
    "get_session",
    "Product",
    "Resource",
    "Alert",
    "AuditLog",
    "AlertStatus",
    "AlertSeverity",
    "ResourceType",
]