variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "bucket_suffix" {
  description = "Suffix for the bucket name (e.g., 'audio', 'processed', 'logs')"
  type        = string
}

variable "enable_versioning" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "enable_lifecycle" {
  description = "Enable lifecycle rules for the bucket"
  type        = bool
  default     = true
}

variable "transition_to_ia_days" {
  description = "Days before transitioning to Infrequent Access"
  type        = number
  default     = 30
}

variable "transition_to_glacier_days" {
  description = "Days before transitioning to Glacier"
  type        = number
  default     = 90
}

variable "transition_to_deep_archive_days" {
  description = "Days before transitioning to Deep Archive"
  type        = number
  default     = 365
}

variable "enable_expiration" {
  description = "Enable object expiration"
  type        = bool
  default     = false
}

variable "expiration_days" {
  description = "Days before objects expire"
  type        = number
  default     = 730
}

variable "enable_cors" {
  description = "Enable CORS configuration"
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "enable_event_notifications" {
  description = "Enable S3 event notifications"
  type        = bool
  default     = false
}

variable "sqs_queue_arn" {
  description = "ARN of SQS queue for notifications"
  type        = string
  default     = null
}

variable "lambda_function_arn" {
  description = "ARN of Lambda function for notifications"
  type        = string
  default     = null
}

variable "event_filter_prefix" {
  description = "Prefix filter for S3 events"
  type        = string
  default     = ""
}

variable "event_filter_suffix" {
  description = "Suffix filter for S3 events"
  type        = string
  default     = ""
}

variable "enable_logging" {
  description = "Enable access logging"
  type        = bool
  default     = true
}

variable "logging_bucket" {
  description = "Target bucket for access logs"
  type        = string
  default     = null
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
  default     = null
}

variable "bucket_policy" {
  description = "JSON bucket policy"
  type        = string
  default     = null
}

variable "create_folders" {
  description = "List of folder paths to create in the bucket"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to apply to resources"
  type        = map(string)
  default     = {}
}