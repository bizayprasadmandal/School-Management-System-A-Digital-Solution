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

variable "db_username" {
  description = "RDS master username (used in the DATABASE_URL output)"
  type        = string
  default     = "sms"
}

variable "db_name" {
  description = "RDS database name (used in the DATABASE_URL output)"
  type        = string
  default     = "sms_db"
}

variable "allowed_cidr_blocks" {
  description = "Extra CIDR blocks allowed to reach RDS/Redis (in addition to the VPC CIDR)"
  type        = list(string)
  default     = []
}

variable "eks_public_access_cidrs" {
  description = "CIDR blocks allowed to reach the public EKS API endpoint (operator/VPN ranges)"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "monthly_budget_usd" {
  description = "Monthly AWS cost budget in USD (0 disables the budget alert)"
  type        = number
  default     = 0
}

variable "alert_email" {
  description = "Email address for budget and cost alerts"
  type        = string
  default     = ""
}

variable "redis_password" {
  description = "ElastiCache Redis auth token (optional; empty disables Redis AUTH)"
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
  description = "Grafana admin password (required — no default)"
  type        = string
  sensitive   = true
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
