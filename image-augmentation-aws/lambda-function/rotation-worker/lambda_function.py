import json
import boto3
from PIL import Image
import io
import os
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Process rotation tasks from SQS
    Creates rotated versions of images
    """
    
    print(f"🔄 Rotation worker started at {datetime.utcnow()}")
    
    processed = 0
    errors = []
    
    try:
        for record in event['Records']:
            try:
                # Parse SQS message
                message = json.loads(record['body'])
                task_id = message['task_id']
                bucket = message['bucket']
                image_key = message['image_key']
                angle = message['angle']
                
                print(f"🎯 Processing task {task_id}: {angle}° rotation for {image_key}")
                
                # Process the rotation
                success = create_rotation(bucket, image_key, angle, task_id)
                
                if success:
                    processed += 1
                    print(f"✅ Completed {angle}° rotation")
                else:
                    errors.append(f"Failed {angle}° rotation for {image_key}")
                    
            except Exception as e:
                error_msg = f"Error processing record: {str(e)}"
                print(f"💥 {error_msg}")
                errors.append(error_msg)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed,
                'total': len(event['Records']),
                'errors': errors
            })
        }
        
    except Exception as e:
        print(f"💥 Critical error in rotation worker: {str(e)}")
        raise e

def create_rotation(bucket, image_key, angle, task_id):
    """
    Download image, rotate it, and save to S3
    """
    try:
        # Download image
        print(f"⬇️ Downloading: {image_key}")
        response = s3_client.get_object(Bucket=bucket, Key=image_key)
        image_data = response['Body'].read()
        
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Create rotation
        if angle == 360:
            rotated = image.copy()  # Original
            rotation_desc = "original"
        else:
            rotated = image.rotate(-angle, expand=True, fillcolor='white')
            rotation_desc = f"rotated_{angle}"
        
        print(f"🔄 Applied {angle}° rotation")
        
        # Save to bytes
        output_buffer = io.BytesIO()
        rotated.save(output_buffer, format='JPEG', quality=90)
        output_buffer.seek(0)
        
        # Generate output path
        filename = os.path.splitext(os.path.basename(image_key))[0]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_key = f"augmented-images/{angle}-degree/{filename}_{rotation_desc}_{timestamp}.jpg"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=output_buffer.getvalue(),
            ContentType='image/jpeg',
            Metadata={
                'original_key': image_key,
                'angle': str(angle),
                'task_id': task_id,
                'created_at': timestamp
            }
        )
        
        print(f"📤 Saved: {output_key}")
        return True
        
    except Exception as e:
        print(f"💥 Error creating {angle}° rotation: {str(e)}")
        return False
