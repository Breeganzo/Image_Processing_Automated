terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws"{
    region = var.aws_region
    default_tags{
        tags = var.tags
    }
}

# Random suffix for unique resource names
resource "random_string" "suffix"{
    length = 6
    special = false
    upper = false
}

resource "aws_s3_bucket" "image_bucket" {
    bucket = "${lower(var.project_name)}-${lower(var.environment)}-${random_string.suffix.result}"
}

resource "aws_s3_bucket_versioning" "image_bucket_versioning" {
    bucket = aws_s3_bucket.image_bucket.id
    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "image_bucket_encryption" {
    bucket = aws_s3_bucket.image_bucket.id
    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

resource "aws_s3_bucket_lifecycle_configuration" "image_bucket_lifecycle" {
    bucket = aws_s3_bucket.image_bucket.id
    rule {
        id     = "delete_old_versions"
        status = "Enabled"
        filter {
            prefix = ""
        }
        noncurrent_version_expiration {
            noncurrent_days = 30
        }
    }
}

# SQS queue for processing images
resource "aws_sqs_queue" "rotation_queue" {
    name                      = "${var.project_name}-rotation-queue-${var.environment}"
    visibility_timeout_seconds = var.sqs_visibility_timeout
    message_retention_seconds  = 1209600  # 14 days
    redrive_policy = jsonencode({
        deadLetterTargetArn = aws_sqs_queue.rotation_dlq.arn
        maxReceiveCount     = 3
    })
}

# Dead-letter queue for failed messages
resource "aws_sqs_queue" "rotation_dlq" {
    name = "${var.project_name}-rotation-dlq-${var.environment}"
    message_retention_seconds = 1209600  # 14 days
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "image_processor_logs" {
    name              = "/aws/lambda/${var.project_name}-image-processor-${var.environment}"
    retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "rotation_worker_logs" {
    name              = "/aws/lambda/${var.project_name}-rotation-worker-${var.environment}"
    retention_in_days = 14
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
    name               = "${var.project_name}-lambda-role-${var.environment}"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action    = "sts:AssumeRole"
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
                Effect    = "Allow"
            }
        ]
    })
}

#IAM Policy for Lambda functions
# IAM Policy for Lambda functions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_cloudwatch_log_group.image_processor_logs.arn,
          aws_cloudwatch_log_group.rotation_worker_logs.arn,
          "${aws_cloudwatch_log_group.image_processor_logs.arn}:*",
          "${aws_cloudwatch_log_group.rotation_worker_logs.arn}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:HeadObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.image_bucket.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.image_bucket.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.rotation_queue.arn,
          aws_sqs_queue.rotation_dlq.arn
        ]
      }
    ]
  })
}

# Attach basic Lambda execution role to the Lambda IAM role
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Create ZIP packages for Lambda deployment (code only, no dependencies)
data "archive_file" "image_processor_zip" {
  type        = "zip"
  source_dir  = "../lambda-function/image-processor"
  output_path = "../lambda-function/image-processor.zip"
  excludes    = ["*.md", "deploy.sh", "requirements.txt", "build"]
}

data "archive_file" "rotation_worker_zip" {
  type        = "zip"
  source_dir  = "../lambda-function/rotation-worker"
  output_path = "../lambda-function/rotation-worker.zip"
  excludes    = ["*.md", "deploy.sh", "requirements.txt", "build"]
}

# Lambda function for image processing (ZIP-based)
resource "aws_lambda_function" "image_processor" {
  function_name    = "${var.project_name}-image-processor-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  filename        = data.archive_file.image_processor_zip.output_path
  source_code_hash = data.archive_file.image_processor_zip.output_base64sha256
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory

  environment {
    variables = {
      SQS_QUEUE_URL     = aws_sqs_queue.rotation_queue.url
      S3_BUCKET         = aws_s3_bucket.image_bucket.bucket
      ENVIRONMENT       = var.environment
      MAX_IMAGE_SIZE_MB = var.max_image_size_mb
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.image_processor_logs
  ]
}

# Lambda function for rotating images (ZIP-based)
resource "aws_lambda_function" "rotation_worker" {
  function_name    = "${var.project_name}-rotation-worker-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  filename        = data.archive_file.rotation_worker_zip.output_path
  source_code_hash = data.archive_file.rotation_worker_zip.output_base64sha256
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory

  environment {
    variables = {
      S3_BUCKET   = aws_s3_bucket.image_bucket.bucket
      ENVIRONMENT = var.environment
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.rotation_worker_logs
  ]
}

#S3 bucket notification to trigger image processor Lambda
resource "aws_s3_bucket_notification" "image_bucket_notification" {
    bucket = aws_s3_bucket.image_bucket.id

    lambda_function {
        lambda_function_arn = aws_lambda_function.image_processor.arn
        events              = ["s3:ObjectCreated:*"]
        filter_prefix       = ""
        filter_suffix       = ".jpg"
    }

    lambda_function {
        lambda_function_arn = aws_lambda_function.image_processor.arn
        events              = ["s3:ObjectCreated:*"]
        filter_prefix       = ""
        filter_suffix       = ".png"
    }

    lambda_function {
        lambda_function_arn = aws_lambda_function.image_processor.arn
        events              = ["s3:ObjectCreated:*"]
        filter_prefix       = ""
        filter_suffix       = ".jpeg"
    }
    depends_on = [ aws_lambda_permission.s3_lambda_permission ]
}

# SQS event source mapping for rotation worker Lambda
resource "aws_lambda_event_source_mapping" "sqs_trigger"{
    event_source_arn = aws_sqs_queue.rotation_queue.arn
    function_name    = aws_lambda_function.rotation_worker.arn
    batch_size       = 5 # upto 5 messages at once

    scaling_config {
      maximum_concurrency = 10 # Max concurrent Lambda executions
    }
}

# Lambda permission for S3 to invoke the image processor
resource "aws_lambda_permission" "s3_lambda_permission" {
    statement_id  = "AllowExecutionFromS3Bucket"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.image_processor.function_name
    principal     = "s3.amazonaws.com"
    source_arn    = aws_s3_bucket.image_bucket.arn
}