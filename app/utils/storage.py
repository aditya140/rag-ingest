import os
import shutil
from fastapi import UploadFile
from app.config import STORAGE_PATH
from app.utils.logger import get_logger
import boto3
from botocore.exceptions import ClientError

logger = get_logger()

# Create storage directory if it doesn't exist
os.makedirs(STORAGE_PATH, exist_ok=True)

def save_file(file: UploadFile) -> str:
    """
    Save uploaded file to local storage
    
    Args:
        file (UploadFile): Uploaded file
        
    Returns:
        str: Path where file was saved
    """
    try:
        file_path = os.path.join(STORAGE_PATH, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved successfully: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise

class StorageService:
    def __init__(self):
        self.local_storage_path = STORAGE_PATH
        self.s3_client = boto3.client('s3')
    
    def upload_to_s3(self, local_path: str, s3_key: str, bucket: str) -> bool:
        """
        Upload file to S3
        
        Args:
            local_path (str): Local file path
            s3_key (str): S3 object key
            bucket (str): S3 bucket name
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            self.s3_client.upload_file(local_path, bucket, s3_key)
            logger.info(f"File uploaded to S3: s3://{bucket}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return False
    
    def get_from_s3(self, s3_key: str, bucket: str, local_path: str) -> bool:
        """
        Download file from S3
        
        Args:
            s3_key (str): S3 object key
            bucket (str): S3 bucket name
            local_path (str): Local path to save file
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            self.s3_client.download_file(bucket, s3_key, local_path)
            logger.info(f"File downloaded from S3: {local_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return False 