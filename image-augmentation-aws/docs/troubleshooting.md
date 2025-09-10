# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Terraform Issues

#### Issue: "No such file or directory" for Lambda ZIP files
**Error**: `Error: open ../lambda-packages/image-processor.zip: no such file or directory`

**Solution**:
```powershell
# Run the package creation script first
cd scripts
.\create-lambda-packages.ps1

# Then proceed with Terraform
cd ..\terraform
terraform plan
```

#### Issue: AWS Credentials Not Found
**Error**: `Error: no valid credential sources found`

**Solution**:
```bash
# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region, and Output format

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Issue: Region Mismatch
**Error**: `InvalidLocationConstraint: The specified location-constraint is not valid`

**Solution**:
Update `terraform/terraform.tfvars`:
```hcl
aws_region = "your-preferred-region"  # e.g., "us-west-2"
```

### 2. Lambda Function Issues

#### Issue: Lambda Function Timeout
**Error**: `Task timed out after 300.00 seconds`

**Solution**:
Increase timeout in `terraform/terraform.tfvars`:
```hcl
lambda_timeout = 600  # Increase to 10 minutes
```

#### Issue: Lambda Out of Memory
**Error**: `Process exited before completing request`

**Solution**:
Increase memory in `terraform/terraform.tfvars`:
```hcl
lambda_memory = 1024  # Increase to 1GB
```

#### Issue: Pillow Import Error
**Error**: `Unable to import module 'lambda_function': No module named 'PIL'`

**Solution**:
Recreate Lambda packages:
```powershell
cd scripts
.\create-lambda-packages.ps1
cd ..\terraform
terraform apply
```

### 3. S3 Issues

#### Issue: Access Denied to S3 Bucket
**Error**: `An error occurred (AccessDenied) when calling the PutObject operation`

**Solution**:
1. Check IAM permissions in Terraform
2. Verify bucket policy
3. Ensure Lambda role has correct permissions

#### Issue: Large File Upload Fails
**Error**: `Request entity too large`

**Solution**:
Adjust file size limit in `terraform/terraform.tfvars`:
```hcl
max_image_size_mb = 50  # Increase limit
```

### 4. SQS Issues

#### Issue: Messages Stuck in Queue
**Error**: Messages visible but not processed

**Solution**:
1. Check Lambda function logs:
```bash
aws logs tail /aws/lambda/Image-Augmentation-rotation-worker-dev --follow
```

2. Check dead letter queue:
```bash
aws sqs receive-message --queue-url YOUR_DLQ_URL
```

3. Manually purge queue if needed:
```bash
aws sqs purge-queue --queue-url YOUR_QUEUE_URL
```

#### Issue: SQS Visibility Timeout Too Short
**Error**: Messages reprocessed multiple times

**Solution**:
Update `terraform/terraform.tfvars`:
```hcl
sqs_visibility_timeout = 900  # 15 minutes (must be > lambda_timeout)
```

### 5. Image Processing Issues

#### Issue: Unsupported Image Format
**Error**: `PIL cannot identify image file`

**Solution**:
1. Check supported formats: JPG, JPEG, PNG
2. Validate file is not corrupted
3. Add format validation in Lambda code

#### Issue: Image Rotation Quality Loss
**Error**: Processed images appear blurry

**Solution**:
Update quality settings in Lambda code:
```python
# In rotation-worker lambda_function.py
rotated.save(output_buffer, format='JPEG', quality=95)  # Increase quality
```

### 6. Frontend Issues

#### Issue: Upload Button Not Working
**Error**: No response when clicking upload

**Solution**:
1. Update S3 bucket name in `frontend/upload.js`:
```javascript
const AWS_CONFIG = {
    region: 'us-east-1',
    bucketName: 'YOUR_ACTUAL_BUCKET_NAME',  // Update this!
};
```

2. Check browser console for JavaScript errors

#### Issue: CORS Errors
**Error**: `Access to XMLHttpRequest at 'https://s3.amazonaws.com' blocked by CORS`

**Solution**:
Add CORS configuration to S3 bucket in Terraform:
```hcl
resource "aws_s3_bucket_cors_configuration" "image_bucket_cors" {
  bucket = aws_s3_bucket.image_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
```

### 7. Performance Issues

#### Issue: Slow Image Processing
**Error**: Processing takes longer than expected

**Solution**:
1. Increase Lambda memory (more CPU allocated):
```hcl
lambda_memory = 1024  # or 1536, 2048
```

2. Optimize image processing code:
```python
# Use more efficient resizing
image.thumbnail((256, 256), Image.Resampling.LANCZOS)
```

#### Issue: High Lambda Costs
**Error**: Unexpected high bills

**Solution**:
1. Monitor execution duration
2. Optimize memory allocation
3. Add timeout limits
4. Consider reserved concurrency

### 8. Monitoring and Debugging

#### Useful Commands for Debugging

**Check Lambda Function Status**:
```bash
aws lambda get-function --function-name Image-Augmentation-image-processor-dev
```

**Monitor Logs in Real-time**:
```bash
aws logs tail /aws/lambda/Image-Augmentation-image-processor-dev --follow
```

**Check SQS Queue Status**:
```bash
aws sqs get-queue-attributes --queue-url YOUR_QUEUE_URL --attribute-names All
```

**List S3 Objects**:
```bash
aws s3 ls s3://YOUR_BUCKET_NAME/augmented-images/ --recursive
```

**Check Recent Lambda Invocations**:
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/Image-Augmentation-image-processor-dev \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### CloudWatch Metrics to Monitor

1. **Lambda Metrics**:
   - Duration
   - Error count
   - Invocation count
   - Throttles

2. **SQS Metrics**:
   - Messages sent
   - Messages visible
   - Messages deleted
   - Queue depth

3. **S3 Metrics**:
   - Number of objects
   - Bucket size
   - Request count

### 9. Recovery Procedures

#### Recreate All Resources
```bash
cd terraform
terraform destroy  # Clean slate
terraform apply    # Recreate everything
```

#### Reset SQS Queues
```bash
aws sqs purge-queue --queue-url YOUR_QUEUE_URL
aws sqs purge-queue --queue-url YOUR_DLQ_URL
```

#### Clear S3 Bucket (Careful!)
```bash
aws s3 rm s3://YOUR_BUCKET_NAME --recursive
```

### 10. Getting Help

#### Enable Debug Logging
Add to Lambda functions:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

#### Contact Points
1. Check AWS Service Health Dashboard
2. Review AWS Documentation
3. Post on AWS Forums or Stack Overflow
4. Check project GitHub issues

#### Log Collection
Always include these in bug reports:
- Terraform output
- Lambda function logs
- SQS queue attributes
- Error messages with timestamps
- File sizes and formats being processed
