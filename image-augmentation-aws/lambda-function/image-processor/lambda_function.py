import json
import boto3
import urllib.parse
from PIL import Image
import io
import os
import uuid
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    """
    Main function triggered when image uploaded to S3
    1. Downloads image
    2. Resizes to 256x256
    3. Sends rotation tasks to SQS
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
    Process single image: resize and queue rotations
    """
    try:
        # Download image
        print(f"⬇️ Downloading image: {key}")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        
        # Open and process image
        image = Image.open(io.BytesIO(image_data))
        print(f"📏 Original size: {image.size}, Mode: {image.mode}")
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'P', 'L'):
            image = image.convert('RGB')
        
        # Resize to 256x256 (maintain aspect ratio)
        image.thumbnail((256, 256), Image.Resampling.LANCZOS)
        
        # Create 256x256 canvas with white background
        canvas = Image.new('RGB', (256, 256), (255, 255, 255))
        
        # Center the image on canvas
        x = (256 - image.size[0]) // 2
        y = (256 - image.size[1]) // 2
        canvas.paste(image, (x, y))
        
        print(f"🔄 Resized to: {canvas.size}")
        
        # Save resized image
        output_buffer = io.BytesIO()
        canvas.save(output_buffer, format='JPEG', quality=90)
        output_buffer.seek(0)
        
        # Upload resized image
        filename = os.path.splitext(os.path.basename(key))[0]
        resized_key = f"processed/{filename}_256x256.jpg"
        
        s3_client.put_object(
            Bucket=bucket,
            Key=resized_key,
            Body=output_buffer.getvalue(),
            ContentType='image/jpeg',
            Metadata={
                'original_key': key,
                'size': '256x256',
                'processed_at': datetime.utcnow().isoformat()
            }
        )
        
        print(f"📤 Uploaded resized image: {resized_key}")
        
        # Queue rotation tasks
        queue_rotations(bucket, resized_key, context)
        
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
