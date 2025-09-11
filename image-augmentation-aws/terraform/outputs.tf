# Output important values after deployment
output "s3_bucket_name" {
  description = "Name of the S3 bucket for images"
  value       = aws_s3_bucket.image_bucket.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.image_bucket.arn
}

output "image_processor_function_name" {
  description = "Name of the image processor Lambda function"
  value       = aws_lambda_function.image_processor.function_name
}

output "rotation_worker_function_name" {
  description = "Name of the rotation worker Lambda function"
  value       = aws_lambda_function.rotation_worker.function_name
}

output "sqs_queue_url" {
  description = "URL of the SQS queue"
  value       = aws_sqs_queue.rotation_queue.url
}

output "sqs_dlq_url" {
  description = "URL of the dead letter queue"
  value       = aws_sqs_queue.rotation_dlq.url
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups for monitoring"
  value = {
    image_processor = aws_cloudwatch_log_group.image_processor_logs.name
    rotation_worker = aws_cloudwatch_log_group.rotation_worker_logs.name
  }
}

output "deployment_info" {
  description = "Deployment information"
  value = {
    region      = var.aws_region
    environment = var.environment
    project     = var.project_name
  }
}

output "upload_instruction" {
  description = "Instruction to upload images"
  value = "Upload images to s3://${aws_s3_bucket.image_bucket.bucket}/ to trigger automatic processing"
}

output "aws_region" {
  description = "AWS Region where resources are deployed"
  value       = var.aws_region
}