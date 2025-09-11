import json
import boto3
import os
from datetime import datetime
from PIL import Image
import io

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
                # Debug: Print the raw record
                print(f"🔍 Raw SQS record: {record}")
                
                # Parse SQS message
                message_body = record['body']
                print(f"🔍 Message body: {message_body}")
                print(f"🔍 Message body type: {type(message_body)}")
                
                message = json.loads(message_body)
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
                    
            except json.JSONDecodeError as e:
                error_msg = f"JSON decode error: {str(e)} - Raw body: {record.get('body', 'No body')}"
                print(f"💥 {error_msg}")
                errors.append(error_msg)
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
    Actually rotate image using PIL and upload to S3
    """
    try:
        # Download the original image from S3
        print(f"📥 Downloading image: {image_key}")
        response = s3_client.get_object(Bucket=bucket, Key=image_key)
        image_data = response['Body'].read()
        
        # Open image with PIL
        with Image.open(io.BytesIO(image_data)) as img:
            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Rotate the image
            if angle == 360:
                rotated_img = img  # No rotation for 360 (original)
                rotation_desc = "original"
            else:
                # Rotate counter-clockwise (PIL default)
                rotated_img = img.rotate(angle, expand=True)
                rotation_desc = f"rotated_{angle}"
            
            # Generate output path
            filename = os.path.splitext(os.path.basename(image_key))[0]
            extension = os.path.splitext(image_key)[1] or '.jpg'
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            output_key = f"augmented-images/{angle}-degree/{filename}_{rotation_desc}_{timestamp}{extension}"
            
            # Save rotated image to bytes buffer
            img_buffer = io.BytesIO()
            
            # Determine format from extension
            format_map = {
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG', 
                '.png': 'PNG',
                '.bmp': 'BMP',
                '.tiff': 'TIFF'
            }
            img_format = format_map.get(extension.lower(), 'JPEG')
            
            # Save with appropriate quality
            if img_format == 'JPEG':
                rotated_img.save(img_buffer, format=img_format, quality=95, optimize=True)
            else:
                rotated_img.save(img_buffer, format=img_format)
            
            img_buffer.seek(0)
            
            # Upload rotated image to S3
            s3_client.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=img_buffer.getvalue(),
                ContentType=f'image/{img_format.lower()}',
                Metadata={
                    'original_key': image_key,
                    'angle': str(angle),
                    'task_id': task_id,
                    'created_at': timestamp,
                    'note': f'Rotated {angle} degrees using PIL'
                }
            )
            
            print(f"📤 Uploaded rotated image to: {output_key}")
            return True
        
    except Exception as e:
        print(f"💥 Error creating {angle}° rotation: {str(e)}")
        return False
