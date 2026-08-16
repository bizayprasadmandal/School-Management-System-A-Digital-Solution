# ─── security_groups.tf — VPC security group definitions ─────────────────────

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "${var.cluster_name}-rds-sg"
  description = "Allow PostgreSQL from EKS nodes (VPC CIDR)"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    cidr_blocks     = concat([module.vpc.vpc_cidr_block], var.allowed_cidr_blocks)
    description     = "PostgreSQL from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = { Name = "${var.cluster_name}-rds-sg" }
}

# Redis Security Group
resource "aws_security_group" "redis" {
  name        = "${var.cluster_name}-redis-sg"
  description = "Allow Redis from EKS nodes"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = concat([module.vpc.vpc_cidr_block], var.allowed_cidr_blocks)
    description = "Redis from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = { Name = "${var.cluster_name}-redis-sg" }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.cluster_name}-db-subnet"
  subnet_ids = module.vpc.private_subnets
  tags       = { Name = "${var.cluster_name}-db-subnet" }
}

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.cluster_name}-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

# CloudWatch Budget Alert
resource "aws_budgets_budget" "monthly" {
  count         = var.monthly_budget_usd > 0 ? 1 : 0
  name          = "${var.cluster_name}-monthly-budget"
  budget_type   = "COST"
  limit_amount  = tostring(var.monthly_budget_usd)
  limit_unit    = "USD"
  time_unit     = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}

# IAM Role for Service Accounts (IRSA) — Backend pods can access S3 and ECR
resource "aws_iam_role" "sms_backend_sa" {
  name = "${var.cluster_name}-backend-sa-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = module.eks.oidc_provider_arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:sub" = "system:serviceaccount:sms:sms-backend-sa"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "sms_backend_s3" {
  name = "${var.cluster_name}-backend-s3-policy"
  role = aws_iam_role.sms_backend_sa.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["ses:SendEmail", "ses:SendRawEmail"]
        Resource = "*"
      }
    ]
  })
}
