import json
import boto3
import urllib.parse
from PIL import image
import io
import os
import uuid

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    """
    Main image processor function triggered by S3 upload
    - Downloads original image
    - Resizes to 256x256
    - Sends rotation tasks to SQS
    """

    try:
        # Parse S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        # Skip if already processed (avoid infinite loops)
            if key.startswith('augmented-images/'):
                print(f"Skipping already processed image: {key}")
                continue
        
            print(f"Processing new image: {key}")
            
            resized_key = resize_image(bucket, key)
            
            if resized_key:
                queue_rotation_tasks(bucket, resized_key)
                print(f"Successfully queued rotation tasks for: {resized_key}")
            
        
        return {
            statusCode: 200,
            'body': json.dumps({
                'message': 'Image processing initiated successfully',
                'processed_image': len(event['Records'])
            })
        }
        
    except Exception as e:
        print(f"Error Processing image: {e}")
        raise e
    
def resize_image(bucket, key):
    """
    Download image from S3, resize to 256x256, and re-upload
    """
    try:
        # Download original image
        print(f"Downloading image : {key}")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_content = response['Body'].read()
        
        image = Image.open(io.BytesIO(image_content))
        print(f"Original image size: {image.size}")
        
        # Resize to 256x256 maintaining aspect ratio
        image = image.convert('RGB')  # Ensure RGB mode
        image.thumbnail((256, 256), Image.Resampling.LANCZOS)
        
        # Create a 256x256 canvas and paste the resized image (center it)
        canvas = Image.new('RGB', (256, 256), (255, 255, 255))  # White background
        
        # Calculate position to center the image
        x = (256 - image.size[0]) // 2
        y = (256 - image.size[1]) // 2
        canvas.paste(image, (x, y))
        
        print(f"Resized image to: {canvas.size}")
        
        # Convert back to bytes
        output_buffer = io.BytesIO()
        canvas.save(output_buffer, format='JPEG', quality=95)
        output_buffer.seek(0)
        
        # Generate new key for resized image
        file_name = os.path.splitext(os.path.basename(key))[0]
        resized_key = f"processed/{file_name}_256x256.jpg"
        
        # Upload resized image
        s3_client.put_object(
            Bucket=bucket,
            Key=resized_key,
            Body=output_buffer.getvalue(),
            ContentType='image/jpeg',
            Metadata={
                'original_key': key,
                'processing_timestamp': str(context.aws_request_id),
                'size': '256x256'
            }
        )
        
        print(f"Uploaded resized image: {resized_key}")
        return resized_key
        
    except Exception as e:
        print(f"Error resizing image {key}: {str(e)}")
        return None
    
def queue_rotation_tasks(bucket, image_key):
    """
    Send rotation tasks to SQS queue
    """
    try:
        queue_url = os.environ['SQS_QUEUE_URL']
        angles = [90, 180, 270, 360]  # 360 represents original (no rotation)
        
        for angle in angles:
            message = {
                'task_id': str(uuid.uuid4()),
                'bucket': bucket,
                'image_key': image_key,
                'rotation_angle': angle,
                'timestamp': context.aws_request_id if 'context' in globals() else 'unknown'
            }
            
            # Send message to SQS
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                MessageAttributes={
                    'angle': {
                        'StringValue': str(angle),
                        'DataType': 'String'
                    },
                    'bucket': {
                        'StringValue': bucket,
                        'DataType': 'String'
                    }
                }
            )
            
            print(f"Queued rotation task: {angle}° - MessageId: {response['MessageId']}")
            
    except Exception as e:
        print(f"Error queuing rotation tasks: {str(e)}")
        raise e