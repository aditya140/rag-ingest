import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from pinecone import Pinecone, ServerlessSpec
from app.config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD
)
import time

def init_pinecone():
    """Initialize Pinecone index if it doesn't exist."""
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        existing_indexes = pc.list_indexes()
        
        if PINECONE_INDEX_NAME not in existing_indexes.names():
            print(f"Creating index {PINECONE_INDEX_NAME}")
            
            # Create serverless spec
            spec = ServerlessSpec(
                cloud=PINECONE_CLOUD,
                region=PINECONE_ENVIRONMENT
            )
            
            # Create the index
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI embedding dimension
                metric='cosine',
                spec=spec
            )
            
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            time.sleep(20)  # Give it some time to initialize
            
            # Check if index is ready
            desc = pc.describe_index(PINECONE_INDEX_NAME)
            if desc.status.get('ready'):
                print(f"Index {PINECONE_INDEX_NAME} is ready!")
            else:
                print(f"Index status: {desc.status}")
        else:
            print(f"Index {PINECONE_INDEX_NAME} already exists")
            
    except Exception as e:
        print(f"Error initializing Pinecone: {str(e)}")
        raise

if __name__ == "__main__":
    init_pinecone() 