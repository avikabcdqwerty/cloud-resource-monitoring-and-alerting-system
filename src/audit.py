import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from .models import AuditLog
from .schemas import AuditLogCreate, AuditLogOut

logger = logging.getLogger("audit")

def create_audit_log(db: Session, audit_in: AuditLogCreate) -> AuditLog:
    """
    Create a new immutable audit log entry.
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

def get_audit_log(db: Session, audit_log_id: int) -> AuditLogOut:
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
    return AuditLogOut.from_orm(audit_log)

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> List[AuditLogOut]:
    """
    Retrieve a list of audit logs, ordered by creation time descending.
    """
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [AuditLogOut.from_orm(log) for log in logs]

# --- Exports ---
__all__ = [
    "create_audit_log",
    "get_audit_log",
    "get_audit_logs",
]