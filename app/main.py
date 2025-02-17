from fastapi import FastAPI
from app.routes import index, search
from pinecone import Pinecone, ServerlessSpec
from app.config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD
)
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)
app = FastAPI(title="Document Ingestion Pipeline")

@app.on_event("startup")
async def init_pinecone():
    """Initialize Pinecone index if it doesn't exist."""
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        existing_indexes = pc.list_indexes()
        
        if PINECONE_INDEX_NAME not in existing_indexes.names():
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            
            # Create the index
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_ENVIRONMENT  # Using us-west-2 for serverless
                )
            )
            
            # Wait for index to be ready
            logger.info("Waiting for index to be ready...")
            time.sleep(20)  # Give it some time to initialize
            
            # Check if index is ready
            desc = pc.describe_index(PINECONE_INDEX_NAME)
            if desc.status.get('ready'):
                logger.info(f"Index {PINECONE_INDEX_NAME} is ready!")
            else:
                logger.warning(f"Index status: {desc.status}")
        else:
            logger.info(f"Using existing Pinecone index: {PINECONE_INDEX_NAME}")
            
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {str(e)}")
        raise

app.include_router(index.router, prefix="/index", tags=["Indexing"])
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/")
def root():
    return {"message": "Document Ingestion Pipeline is running!"} 