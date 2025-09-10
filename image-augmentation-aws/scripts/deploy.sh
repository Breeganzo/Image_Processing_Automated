#!/bin/bash

echo "🚀 Deploying Image Augmentation Pipeline to AWS..."

# Check if Docker containers have been built
echo "🐳 Checking Docker containers..."
if [ ! -f "../terraform/container-uris.txt" ]; then
    echo "❌ Docker containers not found!"
    echo "Please build and push containers first:"
    echo "   cd ../scripts && ./build-and-push-containers.ps1"
    exit 1
fi

echo "✅ Docker containers found!"

# Change to terraform directory
cd terraform

# Run terraform plan
echo "📋 Running Terraform plan..."
terraform plan -out=tfplan

if [ $? -ne 0 ]; then
    echo "❌ Terraform plan failed!"
    exit 1
fi

# Ask for confirmation
echo ""
echo "🤔 Do you want to apply these changes? (yes/no)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "🏗️ Applying Terraform configuration..."
    terraform apply tfplan
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment successful!"
        echo ""
        echo "📊 Deployment Summary:"
        echo "===================="
        terraform output
        echo ""
        echo "🎯 Next Steps:"
        echo "1. Copy the S3 bucket name from the output above"
        echo "2. Update frontend/upload.js with the bucket name"
        echo "3. Test the pipeline by uploading an image to the S3 bucket"
        echo ""
        echo "📝 To upload test image:"
        BUCKET_NAME=$(terraform output -raw s3_bucket_name)
        echo "   aws s3 cp your-image.jpg s3://$BUCKET_NAME/"
        echo ""
        echo "🔍 To monitor processing:"
        echo "   aws logs tail /aws/lambda/image-augmentation-image-processor-dev --follow"
        echo ""
        echo "📁 Check results in S3:"
        echo "   aws s3 ls s3://$BUCKET_NAME/augmented-images/ --recursive"
    else
        echo "❌ Deployment failed!"
        exit 1
    fi
else
    echo "❌ Deployment cancelled by user"
    exit 1
fi
