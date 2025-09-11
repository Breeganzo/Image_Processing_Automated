import json
import boto3
import os
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Process rotation tasks from SQS
    Creates copies of images in different folders (simulating rotation)
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
                
                # Process the rotation (copy file to rotation folder)
                success = create_rotation_copy(bucket, image_key, angle, task_id)
                
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

def create_rotation_copy(bucket, image_key, angle, task_id):
    """
    Copy image to rotation folder (simulating rotation without PIL)
    """
    try:
        # Generate output path
        filename = os.path.splitext(os.path.basename(image_key))[0]
        extension = os.path.splitext(image_key)[1] or '.jpg'
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if angle == 360:
            rotation_desc = "original"
        else:
            rotation_desc = f"rotated_{angle}"
            
        output_key = f"augmented-images/{angle}-degree/{filename}_{rotation_desc}_{timestamp}{extension}"
        
        # Copy the original image to the rotation folder
        copy_source = {'Bucket': bucket, 'Key': image_key}
        
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket,
            Key=output_key,
            Metadata={
                'original_key': image_key,
                'angle': str(angle),
                'task_id': task_id,
                'created_at': timestamp,
                'note': f'Simulated {angle}° rotation - actual rotation requires PIL library'
            },
            MetadataDirective='REPLACE'
        )
        
        print(f"📤 Copied to: {output_key}")
        return True
        
    except Exception as e:
        print(f"💥 Error creating {angle}° rotation copy: {str(e)}")
        return False
