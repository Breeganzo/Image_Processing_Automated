# Image Augmentation AWS Workflow

## Overview
This project creates an automated image augmentation pipeline using AWS services. When you upload an image to S3 from VS Code, it triggers a series of Lambda functions that process and rotate the image in different angles.

## Architecture Workflow

```
1. Upload Image (VS Code) → S3 Bucket
2. S3 Event → Triggers Image Processor Lambda
3. Image Processor Lambda → Resizes image & sends SQS messages
4. SQS Messages → Trigger Rotation Worker Lambda
5. Rotation Worker Lambda → Rotates images (90°, 180°, 270°, 360°) → Saves to S3 folders
6. SQS Notifications → Confirm processing completion
```

## Detailed Step-by-Step Flow

### Step 1: Image Upload
- User uploads any image from VS Code to the S3 bucket
- S3 bucket is configured to trigger events on object creation

### Step 2: Initial Processing
- S3 event triggers the **Image Processor Lambda**
- Lambda function:
  - Downloads the uploaded image
  - Resizes it if larger than the configured limit
  - Saves the resized image back to S3
  - Sends 4 SQS messages (one for each rotation angle: 90°, 180°, 270°, 360°)

### Step 3: Rotation Processing
- Each SQS message triggers the **Rotation Worker Lambda**
- For each message, the Lambda:
  - Downloads the resized image from S3
  - Rotates it to the specified angle
  - Saves the rotated image to the corresponding S3 folder:
    - `augmented-images/90-degree/`
    - `augmented-images/180-degree/`
    - `augmented-images/270-degree/`
    - `augmented-images/360-degree/`

### Step 4: Notifications
- SQS provides reliable message delivery and retry logic
- Dead Letter Queue (DLQ) handles any failed processing
- CloudWatch logs capture all processing steps for monitoring

## S3 Bucket Structure

```
your-bucket-name/
├── original-image.jpg           # Your uploaded image
├── resized/
│   └── original-image.jpg       # Resized version (if needed)
└── augmented-images/
    ├── 90-degree/
    │   └── original-image.jpg
    ├── 180-degree/
    │   └── original-image.jpg
    ├── 270-degree/
    │   └── original-image.jpg
    └── 360-degree/
        └── original-image.jpg
```

## AWS Resources Created

1. **S3 Bucket** - Stores original and processed images
2. **Lambda Functions** (2):
   - Image Processor - Initial processing and SQS message generation
   - Rotation Worker - Image rotation processing
3. **SQS Queue** - Message queue for rotation tasks
4. **SQS Dead Letter Queue** - Handles failed messages
5. **IAM Roles & Policies** - Secure access between services
6. **CloudWatch Log Groups** - Logging and monitoring

## How to Use

### 1. Deploy the Infrastructure
```bash
cd scripts
./deploy.sh
```

### 2. Upload Images from VS Code
Use VS Code's AWS extension or AWS CLI:
```bash
aws s3 cp your-image.jpg s3://YOUR-BUCKET-NAME/
```

### 3. Monitor Processing
Check CloudWatch logs:
```bash
# Image Processor logs
aws logs tail /aws/lambda/image-augmentation-image-processor-dev --follow

# Rotation Worker logs  
aws logs tail /aws/lambda/image-augmentation-rotation-worker-dev --follow
```

### 4. View Results
Check the processed images:
```bash
aws s3 ls s3://YOUR-BUCKET-NAME/augmented-images/ --recursive
```

## Key Features

- **Automatic Processing**: No manual intervention needed
- **Scalable**: Handles multiple images concurrently
- **Reliable**: SQS ensures all rotations are processed
- **Cost-Effective**: Pay only for what you use
- **Monitoring**: Full CloudWatch integration
- **Error Handling**: Dead Letter Queue for failed processing

## Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Configuration Options
Edit `terraform/terraform.tfvars` to customize:
- Maximum image size (default: 10MB)
- Lambda timeout and memory
- AWS region
- Environment name
