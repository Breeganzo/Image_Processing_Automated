import json
import boto3
import urllib.parse
import os
import uuid
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    """
    Main function triggered when image uploaded to S3
    1. Validates image exists
    2. Sends rotation tasks to SQS (without resizing to avoid PIL dependency)
    """
    
    print(f"🚀 Image processor started at {datetime.utcnow()}")
    
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])
            
            print(f"📥 Processing: {key} from bucket: {bucket}")
            
            # Skip if already processed (avoid infinite loops)
            if key.startswith('processed/') or key.startswith('augmented-images/'):
                print(f"⏭️ Skipping already processed image: {key}")
                continue
            
            # Process the image
            success = process_image(bucket, key, context)
            
            if success:
                print(f"✅ Successfully processed: {key}")
            else:
                print(f"❌ Failed to process: {key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Images processed successfully')
        }
        
    except Exception as e:
        print(f"💥 Error in lambda_handler: {str(e)}")
        raise e

def process_image(bucket, key, context):
    """
    Process single image: validate and queue rotations
    """
    try:
        # Get image metadata
        print(f"⬇️ Getting image metadata: {key}")
        response = s3_client.head_object(Bucket=bucket, Key=key)
        content_type = response.get('ContentType', '')
        content_length = response.get('ContentLength', 0)
        
        print(f"📏 Content Type: {content_type}, Size: {content_length} bytes")
        
        # Validate it's an image
        if not content_type.startswith('image/'):
            print(f"⚠️ Skipping non-image file: {content_type}")
            return True
        
        # Check size (skip if too large)
        max_size = int(os.environ.get('MAX_IMAGE_SIZE_MB', 10)) * 1024 * 1024
        if content_length > max_size:
            print(f"⚠️ Image too large: {content_length} bytes > {max_size} bytes")
            return False
        
        # Queue rotation tasks directly on original image
        queue_rotations(bucket, key, context)
        
        return True
        
    except Exception as e:
        print(f"💥 Error processing image {key}: {str(e)}")
        return False

def queue_rotations(bucket, image_key, context):
    """
    Send rotation tasks to SQS queue
    """
    try:
        queue_url = os.environ['SQS_QUEUE_URL']
        angles = [90, 180, 270, 360]  # 360 = original
        
        print(f"📋 Queuing {len(angles)} rotation tasks")
        
        for angle in angles:
            message = {
                'task_id': str(uuid.uuid4()),
                'bucket': bucket,
                'image_key': image_key,
                'angle': angle,
                'request_id': context.aws_request_id
            }
            
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                MessageAttributes={
                    'angle': {'StringValue': str(angle), 'DataType': 'String'},
                    'bucket': {'StringValue': bucket, 'DataType': 'String'}
                }
            )
            
            print(f"✉️ Queued {angle}° rotation - MessageId: {response['MessageId']}")
        
        print(f"🎯 All rotation tasks queued successfully")
        
    except Exception as e:
        print(f"💥 Error queuing rotations: {str(e)}")
        raise e
