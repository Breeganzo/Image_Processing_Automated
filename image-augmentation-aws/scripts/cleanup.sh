#!/bin/bash

echo "🧹 Cleaning up Image Augmentation Pipeline..."

# Change to terraform directory
cd terraform

# Warn user about destruction
echo "⚠️  WARNING: This will destroy all AWS resources created by this project!"
echo "This includes:"
echo "- S3 bucket and all stored images"
echo "- Lambda functions"
echo "- SQS queues"
echo "- CloudWatch log groups"
echo "- IAM roles and policies"
echo ""
echo "Are you sure you want to continue? (yes/no)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "🗑️ Destroying Terraform infrastructure..."
    terraform destroy
    
    if [ $? -eq 0 ]; then
        echo "✅ Cleanup completed successfully!"
        echo ""
        echo "🧹 Additional cleanup steps:"
        echo "1. Remove local lambda-functions/*.zip files if desired"
        echo "2. Remove terraform.tfstate files if desired"
        echo "3. Remove local Python packages from lambda-functions directories"
    else
        echo "❌ Cleanup failed! Please check for any remaining resources manually."
        exit 1
    fi
else
    echo "❌ Cleanup cancelled by user"
fi
