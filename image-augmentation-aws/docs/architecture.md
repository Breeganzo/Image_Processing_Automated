# 🏗️ AWS Image Augmentation Pipeline - Architecture & Deployment Guide

## 🎯 What Exactly This Project Does

Your project is an **automated image processing pipeline** that:

1. **Takes any image** (JPG, PNG, JPEG) up to 10MB
2. **Automatically resizes** it to 256×256 pixels (maintains aspect ratio, adds white background if needed)
3. **Creates 4 rotated versions**: 90°, 180°, 270°, and original (360°)
4. **Organizes results** in S3 folders by rotation angle
5. **Processes everything serverlessly** - no servers to manage!

## 🔄 Complete Processing Flow

```
User Upload → S3 Event → Lambda Container → Resize Image → Queue Tasks → Parallel Processing → 4 Rotated Images
     ↓           ↓            ↓              ↓             ↓              ↓                   ↓
  image.jpg   Triggers    Image Processor  256×256.jpg  SQS Queue   Rotation Worker     Organized Results
                         (Docker)                                   (Docker)
```

## 🏗️ Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Upload   │    │   S3 Bucket     │    │   Lambda        │
│   (Any Method)  │───▶│  Trigger Event  │───▶│ Image Processor │
│                 │    │                 │    │ (Docker Image)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │  SQS Message    │    │  SQS Message    │    │  SQS Message    │
                    │   (90° Task)    │    │  (180° Task)    │    │  (270° Task)    │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │                         │
                              ▼                         ▼                         ▼
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │   Lambda        │    │   Lambda        │    │   Lambda        │
                    │ Rotation Worker │    │ Rotation Worker │    │ Rotation Worker │
                    │ (Docker Image)  │    │ (Docker Image)  │    │ (Docker Image)  │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │                         │
                              ▼─────────────────────────┼─────────────────────────▼
                                          ┌─────────────────┐
                                          │   S3 Bucket     │
                                          │ Organized by    │
                                          │ Rotation Angle  │
                                          └─────────────────┘
                                                    │
                                                    ▼
                                          ┌─────────────────┐
                                          │   CloudWatch    │
                                          │  Logs & ECR     │
                                          └─────────────────┘
```

## Components Detail

### 1. Frontend Layer
- **Technology**: HTML5, CSS3, JavaScript
- **Features**:
  - Drag & drop file upload
  - File validation (type, size)
  - Progress tracking
  - Results display
- **Location**: `frontend/`

### 2. Storage Layer (S3)
- **Bucket Structure**:
  ```
  bucket-name/
  ├── original-uploads/     # Raw uploaded images
  ├── processed/           # Resized 256x256 images
  └── augmented-images/    # Rotated versions
      ├── 90-degree/
      ├── 180-degree/
      ├── 270-degree/
      └── 360-degree/
  ```
- **Features**:
  - Versioning enabled
  - Server-side encryption (AES256)
  - Lifecycle policies for cleanup
  - Event notifications

## 🚀 How to Deploy and Run Your Project

### Prerequisites Check
```bash
# 1. AWS CLI configured
aws sts get-caller-identity

# 2. Docker installed and running  
docker --version

