#!/bin/bash

echo "🚀 Deploying Rotation Worker Lambda..."

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -t . --upgrade

# Create deployment package
echo "📦 Creating deployment package..."
zip -r rotation-worker.zip . -x "*.pyc" "__pycache__/*" "deploy.sh" "*.md"

# Update Lambda function (if it exists)
if aws lambda get-function --function-name image-augmentation-rotation-worker-dev >/dev/null 2>&1; then
    echo "🔄 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name image-augmentation-rotation-worker-dev \
        --zip-file fileb://rotation-worker.zip
else
    echo "ℹ️ Lambda function doesn't exist. Use Terraform to deploy infrastructure first."
fi

echo "✅ Rotation Worker deployment complete!"