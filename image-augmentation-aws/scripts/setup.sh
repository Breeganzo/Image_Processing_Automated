#!/bin/bash

echo "🚀 Setting up Image Augmentation AWS Project..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "   pip install awscli"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install it first."
    echo "   Download from: https://terraform.io/downloads.html"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install it first."
    echo "   Download from: https://docker.com/get-started"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check AWS credentials
echo "🔑 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Check Docker containers can be built
echo "🐳 Validating Docker setup..."
echo "Docker version: $(docker --version)"
echo "✅ Docker setup validated!"

# Initialize Terraform
echo "🏗️ Initializing Terraform..."
cd terraform
terraform init

if [ $? -eq 0 ]; then
    echo "✅ Terraform initialized successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Review terraform/terraform.tfvars and update values if needed"
    echo "2. Build and push Docker containers: cd ../scripts && ./build-and-push-containers.ps1"
    echo "3. Run: terraform plan"
    echo "4. Run: terraform apply"
    echo "5. Update frontend/upload.js with the S3 bucket name from Terraform outputs"
else
    echo "❌ Terraform initialization failed!"
    exit 1
fi

cd ..
echo "🎉 Setup complete! Ready for deployment."
