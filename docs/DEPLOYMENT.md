# Deployment Guide — EduSphere SMS

## Overview

Production deployment uses Kubernetes (EKS/AKS/GKE) with Helm for application deployment
and Terraform for infrastructure provisioning.

## Prerequisites

- AWS CLI configured with sufficient IAM permissions
- Terraform >= 1.7, kubectl, helm installed
- Docker registry access (ECR or Docker Hub)

## Step 1 — Provision Infrastructure (Terraform)

```bash
cd infrastructure/terraform

# Initialise
terraform init

# Plan (review changes)
terraform plan -var="db_password=YourSecurePassword123!" -out=tfplan

# Apply
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json
```

## Step 2 — Configure kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name edusphere-sms
kubectl get nodes   # Verify cluster connectivity
```

## Step 3 — Build & Push Docker Images

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account_id>.dkr.ecr.us-east-1.amazonaws.com

# Backend
docker build -f infrastructure/docker/backend/Dockerfile \
  --target production \
  -t <ecr_backend_url>:2.0.0 backend/
docker push <ecr_backend_url>:2.0.0

# Frontend
docker build -f infrastructure/docker/frontend/Dockerfile \
  --target production \
  --build-arg REACT_APP_API_URL=https://api.edusphere.school/api/v1 \
  --build-arg REACT_APP_WS_URL=wss://api.edusphere.school \
  -t <ecr_frontend_url>:2.0.0 frontend/web/
docker push <ecr_frontend_url>:2.0.0
```

## Step 4 — Apply Kubernetes Manifests

```bash
# Create namespace
kubectl apply -f infrastructure/k8s/deployments/backend.yaml

# Create secrets (fill in real values first!)
kubectl create secret generic sms-secrets \
  --from-literal=secret-key="<your-django-secret-key>" \
  --from-literal=database-url="postgresql://sms:pass@rds-endpoint:5432/sms_db" \
  --from-literal=redis-url="redis://elasticache-endpoint:6379/0" \
  --from-literal=aws-access-key-id="<your-aws-access-key-id>" \
  --from-literal=aws-secret-access-key="<your-aws-secret-access-key>" \
  -n sms

# Deploy all services
kubectl apply -f infrastructure/k8s/deployments/

# Verify pods are running
kubectl get pods -n sms -w
```

## Step 5 — Database Migrations

> **Before the first deployment**, generate real migration files locally (`python manage.py makemigrations`) and commit them to the repo — only `auth_service` ships with a hand-written initial migration in this scaffold. Production should always apply pre-generated, reviewed migrations, never run `makemigrations` against a live database.

```bash
# Run as a one-off Job
kubectl run sms-migrate \
  --image=<ecr_backend_url>:2.0.0 \
  --restart=Never \
  --env="DATABASE_URL=..." \
  --env="SECRET_KEY=..." \
  -n sms \
  -- python manage.py migrate --settings=core.settings.production

# Verify
kubectl logs sms-migrate -n sms
kubectl delete pod sms-migrate -n sms
```

## Step 6 — Install Monitoring

```bash
# Prometheus + Grafana
kubectl apply -f infrastructure/monitoring/prometheus.yaml

# Access Grafana (port-forward)
kubectl port-forward svc/grafana 3000:3000 -n sms
open http://localhost:3000   # admin / (check sms-secrets)
```

## Step 7 — Verify Deployment

```bash
# Check all pods
kubectl get pods -n sms

# Check ingress
kubectl get ingress -n sms

# Test API health
curl https://api.edusphere.school/health/ready/

# Test frontend
open https://app.edusphere.school
```

## Rolling Updates

```bash
# Update backend image tag and roll out
kubectl set image deployment/sms-backend \
  backend=<ecr_backend_url>:2.1.0 -n sms

# Monitor rollout
kubectl rollout status deployment/sms-backend -n sms

# Rollback if needed
kubectl rollout undo deployment/sms-backend -n sms
```

## Scaling

```bash
# Manual scale
kubectl scale deployment sms-backend --replicas=5 -n sms

# View HPA status
kubectl get hpa -n sms

# Force HPA recalculation
kubectl patch hpa sms-backend-hpa -n sms \
  -p '{"spec":{"minReplicas":3}}'
```

## Backup & Recovery

> 💡 **Full documentation for backup verification, automated strategy, PITR, and
> disaster recovery runbooks is available at `infrastructure/db/README.md`.**

### Database Backup

```bash
# Manual backup (RDS has automated daily backups)
aws rds create-db-snapshot \
  --db-instance-identifier edusphere-sms-postgres \
  --db-snapshot-identifier manual-backup-$(date +%Y%m%d)

# Also generate a portable pg_dump backup for off-site storage:
pg_dump -h localhost -U sms -d sms_db --no-owner --compress=9 \
  -f /backups/sms-manual-$(date +%Y%m%d).sql.gz
```

### Verify Backup Integrity

Always verify a backup after creating it (see `infrastructure/db/README.md`):

```bash
./infrastructure/db/verify_backup.sh /backups/sms-manual-20241115.sql.gz
```

### Restore from Snapshot

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier edusphere-sms-postgres-restored \
  --db-snapshot-identifier manual-backup-20241115

# Then verify the restored instance has the expected data:
PGHOST=restored-instance.aws.com \
  ./infrastructure/db/verify_backup.sh /backups/sms-manual-20241115.sql.gz
```

## Troubleshooting

| Symptom                    | Check                                                         |
| -------------------------- | ------------------------------------------------------------- |
| Pods in CrashLoopBackOff   | `kubectl logs <pod> -n sms --previous`                        |
| 502 Bad Gateway            | Backend pods not ready — check readiness probes               |
| Database connection errors | Verify `database-url` secret; check RDS security groups       |
| Celery tasks not running   | Check `sms-celery-worker` pod logs; verify Redis connectivity |
| WebSocket disconnects      | Check Nginx ingress WebSocket upgrade annotations             |
| File uploads failing       | Verify S3 bucket permissions and `aws-*` secrets              |
