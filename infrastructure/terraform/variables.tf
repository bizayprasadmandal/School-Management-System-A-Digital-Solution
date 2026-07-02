# ─── variables.tf ─────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Must be staging or production."
  }
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "edusphere-sms"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "ElastiCache Redis password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "domain_name" {
  description = "Primary domain for the application"
  type        = string
  default     = "edusphere.school"
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
}

variable "node_instance_types" {
  description = "EC2 instance types for general node group"
  type        = list(string)
  default     = ["t3.medium", "t3.large"]
}

variable "worker_instance_types" {
  description = "EC2 instance types for Celery worker node group"
  type        = list(string)
  default     = ["m5.large"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_storage_gb" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on RDS and critical resources"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
