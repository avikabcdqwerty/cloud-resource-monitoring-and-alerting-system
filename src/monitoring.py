import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .models import Resource, get_session
from .schemas import ResourceMetrics, MetricData

from .config import settings

# For demonstration, we use boto3 for AWS CloudWatch and prometheus_api_client for Prometheus.
# In production, these should be securely configured and credentials managed via environment variables/secrets.
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None

try:
    from prometheus_api_client import PrometheusConnect
except ImportError:
    PrometheusConnect = None

logger = logging.getLogger("monitoring")

# --- Cloud-Native Monitoring Integration ---

def fetch_aws_cloudwatch_metrics(resource: Resource) -> List[MetricData]:
    """
    Fetch metrics from AWS CloudWatch for a given resource.
    """
    if not boto3:
        logger.error("boto3 is not installed. AWS CloudWatch integration unavailable.")
        return []
    try:
        cloudwatch = boto3.client(
            "cloudwatch",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        # Example: Fetch CPUUtilization for EC2 instance
        metrics = []
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=60)
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": resource.resource_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=["Average"],
        )
        for datapoint in response.get("Datapoints", []):
            metrics.append(
                MetricData(
                    timestamp=datapoint["Timestamp"],
                    cpu=datapoint.get("Average"),
                    memory=None,
                    network=None,
                    storage=None,
                )
            )
        logger.info(f"Fetched {len(metrics)} CloudWatch metrics for resource {resource.resource_id}")
        return metrics
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Error fetching CloudWatch metrics: {e}")
        return []

def fetch_prometheus_metrics(resource: Resource) -> List[MetricData]:
    """
    Fetch metrics from Prometheus for a given resource.
    """
    if not PrometheusConnect:
        logger.error("prometheus_api_client is not installed. Prometheus integration unavailable.")
        return []
    try:
        prom = PrometheusConnect(url=settings.PROMETHEUS_URL, disable_ssl=True)
        metrics = []
        # Example: Query CPU usage for a VM
        query = f'instance:node_cpu_utilisation:avg1m{{instance="{resource.resource_id}"}}'
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=60)
        step = 300  # 5 minutes
        result = prom.custom_query_range(
            query=query,
            start_time=start_time,
            end_time=end_time,
            step=step,
        )
        for series in result:
            for value in series.get("values", []):
                metrics.append(
                    MetricData(
                        timestamp=datetime.utcfromtimestamp(float(value[0])),
                        cpu=float(value[1]),
                        memory=None,
                        network=None,
                        storage=None,
                    )
                )
        logger.info(f"Fetched {len(metrics)} Prometheus metrics for resource {resource.resource_id}")
        return metrics
    except Exception as e:
        logger.error(f"Error fetching Prometheus metrics: {e}")
        return []

def fetch_metrics_for_resource(resource: Resource) -> List[MetricData]:
    """
    Fetch metrics for a resource from the appropriate monitoring backend.
    """
    # Determine backend based on resource.cloud_provider or configuration
    if resource.cloud_provider.lower() == "aws":
        return fetch_aws_cloudwatch_metrics(resource)
    elif resource.cloud_provider.lower() == "prometheus":
        return fetch_prometheus_metrics(resource)
    # Add more cloud providers as needed (Azure, GCP, etc.)
    logger.warning(f"No monitoring integration for provider: {resource.cloud_provider}")
    return []

def get_resource_metrics(resource_id: str) -> ResourceMetrics:
    """
    Get metrics for a specific resource.
    """
    db = get_session()
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        logger.warning(f"Resource not found for metrics: {resource_id}")
        return ResourceMetrics(resource_id=resource_id, metrics=[])
    metrics = fetch_metrics_for_resource(resource)
    return ResourceMetrics(resource_id=resource_id, metrics=metrics)

def get_all_resources_metrics() -> List[ResourceMetrics]:
    """
    Get metrics for all monitored resources.
    """
    db = get_session()
    resources = db.query(Resource).filter(Resource.monitoring_enabled == True).all()
    results = []
    for resource in resources:
        metrics = fetch_metrics_for_resource(resource)
        results.append(ResourceMetrics(resource_id=resource.resource_id, metrics=metrics))
    logger.info(f"Fetched metrics for {len(results)} resources.")
    return results

# --- Exports ---
__all__ = [
    "get_resource_metrics",
    "get_all_resources_metrics",
]