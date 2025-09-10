# AWS Image Augmentation Pipeline

An automated image processing system built on AWS that resizes and rotates uploaded images using serverless architecture.

## 🏗️ Architecture

```
graph TD
    A[User Uploads Image] --> B[S3 Bucket - Original Images]
    B --> C[S3 Event Trigger]
    C --> D[Lambda: Image Processor]
    D --> E[Resize to 256x256]
    E --> F[SQS Queue - Rotation Tasks]
    F --> G[Lambda: Rotation Worker]
    G --> H[Generate 4 Rotations]
    H --> I[S3 Bucket - Augmented Images]
    
    I --> J[90-degree folder]
    I --> K[180-degree folder]
    I --> L[270-degree folder]
    I --> M[360-degree folder]
    
    subgraph "AWS Services Used"
        N[S3 - Storage]
        O[Lambda - Processing]
        P[SQS - Message Queue]
        Q[IAM - Permissions]
        R[CloudWatch - Monitoring]
    end
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style F fill:#f3e5f5
    style G fill:#e8f5e8
    style I fill:#fff8e1
```

## 🚀 Features

- **Automatic Processing**: Images are processed immediately upon upload
- **Parallel Processing**: Uses SQS for efficient task distribution
- **Multiple Rotations**: Generates 90°, 180°, 270°, and 360° rotated versions
- **Organized Storage**: Automatically organizes output by rotation angle
- **Serverless**: Built entirely on AWS serverless services

## 🔄 Workflow

1. **Image Upload**: Users upload images to the original S3 bucket
2. **Event Trigger**: S3 event automatically triggers the processing Lambda
3. **Image Processing**: Lambda resizes images to 256x256 pixels
4. **Queue Tasks**: Rotation tasks are queued in SQS for parallel processing
5. **Image Rotation**: Worker Lambda generates 4 rotated versions
6. **Storage**: Augmented images are organized in separate folders by rotation degree

## 📁 Project Structure

```
image-augmentation-aws/
├── README.md
├── .gitignore
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
├── lambda-functions/
│   ├── image-processor/
│   │   ├── lambda_function.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   └── rotation-worker/
│       ├── lambda_function.py
│       ├── requirements.txt
│       └── deploy.sh
├── frontend/
│   ├── index.html
│   ├── upload.js
│   └── styles.css
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── cleanup.sh
└── docs/
    ├── architecture.md
    └── troubleshooting.md

```

## 🛠️ AWS Services Used

| Service | Purpose |
|---------|---------|
| **S3** | Storage for original and processed images |
| **Lambda** | Serverless image processing functions |
| **SQS** | Message queue for rotation tasks |
| **IAM** | Access permissions and security |
| **CloudWatch** | Monitoring and logging |

## 🚀 Quick Start

1. Clone this repository
```
git clone <your-repo-url>
cd aws-image-augmentation-pipeline
```

2. Configure AWS credentials
```
aws configure
```

3. Deploy infrastructure
```
cd terraform
terraform init
terraform plan
terraform apply
```

4. Upload test images to the S3 bucket and watch the magic happen!

## 📊 Monitoring

The system includes CloudWatch monitoring for:
- Lambda execution metrics
- SQS queue depth and processing times
- S3 storage usage
- Error rates and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

Just copy and paste this entire content into your `README.md` file. The Mermaid diagram will render automatically on GitHub, showing your flowchart with proper styling and colors exactly as you designed it!