# 3. Terraform installed
terraform --version
```

### Step-by-Step Deployment

#### 1. Initial Setup
```bash
cd C:\Users\AnthonyBreeganzoT\My_Learning\AWS\Image_Processing_Automated\image-augmentation-aws\scripts
./setup.sh
```

#### 2. Build & Push Docker Containers
```powershell
.\build-and-push-containers.ps1
```
**This creates:**
- ECR repositories in your AWS account
- Docker images for both Lambda functions
- Pushes containers to ECR

#### 3. Deploy Infrastructure
```bash
./deploy.sh
```
**This creates:**
- S3 bucket for images
- 2 Lambda functions (containerized)
- SQS queue for task management
- IAM roles and policies
- CloudWatch log groups

### What Gets Created in AWS

| Service | Resource Name | Purpose |
|---------|---------------|---------|
| **S3** | `Image-Augmentation-dev-XXXXXX` | Stores original and processed images |
| **Lambda** | `Image-Augmentation-image-processor-dev` | Resizes images |
| **Lambda** | `Image-Augmentation-rotation-worker-dev` | Creates rotations |
| **SQS** | `Image-Augmentation-rotation-queue-dev` | Task management |
| **SQS** | `Image-Augmentation-rotation-dlq-dev` | Failed message handling |
| **ECR** | `Image-Augmentation-image-processor` | Docker container storage |
| **ECR** | `Image-Augmentation-rotation-worker` | Docker container storage |
| **CloudWatch** | Log groups for monitoring | Function execution logs |

### 3. Container Registry (ECR)
- **Image Storage**: Stores Docker container images for Lambda functions
- **Security**: Image vulnerability scanning enabled
- **Versioning**: Automatic image tagging and version management
- **Repositories**:
  - `Image-Augmentation-image-processor`: Container for image processing
  - `Image-Augmentation-rotation-worker`: Container for rotation tasks

### 4. Processing Layer (Lambda with Containers)

#### Image Processor Function (Docker Container)
- **Base Image**: `public.ecr.aws/lambda/python:3.9`
- **Dependencies**: Pillow, boto3, botocore (in container)
- **Memory**: 512MB (configurable)
- **Timeout**: 300 seconds (configurable)
- **Triggers**: S3 ObjectCreated events
- **Container Features**:
  - Pre-installed Python dependencies
  - Optimized for cold starts
  - Easy local testing with Docker
- **Functions**:
  - Download uploaded image from S3
  - Resize to 256×256 pixels using Pillow
  - Maintain aspect ratio with white background
  - Queue rotation tasks to SQS

#### Rotation Worker Function (Docker Container)
- **Base Image**: `public.ecr.aws/lambda/python:3.9`
- **Dependencies**: Pillow, boto3, botocore (in container)
- **Memory**: 512MB (configurable)
- **Timeout**: 300 seconds (configurable)
- **Triggers**: SQS messages
- **Container Features**:
  - Same base image as processor for consistency
  - Efficient image rotation algorithms
  - Parallel processing capability
- **Functions**:
  - Process individual rotation tasks from SQS
  - Create rotated versions (90°, 180°, 270°, original)
  - Save to organized S3 folders with timestamps

### 4. Message Queue Layer (SQS)
- **Queue Type**: Standard Queue
- **Features**:
  - Visibility timeout: 360 seconds
  - Message retention: 14 days
  - Dead letter queue for failed messages
  - Batch processing (up to 5 messages)

### 5. Monitoring Layer (CloudWatch)
- **Log Groups**:
  - `/aws/lambda/image-augmentation-image-processor-dev`
  - `/aws/lambda/image-augmentation-rotation-worker-dev`
- **Retention**: 14 days
- **Features**:
  - Function execution logs
  - Error tracking
  - Performance metrics

### 6. Security Layer (IAM)
- **Lambda Execution Role**:
  - CloudWatch Logs permissions
  - S3 read/write permissions
  - SQS send/receive permissions
- **Principle**: Least privilege access

## Data Flow

1. **Upload**: User uploads image via frontend
2. **Trigger**: S3 ObjectCreated event triggers Image Processor Lambda
3. **Process**: Lambda resizes image to 256×256 pixels
4. **Queue**: Rotation tasks sent to SQS queue (4 messages: 90°, 180°, 270°, 360°)
5. **Execute**: SQS triggers Rotation Worker Lambda for each message
6. **Rotate**: Worker creates rotated version and saves to S3
7. **Complete**: All 4 rotated images available in organized folders

## Scalability Features

### Automatic Scaling
- **Lambda**: Scales automatically based on incoming requests
- **SQS**: Handles message queuing and delivery
- **S3**: Unlimited storage capacity

### Concurrency Controls
- **Lambda Concurrency**: Maximum 10 concurrent executions
- **SQS Batch Size**: Up to 5 messages processed together
- **Error Handling**: Dead letter queue for failed messages

### Performance Optimization
- **Memory Allocation**: 512MB for image processing operations
- **Timeout Configuration**: 300 seconds for large images
- **Connection Reuse**: Boto3 clients initialized outside handlers

## 📤 How to Upload Images and Test

### Method 1: Direct S3 Upload (Recommended for Testing)
```bash
# Get your bucket name from Terraform output
cd terraform
terraform output s3_bucket_name

