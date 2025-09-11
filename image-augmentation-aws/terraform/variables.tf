variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "project_name"{
    description = "Name of the project (used for resource naming)"
    type        = string
    default     = "image-augmentation"
    
    validation {
        condition     = can(regex("^[a-z0-9-]+$", var.project_name))
        error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
    }
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.environment))
    error_message = "Environment must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory" {
  description = "Memory size for Lambda functions in MB"
  type        = number
  default     = 512
}

variable "sqs_visibility_timeout" {
  description = "Visibility timeout for SQS queues in seconds"
  type        = number
  default     = 360  # Should be > Lambda timeout
}

variable "max_image_size_mb" {
  description = "Maximum image size in MB"
  type        = number
  default     = 10
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {
    Project     = "ImageAugmentation"
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}