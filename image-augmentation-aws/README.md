# AWS Image Augmentation Pipeline

## 🎯 Project Overview

This project creates an automated image processing pipeline on AWS that:
- Accepts image uploads (JPG, PNG, JPEG)
- Automatically resizes images to 256×256 pixels
- Creates 4 rotated versions (90°, 180°, 270°, original)
- Stores processed images in organized S3 folders
- Uses serverless architecture for scalability and cost-efficiency

## 🏗️ Architecture

```
Frontend (HTML/JS) → S3 Bucket → Lambda (Image Processor) → SQS Queue → Lambda (Rotation Worker) → S3 (Organized Results)
                     ↓
                CloudWatch Logs (Monitoring)
```

### Components:
- **S3 Bucket**: Stores original and processed images
- **Lambda Functions**: 
  - Image Processor: Resizes images and queues rotation tasks
  - Rotation Worker: Processes individual rotation tasks
- **SQS Queue**: Manages rotation tasks with dead-letter queue for failed messages
- **CloudWatch**: Logging and monitoring
- **IAM Roles**: Secure permissions for AWS services

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** >= 1.0 installed
4. **Python 3.8+** installed
5. **Git** for version control

## 🚀 Deployment Guide

### Step 1: Clone and Setup
```bash
cd c:\Users\AnthonyBreeganzoT\My_Learning\AWS\Image_Processing_Automated\image-augmentation-aws
```

### Step 2: Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

### Step 3: Install Dependencies
```bash
# For image-processor Lambda
cd lambda-functions\image-processor
pip install -r requirements.txt -t . --upgrade

# For rotation-worker Lambda  
cd ..\rotation-worker
pip install -r requirements.txt -t . --upgrade

cd ..\..
```

### Step 4: Review Configuration
Edit `terraform\terraform.tfvars` if needed:
```hcl
project_name = "Image-Augmentation"
environment = "dev"
aws_region = "us-east-1"
lambda_timeout = 300
lambda_memory = 512
max_image_size_mb = 10
```

### Step 5: Deploy Infrastructure
```bash
cd terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan

# Deploy to AWS
terraform apply
```

### Step 6: Get Deployment Outputs
```bash
terraform output
```

### Step 7: Update Frontend Configuration
Update `frontend\upload.js` with the S3 bucket name from Terraform outputs:
```javascript
const AWS_CONFIG = {
    region: 'us-east-1',
    bucketName: 'YOUR_ACTUAL_BUCKET_NAME_FROM_OUTPUT', 
};
```

## 🧪 Testing Your Deployment

### 1. Test Lambda Functions
```bash
# Check if functions are deployed
aws lambda list-functions --query "Functions[?contains(FunctionName, 'Image-Augmentation')].[FunctionName,Runtime,LastModified]" --output table
```

### 2. Test S3 Upload
```bash
# Upload a test image
aws s3 cp test-image.jpg s3://YOUR_BUCKET_NAME/
```

### 3. Monitor Logs
```bash
# View image processor logs
aws logs tail /aws/lambda/Image-Augmentation-image-processor-dev --follow

# View rotation worker logs  
aws logs tail /aws/lambda/Image-Augmentation-rotation-worker-dev --follow
```

### 4. Check SQS Queue
```bash
# Check queue status
aws sqs get-queue-attributes --queue-url YOUR_QUEUE_URL --attribute-names All
```

## 📁 Folder Structure After Processing

```
S3 Bucket:
├── original-uploads/
│   └── your-image.jpg
├── processed/
│   └── your-image_256x256.jpg  
└── augmented-images/
    ├── 90-degree/
    │   └── processed_image_rotated_90_degrees_timestamp.jpg
    ├── 180-degree/
    │   └── processed_image_rotated_180_degrees_timestamp.jpg  
    ├── 270-degree/
    │   └── processed_image_rotated_270_degrees_timestamp.jpg
    └── 360-degree/
        └── processed_image_original_timestamp.jpg
```

## 🔧 Troubleshooting

### Common Issues:
1. **Lambda Timeout**: Increase `lambda_timeout` in terraform.tfvars
2. **Memory Issues**: Increase `lambda_memory` for large images
3. **Permission Errors**: Check IAM roles and policies
4. **SQS Messages Stuck**: Check dead-letter queue for failed messages

### Debug Commands:
```bash
# Check Lambda function status
aws lambda get-function --function-name YOUR_FUNCTION_NAME

# Check recent Lambda invocations
aws logs filter-log-events --log-group-name /aws/lambda/YOUR_FUNCTION_NAME --start-time $(date -d '1 hour ago' +%s)000

# Check SQS queue metrics
aws cloudwatch get-metric-statistics --namespace AWS/SQS --metric-name NumberOfMessagesSent --start-time $(date -d '1 hour ago' --iso-8601) --end-time $(date --iso-8601) --period 300 --statistics Sum --dimensions Name=QueueName,Value=YOUR_QUEUE_NAME
```

## 💰 Cost Optimization

- **Lambda**: Pay per execution (first 1M requests/month free)
- **S3**: Pay for storage and requests (~$0.023/GB/month)
- **SQS**: Pay per request (first 1M requests/month free)
- **CloudWatch**: Pay for log storage and monitoring

## 🧹 Cleanup

To avoid charges, destroy resources when done:
```bash
cd terraform
terraform destroy
```

## 🔄 CI/CD Integration

For production deployments, consider:
1. **GitHub Actions** for automated deployments
2. **AWS CodePipeline** for AWS-native CI/CD
3. **Environment-specific tfvars** files
4. **State file management** with S3 backend

## 📊 Monitoring Dashboard

Create CloudWatch dashboards to monitor:
- Lambda execution duration and errors
- S3 request metrics
- SQS queue depth and processing time
- Overall system health