# Upload test image directly to S3
aws s3 cp your-test-image.jpg s3://YOUR_BUCKET_NAME/
```

### Method 2: Using the Frontend (After Configuration)
1. **Update frontend configuration:**
   ```javascript
   // Edit frontend/upload.js
   const AWS_CONFIG = {
       region: 'us-east-1',
       bucketName: 'YOUR_ACTUAL_BUCKET_NAME', // From terraform output
   };
   ```

2. **Open frontend/index.html** in your browser
3. **Drag and drop** or click to select an image
4. **Upload** and watch the progress

### Method 3: AWS Console Upload
1. Open AWS S3 Console
2. Find your bucket: `Image-Augmentation-dev-XXXXXX`
3. Click "Upload" and select your image

## 🔍 How to Check Results

### 1. Monitor Processing in Real-Time
```bash
# Watch image processor logs
aws logs tail /aws/lambda/Image-Augmentation-image-processor-dev --follow

# Watch rotation worker logs  
aws logs tail /aws/lambda/Image-Augmentation-rotation-worker-dev --follow
```

### 2. Check S3 Bucket Structure
```bash
# List all processed images
aws s3 ls s3://YOUR_BUCKET_NAME/ --recursive

# Expected structure after processing:
# original-image.jpg                           (your upload)
# processed/original-image_256x256.jpg         (resized version)
# augmented-images/90-degree/...               (90° rotation)
# augmented-images/180-degree/...              (180° rotation) 
# augmented-images/270-degree/...              (270° rotation)
# augmented-images/360-degree/...              (original/360°)
```

### 3. Download Results
```bash
# Download all processed images
aws s3 sync s3://YOUR_BUCKET_NAME/augmented-images/ ./downloaded-results/

# Or browse in AWS Console
```

### 4. Verify SQS Processing
```bash
# Check queue status (should be empty after processing)
aws sqs get-queue-attributes --queue-url YOUR_QUEUE_URL --attribute-names All
```

## ⚡ Expected Processing Times
- **Small images (<1MB)**: ~5-10 seconds total
- **Medium images (1-5MB)**: ~10-20 seconds total  
- **Large images (5-10MB)**: ~20-45 seconds total

## 🎯 Testing Checklist

After deployment, test with these steps:
1. ✅ Upload a test image to S3
2. ✅ Check CloudWatch logs for processing activity
3. ✅ Verify 4 rotated images appear in S3
4. ✅ Confirm images are properly rotated and named
5. ✅ Test with different image formats (JPG, PNG)

## Cost Optimization

### Pay-per-Use Services
- **Lambda**: First 1M requests/month free
- **S3**: ~$0.023/GB/month for storage
- **SQS**: First 1M requests/month free
- **CloudWatch**: Pay for log storage

### Resource Efficiency
- **Right-sizing**: Optimal memory allocation for workload
- **Lifecycle Policies**: Automatic cleanup of old versions
- **Compression**: JPEG format with 90% quality for balance

## Security Considerations

### Data Protection
- **Encryption**: Server-side encryption for all S3 objects
- **Access Control**: IAM policies restrict access to specific resources
- **Network**: No public access to Lambda functions

### Compliance
- **Logging**: All operations logged to CloudWatch
- **Audit Trail**: S3 object metadata tracks processing history
- **Retention**: Log retention policies for compliance requirements

## Monitoring & Observability

### Key Metrics
- **Lambda Duration**: Function execution time
- **Error Rate**: Failed executions percentage  
- **SQS Depth**: Queue message count
- **S3 Requests**: Upload/download operations

### Alerting (Recommended)
- Lambda function errors
- SQS queue depth threshold
- S3 bucket size monitoring
- Cost threshold alerts

## Disaster Recovery

### Backup Strategy
- **S3 Versioning**: Multiple versions of objects retained
- **Cross-Region**: Consider cross-region replication for critical data
- **Infrastructure**: Terraform state provides infrastructure backup

### Recovery Procedures
- **Lambda**: Automatic recovery via AWS
- **SQS**: Messages persist until processed or expired
- **S3**: Object versioning allows recovery
- **Infrastructure**: `terraform apply` recreates resources
