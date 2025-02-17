import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

import requests

def test_document_upload():
    """Test uploading a document to the ingestion pipeline."""
    
    # API endpoint
    upload_url = "http://localhost:8000/index/upload"
    
    # Get the path to the assets folder and the Deepseek file
    current_dir = Path(__file__).parent
    assets_dir = current_dir.parent / "assets"
    file_path = assets_dir / "DeepSeek_R1.pdf"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Test file not found at {file_path}")
    
    print(f"Uploading file: {file_path}")
    
    # Prepare the file for upload
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "application/pdf")}
        
        try:
            # Make the upload request
            response = requests.post(upload_url, files=files)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                print("Upload successful!")
                print(f"Response: {result}")
            else:
                print(f"Upload failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error during upload: {str(e)}")

if __name__ == "__main__":
    test_document_upload() 