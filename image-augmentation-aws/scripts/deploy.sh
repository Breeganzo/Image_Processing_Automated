#!/bin/bash

# Image Augmentation AWS - Simple Deploy Script
# This script deploys the AWS infrastructure using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment of Image Augmentation AWS infrastructure...${NC}"

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed. Please install Terraform first.${NC}"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed. Please install AWS CLI first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Navigate to terraform directory
cd "$(dirname "$0")/../terraform"

echo -e "${YELLOW}Initializing Terraform...${NC}"
terraform init

echo -e "${YELLOW}Validating Terraform configuration...${NC}"
terraform validate

echo -e "${YELLOW}Planning deployment...${NC}"
terraform plan

echo -e "${YELLOW}Applying Terraform configuration...${NC}"
terraform apply -auto-approve

echo -e "${GREEN}Deployment completed successfully!${NC}"

# Display important outputs
echo -e "\n${YELLOW}Important Information:${NC}"
echo -e "S3 Bucket: $(terraform output -raw s3_bucket_name)"
echo -e "Image Processor Lambda: $(terraform output -raw image_processor_function_name)"
echo -e "Rotation Worker Lambda: $(terraform output -raw rotation_worker_function_name)"
echo -e "SQS Queue URL: $(terraform output -raw sqs_queue_url)"
echo -e "\n${GREEN}Upload images to the S3 bucket to start automatic processing!${NC}"
