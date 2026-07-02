# ─── backend.tf — Remote state configuration ──────────────────────────────────
# Before first use, create the S3 bucket and DynamoDB table manually:
#   aws s3 mb s3://edusphere-terraform-state --region us-east-1
#   aws dynamodb create-table \
#     --table-name edusphere-terraform-locks \
#     --attribute-definitions AttributeName=LockID,AttributeType=S \
#     --key-schema AttributeName=LockID,KeyType=HASH \
#     --billing-mode PAY_PER_REQUEST \
#     --region us-east-1

terraform {
  backend "s3" {
    bucket         = "edusphere-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "edusphere-terraform-locks"
  }
}
