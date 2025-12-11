# Cloud Resource Monitoring and Alerting System

A scalable, cloud-agnostic platform for monitoring, alerting, and auditing cloud resources. Provides centralized metric visualization, automated alerting, incident logging, and seamless onboarding of new resources.

---

## Features

- **Cloud-native monitoring integration** (AWS CloudWatch, Prometheus, etc.)
- **Centralized dashboard** with Grafana
- **Automated alerting** (email, Slack, Teams)
- **Incident and audit logging** (tamper-proof, security-compliant)
- **Automated onboarding** of new resources
- **RESTful API** for CRUD operations on products and resources
- **Security event detection** and alerting
- **DevOps notifications** for misconfigurations or lack of coverage

---

## Architecture Overview

- **FastAPI**: REST API server
- **PostgreSQL**: Persistent storage for products, alerts, resources, and audit logs
- **Grafana**: Visualization dashboards
- **Prometheus**: Metrics collection (optional/hybrid)
- **Celery**: Background tasks (alerting/onboarding, optional)
- **Docker Compose**: Local orchestration
- **Cloud-native integrations**: AWS CloudWatch, Azure Monitor, etc.

---

## Quick Start (Local Development)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- (Optional) Python 3.11+ for local development

### 1. Clone the Repository

```sh
git clone <repo-url>
cd <repo-directory>
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and edit as needed:

```sh
cp .env.example .env
```

Key variables:
- `DATABASE_URL`
- `ALERT_EMAIL_FROM`, `ALERT_EMAIL_RECIPIENTS`, `SMTP_*`
- `SLACK_WEBHOOK_URL`, `TEAMS_WEBHOOK_URL`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `PROMETHEUS_URL`

### 3. Build and Start All Services

```sh
docker-compose up --build
```

- API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Grafana: [http://localhost:3000](http://localhost:3000) (default user: `admin`, password: `admin`)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- PostgreSQL: `localhost:5432` (user: `cloudmon`, password: `cloudmonpass`)

### 4. Run Tests

```sh
docker-compose exec api pytest
```

Or locally (requires Python 3.11+, dependencies in `requirements.txt`):

```sh
pip install -r requirements.txt
pytest
```

---

## API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

- `/products/` - CRUD for products
- `/metrics/resources/` - Get metrics for all resources
- `/alerts/` - List and resolve alerts
- `/onboarding/resources/` - Trigger resource onboarding
- `/audit/logs/` - Retrieve audit logs
- `/health` - Health check

---

## Configuration

All configuration is managed via environment variables (see `.env.example`).

- **Database**: `DATABASE_URL`
- **Monitoring**: `AWS_*`, `PROMETHEUS_URL`
- **Alerting**: `ALERT_EMAIL_*`, `SLACK_WEBHOOK_URL`, `TEAMS_WEBHOOK_URL`
- **Security**: `SECRET_KEY`
- **CORS**: `ALLOWED_ORIGINS`

---

## Operational Procedures

### Onboarding New Resources

- Resources are discovered and onboarded automatically via background tasks.
- Manual trigger: `POST /onboarding/resources/`

### Alerting

- Alerts are generated on threshold breaches or security events.
- Delivered via email and/or messaging platforms.
- All alert events are logged for audit.

### Audit Trail

- All alert generation and resolution events are logged in an immutable audit log.
- Retrieve via `GET /audit/logs/`.

### Dashboard

- Grafana is pre-configured with dashboards for resource metrics.
- Import or customize dashboards via the Grafana UI.

---

## Security & Compliance

- All secrets and credentials are managed via environment variables.
- Audit logs are tamper-proof and compliant with security standards.
- Monitoring configuration is extensible and reviewed for completeness.

---

## Extending & Customizing

- Add new cloud providers by extending `src/monitoring.py` and `src/onboarding.py`.
- Add new alert delivery channels in `src/alerting.py`.
- Customize Grafana dashboards in `dashboards/grafana-dashboard.json`.

---

## Troubleshooting

- **API not starting?** Check logs with `docker-compose logs api`.
- **Database connection issues?** Ensure `db` service is healthy and credentials match.
- **Email/Slack/Teams alerts not delivered?** Check environment variables and logs.
- **Metrics not appearing?** Ensure Prometheus and cloud provider credentials are correct.

---

## License

MIT License

---

## Maintainers

- [Your Name] - [your.email@example.com]
- [Contributors...]

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Grafana](https://grafana.com/)
- [Prometheus](https://prometheus.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)