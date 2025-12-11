import logging
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models import Resource, ResourceType, get_session
from .crud import create_resource, get_resource_by_resource_id
from .config import settings

logger = logging.getLogger("onboarding")

# --- Cloud Resource Discovery (Stub/Example) ---

def discover_aws_resources() -> List[Dict[str, Any]]:
    """
    Discover new AWS resources (VMs, storage, databases, etc.).
    Returns a list of resource dicts.
    """
    # In production, use boto3 to list resources from AWS APIs.
    # Here, we provide a stub for demonstration.
    # Example resource:
    return [
        {
            "resource_id": "i-0abcd1234efgh5678",
            "name": "web-server-1",
            "type": ResourceType.VM,
            "cloud_provider": "aws",
        },
        {
            "resource_id": "vol-0abcd1234efgh5678",
            "name": "data-volume-1",
            "type": ResourceType.STORAGE,
            "cloud_provider": "aws",
        },
    ]

def discover_prometheus_resources() -> List[Dict[str, Any]]:
    """
    Discover resources registered in Prometheus.
    Returns a list of resource dicts.
    """
    # In production, query Prometheus targets or service discovery endpoints.
    # Here, we provide a stub for demonstration.
    return [
        {
            "resource_id": "node1.example.com",
            "name": "node1",
            "type": ResourceType.VM,
            "cloud_provider": "prometheus",
        }
    ]

def discover_all_resources() -> List[Dict[str, Any]]:
    """
    Aggregate discovery from all supported cloud providers.
    """
    resources = []
    if settings.ENABLE_AWS_DISCOVERY:
        resources.extend(discover_aws_resources())
    if settings.ENABLE_PROMETHEUS_DISCOVERY:
        resources.extend(discover_prometheus_resources())
    # Add more providers as needed
    return resources

# --- Onboarding Logic ---

def onboard_resource(db: Session, resource_data: Dict[str, Any]) -> bool:
    """
    Onboard a single resource into monitoring and alerting.
    Returns True if onboarded, False if already exists.
    """
    existing = get_resource_by_resource_id(db, resource_data["resource_id"])
    if existing:
        logger.info(f"Resource already onboarded: {resource_data['resource_id']}")
        return False
    try:
        create_resource(db, resource_data)
        logger.info(f"Resource onboarded: {resource_data['resource_id']}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error onboarding resource {resource_data['resource_id']}: {e}")
        return False

def trigger_resource_onboarding():
    """
    Discover and onboard new cloud resources.
    This function is intended to be run as a background task.
    """
    db = get_session()
    discovered = discover_all_resources()
    onboarded_count = 0
    for resource_data in discovered:
        if onboard_resource(db, resource_data):
            onboarded_count += 1
    logger.info(f"Onboarding complete. {onboarded_count} new resources onboarded.")
    db.close()

# --- Exports ---
__all__ = [
    "trigger_resource_onboarding",
]