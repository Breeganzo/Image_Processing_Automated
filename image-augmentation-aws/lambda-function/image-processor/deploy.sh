#!/bin/bash

echo "🚀 Deploying Image Processor Lambda..."

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -t . --upgrade

# Create deployment package
echo "📦 Creating deployment package..."
zip -r image-processor.zip . -x "*.pyc" "__pycache__/*" "deploy.sh" "*.md"

# Update Lambda function (if it exists)
if aws lambda get-function --function-name image-augmentation-image-processor-dev >/dev/null 2>&1; then
    echo "🔄 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name image-augmentation-image-processor-dev \
        --zip-file fileb://image-processor.zip
else
    echo "ℹ️ Lambda function doesn't exist. Use Terraform to deploy infrastructure first."
fi

echo "✅ Image Processor deployment complete!"