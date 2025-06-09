terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Configure these values based on your setup
    # bucket         = "your-terraform-state-bucket"
    # key            = "meeting-ai/dev/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "terraform-state-lock"
    # encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

locals {
  project_name = "meeting-ai"
  environment  = "dev"
  
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
    Owner       = var.owner_email
    CostCenter  = var.cost_center
  }

  availability_zones = data.aws_availability_zones.available.names
}

data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name       = local.project_name
  environment        = local.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = slice(local.availability_zones, 0, 3)
  enable_nat_gateway = false # Cost savings for dev
  tags               = local.common_tags
}

# S3 Buckets
module "s3_raw_audio" {
  source = "../../modules/s3"

  project_name               = local.project_name
  environment                = local.environment
  bucket_suffix              = "raw-audio"
  enable_lifecycle           = true
  transition_to_ia_days      = 30
  transition_to_glacier_days = 90
  enable_event_notifications = true
  sqs_queue_arn              = aws_sqs_queue.audio_processing.arn
  event_filter_suffix        = ".wav"
  create_folders             = ["uploads", "processing", "processed"]
  tags                       = local.common_tags
}

module "s3_processed" {
  source = "../../modules/s3"

  project_name          = local.project_name
  environment           = local.environment
  bucket_suffix         = "processed-data"
  enable_lifecycle      = true
  transition_to_ia_days = 60
  create_folders        = ["transcripts", "embeddings", "insights"]
  tags                  = local.common_tags
}

module "s3_logs" {
  source = "../../modules/s3"

  project_name     = local.project_name
  environment      = local.environment
  bucket_suffix    = "logs"
  enable_lifecycle = true
  expiration_days  = 90
  tags             = local.common_tags
}

# RDS PostgreSQL with pgvector
module "rds" {
  source = "../../modules/rds-postgres"

  project_name            = local.project_name
  environment             = local.environment
  vpc_id                  = module.vpc.vpc_id
  subnet_ids              = module.vpc.private_subnet_ids
  allowed_security_groups = [aws_security_group.ecs_tasks.id]
  
  instance_class          = "db.t3.micro" # Cost savings for dev
  allocated_storage       = 20
  max_allocated_storage   = 100
  backup_retention_period = 1
  deletion_protection     = false
  skip_final_snapshot     = true
  
  tags = local.common_tags
}

# Security Groups
resource "aws_security_group" "alb" {
  name_prefix = "${local.project_name}-${local.environment}-alb-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for Application Load Balancer"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-alb-sg"
  })
}

resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${local.project_name}-${local.environment}-ecs-"
  vpc_id      = module.vpc.vpc_id
  description = "Security group for ECS tasks"

  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-${local.environment}-ecs-sg"
  })
}

# SQS Queue for audio processing
resource "aws_sqs_queue" "audio_processing" {
  name                       = "${local.project_name}-${local.environment}-audio-processing"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 10
  visibility_timeout_seconds = 300

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.audio_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = local.common_tags
}

resource "aws_sqs_queue" "audio_processing_dlq" {
  name                      = "${local.project_name}-${local.environment}-audio-processing-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = local.common_tags
}

# S3 bucket notification permission
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_trigger.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.s3_raw_audio.bucket_arn
}

# Placeholder Lambda for S3 triggers (to be implemented)
resource "aws_lambda_function" "s3_trigger" {
  filename      = "../../lambda-placeholder.zip"
  function_name = "${local.project_name}-${local.environment}-s3-trigger"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 60

  environment {
    variables = {
      SQS_QUEUE_URL = aws_sqs_queue.audio_processing.url
      ENVIRONMENT   = local.environment
    }
  }

  tags = local.common_tags
}

resource "aws_iam_role" "lambda_role" {
  name = "${local.project_name}-${local.environment}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "database_endpoint" {
  value     = module.rds.db_instance_endpoint
  sensitive = true
}

output "s3_raw_audio_bucket" {
  value = module.s3_raw_audio.bucket_id
}

output "sqs_queue_url" {
  value = aws_sqs_queue.audio_processing.url
}