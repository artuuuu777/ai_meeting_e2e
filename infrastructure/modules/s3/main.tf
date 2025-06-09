resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}-${var.bucket_suffix}"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-${var.bucket_suffix}"
  })
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  count  = var.enable_lifecycle ? 1 : 0
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = var.transition_to_ia_days
      storage_class = "STANDARD_IA"
    }
  }

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    transition {
      days          = var.transition_to_glacier_days
      storage_class = "GLACIER_FLEXIBLE_RETRIEVAL"
    }
  }

  rule {
    id     = "transition-to-deep-archive"
    status = "Enabled"

    transition {
      days          = var.transition_to_deep_archive_days
      storage_class = "DEEP_ARCHIVE"
    }
  }

  rule {
    id     = "expire-old-objects"
    status = var.enable_expiration ? "Enabled" : "Disabled"

    expiration {
      days = var.expiration_days
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "main" {
  count  = var.enable_cors ? 1 : 0
  bucket = aws_s3_bucket.main.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = var.cors_allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_notification" "main" {
  count  = var.enable_event_notifications ? 1 : 0
  bucket = aws_s3_bucket.main.id

  dynamic "sqs_queue" {
    for_each = var.sqs_queue_arn != null ? [1] : []
    content {
      queue_arn     = var.sqs_queue_arn
      events        = ["s3:ObjectCreated:*"]
      filter_prefix = var.event_filter_prefix
      filter_suffix = var.event_filter_suffix
    }
  }

  dynamic "lambda_function" {
    for_each = var.lambda_function_arn != null ? [1] : []
    content {
      lambda_function_arn = var.lambda_function_arn
      events              = ["s3:ObjectCreated:*"]
      filter_prefix       = var.event_filter_prefix
      filter_suffix       = var.event_filter_suffix
    }
  }
}

resource "aws_s3_bucket_logging" "main" {
  count  = var.enable_logging ? 1 : 0
  bucket = aws_s3_bucket.main.id

  target_bucket = var.logging_bucket
  target_prefix = "${var.project_name}/${var.environment}/${var.bucket_suffix}/"
}

# Bucket policy for CloudFront OAI or specific services
resource "aws_s3_bucket_policy" "main" {
  count  = var.bucket_policy != null ? 1 : 0
  bucket = aws_s3_bucket.main.id
  policy = var.bucket_policy
}

# Create folders structure
resource "aws_s3_object" "folders" {
  for_each = toset(var.create_folders)
  bucket   = aws_s3_bucket.main.id
  key      = "${each.value}/"
  content  = ""
}