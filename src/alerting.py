import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Alert, AlertStatus, AlertSeverity, Resource, AuditLog, get_session
from .schemas import AlertOut, AuditLogCreate
from .crud import (
    get_alert,
    update_alert,
    get_alerts as crud_get_alerts,
    create_audit_log,
)
from .config import settings

# Email and messaging platform integration
import smtplib
from email.mime.text import MIMEText
import requests

logger = logging.getLogger("alerting")

# --- Alert Delivery ---

def send_email_alert(subject: str, body: str, recipients: List[str]) -> bool:
    """
    Send an alert email to designated recipients.
    """
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.ALERT_EMAIL_FROM
        msg["To"] = ", ".join(recipients)

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.ALERT_EMAIL_FROM, recipients, msg.as_string())
        logger.info(f"Alert email sent to {recipients}")
        return True
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
        return False

def send_slack_alert(message: str, webhook_url: str) -> bool:
    """
    Send an alert message to Slack via webhook.
    """
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info("Alert sent to Slack.")
            return True
        else:
            logger.error(f"Slack alert failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False

def send_teams_alert(message: str, webhook_url: str) -> bool:
    """
    Send an alert message to Microsoft Teams via webhook.
    """
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info("Alert sent to Teams.")
            return True
        else:
            logger.error(f"Teams alert failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to send Teams alert: {e}")
        return False

def deliver_alert(alert: Alert, resource: Resource) -> List[str]:
    """
    Deliver alert via configured channels (email, Slack, Teams).
    Returns list of successful delivery channels.
    """
    subject = f"[{alert.severity.upper()}] Alert for Resource {resource.name} ({resource.resource_id})"
    body = f"""
    Alert Message: {alert.message}
    Severity: {alert.severity}
    Status: {alert.status}
    Resource: {resource.name} ({resource.resource_id})
    Triggered At: {alert.triggered_at}
    """
    delivered_channels = []

    # Email delivery
    if settings.ALERT_EMAIL_RECIPIENTS:
        if send_email_alert(subject, body, settings.ALERT_EMAIL_RECIPIENTS):
            delivered_channels.append("email")

    # Slack delivery
    if settings.SLACK_WEBHOOK_URL:
        if send_slack_alert(body, settings.SLACK_WEBHOOK_URL):
            delivered_channels.append("slack")

    # Teams delivery
    if settings.TEAMS_WEBHOOK_URL:
        if send_teams_alert(body, settings.TEAMS_WEBHOOK_URL):
            delivered_channels.append("teams")

    return delivered_channels

# --- Alert Generation ---

def generate_alert(
    db: Session,
    resource_id: int,
    severity: AlertSeverity,
    message: str,
    incident_details: Optional[dict] = None,
) -> Alert:
    """
    Generate an alert for a resource and deliver it.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        logger.error(f"Resource not found for alert generation: id={resource_id}")
        raise ValueError("Resource not found.")

    alert = Alert(
        resource_id=resource.id,
        status=AlertStatus.OPEN,
        severity=severity,
        message=message,
        triggered_at=datetime.utcnow(),
        incident_details=incident_details,
    )
    try:
        db.add(alert)
        db.commit()
        db.refresh(alert)
        delivered_channels = deliver_alert(alert, resource)
        alert.delivered_via = ",".join(delivered_channels)
        db.commit()
        logger.info(f"Alert generated and delivered via: {alert.delivered_via}")

        # Log audit event
        audit_log = AuditLog(
            alert_id=alert.id,
            event_type="generated",
            event_details=incident_details,
            created_at=datetime.utcnow(),
            actor="system",
        )
        db.add(audit_log)
        db.commit()
        return alert
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error generating alert: {e}")
        raise

# --- Alert Query/Resolution ---

def get_alerts(db: Session, status: Optional[str] = None, severity: Optional[str] = None) -> List[AlertOut]:
    """
    Retrieve alerts, optionally filtered by status and severity.
    """
    alerts = crud_get_alerts(db, status=status, severity=severity)
    return [AlertOut.from_orm(a) for a in alerts]

def get_alert_by_id(db: Session, alert_id: int) -> AlertOut:
    """
    Retrieve a specific alert by ID.
    """
    alert = get_alert(db, alert_id)
    return AlertOut.from_orm(alert)

def resolve_alert(db: Session, alert_id: int) -> AlertOut:
    """
    Resolve an alert and log the resolution.
    """
    alert = get_alert(db, alert_id)
    if alert.status == AlertStatus.RESOLVED:
        logger.info(f"Alert already resolved: id={alert_id}")
        return AlertOut.from_orm(alert)
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    try:
        db.commit()
        db.refresh(alert)
        logger.info(f"Alert resolved: id={alert_id}")

        # Log audit event
        audit_log = AuditLog(
            alert_id=alert.id,
            event_type="resolved",
            event_details={"message": alert.message},
            created_at=datetime.utcnow(),
            actor="system",
        )
        db.add(audit_log)
        db.commit()
        return AlertOut.from_orm(alert)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error resolving alert: {e}")
        raise

# --- Security Event Alerting ---

def generate_security_alert(
    db: Session,
    resource_id: int,
    message: str,
    incident_details: Optional[dict] = None,
) -> Alert:
    """
    Generate a security-relevant alert.
    """
    return generate_alert(
        db=db,
        resource_id=resource_id,
        severity=AlertSeverity.SECURITY,
        message=message,
        incident_details=incident_details,
    )

# --- Exports ---
__all__ = [
    "generate_alert",
    "generate_security_alert",
    "get_alerts",
    "get_alert_by_id",
    "resolve_alert",
]