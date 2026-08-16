# ─── EduSphere SMS — AWS EKS Infrastructure (Terraform) ─────────────────────
# Provisions: VPC, EKS cluster, managed node groups, RDS PostgreSQL,
# ElastiCache Redis, S3 bucket, ECR repositories, ACM certificate.
# (ALB/Route53/Helm chart installs are applied via the ingress-nginx
# controller and Kubernetes manifests after `terraform apply`.)

terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.27"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "EduSphere-SMS"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ─── VPC ─────────────────────────────────────────────────────────────────────

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true

  public_subnet_tags = {
    "kubernetes.io/role/elb"                        = 1
    "kubernetes.io/cluster/${var.cluster_name}"     = "owned"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"               = 1
    "kubernetes.io/cluster/${var.cluster_name}"     = "owned"
  }
}

# ─── EKS Cluster ─────────────────────────────────────────────────────────────

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  # Public API access is restricted to the CIDRs in var.eks_public_access_cidrs
  # (operator/VPN ranges); private access is enabled for in-VPC connectivity.
  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = var.eks_public_access_cidrs
  cluster_endpoint_private_access      = true

  # Managed node groups
  eks_managed_node_groups = {
    # General workloads (backend, frontend, celery)
    general = {
      name           = "general"
      instance_types = ["t3.medium"]
      min_size       = 2
      max_size       = 8
      desired_size   = 3
      disk_size      = 50
      labels = { role = "general" }
    }
    # Memory-optimised for Celery workers processing reports
    workers = {
      name           = "workers"
      instance_types = ["m5.large"]
      min_size       = 1
      max_size       = 4
      desired_size   = 2
      disk_size      = 30
      labels = { role = "worker" }
      taints = [{ key = "workload", value = "celery", effect = "NO_SCHEDULE" }]
    }
  }

  # Enable IRSA for service accounts
  enable_irsa = true

  cluster_addons = {
    coredns                = { most_recent = true }
    kube-proxy             = { most_recent = true }
    vpc-cni                = { most_recent = true }
    aws-ebs-csi-driver     = { most_recent = true }
  }
}

# ─── RDS PostgreSQL ───────────────────────────────────────────────────────────

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier        = "${var.cluster_name}-postgres"
  engine            = "postgres"
  engine_version    = "16.2"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  multi_az               = true
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  deletion_protection = true
  skip_final_snapshot = false

  performance_insights_enabled = true
  monitoring_interval          = 60

  parameters = [
    { name = "log_connections",    value = "1" },
    { name = "log_disconnections", value = "1" },
    { name = "log_min_duration_statement", value = "1000" },
  ]
}

# ─── ElastiCache Redis ────────────────────────────────────────────────────────

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.cluster_name}-redis"
  description                = "EduSphere SMS Redis cluster"
  node_type                  = "cache.t3.medium"
  num_cache_clusters         = 2
  port                       = 6379
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  automatic_failover_enabled = true
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  snapshot_retention_limit   = 3
  auth_token                 = var.redis_password != "" ? var.redis_password : null
}

# ─── S3 Bucket (Documents & Media) ───────────────────────────────────────────

resource "aws_s3_bucket" "documents" {
  bucket = "${var.cluster_name}-documents-${var.environment}"
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    id     = "archive-old-reports"
    status = "Enabled"
    filter { prefix = "report_cards/" }
    transition {
      days          = 365
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 1825
      storage_class = "GLACIER"
    }
  }
}

# ─── ECR Repositories ────────────────────────────────────────────────────────

resource "aws_ecr_repository" "backend" {
  name                 = "${var.cluster_name}/backend"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.cluster_name}/frontend"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

# ─── ACM Certificate ─────────────────────────────────────────────────────────

resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"
  lifecycle { create_before_destroy = true }
}
