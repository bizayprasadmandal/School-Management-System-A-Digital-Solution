# ─── outputs.tf — Terraform output values ────────────────────────────────────

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API server endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_certificate" {
  description = "EKS cluster CA certificate"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "rds_endpoint" {
  description = "RDS PostgreSQL connection endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.rds.db_instance_name
}

output "redis_primary_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = true
}

output "s3_documents_bucket" {
  description = "S3 bucket name for documents and media"
  value       = aws_s3_bucket.documents.bucket
}

output "ecr_backend_repository_url" {
  description = "ECR repository URL for the backend image"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_repository_url" {
  description = "ECR repository URL for the frontend image"
  value       = aws_ecr_repository.frontend.repository_url
}

output "acm_certificate_arn" {
  description = "ACM certificate ARN for the domain"
  value       = aws_acm_certificate.main.arn
}

output "configure_kubectl_command" {
  description = "Command to configure kubectl for this cluster"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
}

output "database_url" {
  description = "Full PostgreSQL DATABASE_URL for Django settings"
  value       = "postgresql://${var.db_username}:${var.db_password}@${module.rds.db_instance_endpoint}/${var.db_name}"
  sensitive   = true
}

output "redis_url" {
  description = "Full Redis URL for Django settings"
  value       = "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:6379/0"
  sensitive   = true
}

output "backend_sa_role_arn" {
  description = "IRSA role ARN for the sms-backend-sa service account (substitute into the k8s annotation)"
  value       = aws_iam_role.sms_backend_sa.arn
}

output "grafana_admin_password" {
  description = "Grafana admin password (set the same value into the sms-secrets secret)"
  value       = var.grafana_admin_password
  sensitive   = true
}
