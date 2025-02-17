from typing import List, Dict, Any
import time
from pinecone import Pinecone, ServerlessSpec
from app.config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

class IndexingService:
    def __init__(self):
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self._ensure_index_exists()
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists and is ready"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            logger.info(f"Found existing indexes: {existing_indexes.names()}")
            
            if PINECONE_INDEX_NAME not in existing_indexes.names():
                logger.info(f"Creating index {PINECONE_INDEX_NAME} in {PINECONE_CLOUD}/{PINECONE_ENVIRONMENT}")
                
                # Create serverless spec
                spec = ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_ENVIRONMENT
                )
                
                # Create the index
                self.pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=384,  # BGE-small dimension
                    metric='cosine',
                    spec=spec
                )
                
                # Wait for index to be ready
                max_wait = 60  # Maximum wait time in seconds
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    try:
                        desc = self.pc.describe_index(PINECONE_INDEX_NAME)
                        status = desc.status
                        
                        if status and status.get('ready'):
                            logger.info(f"Index {PINECONE_INDEX_NAME} is ready")
                            break
                            
                        logger.info(f"Waiting for index to be ready. Status: {status}")
                    except Exception as e:
                        logger.warning(f"Error checking index status: {str(e)}")
                    
                    time.sleep(5)
                else:
                    raise TimeoutError(f"Index did not become ready within {max_wait} seconds")
            
            # Initialize index connection
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
            logger.info(f"Successfully connected to index {PINECONE_INDEX_NAME}")
            
        except Exception as e:
            logger.error(f"Error ensuring index exists: {str(e)}")
            raise
    
    def index_document(self, 
                      doc_id: str, 
                      chunks: List[str], 
                      embeddings: List[List[float]], 
                      metadata: Dict[str, Any]):
        """
        Index document chunks in Pinecone
        
        Args:
            doc_id (str): Unique document identifier
            chunks (List[str]): List of text chunks
            embeddings (List[List[float]]): List of embedding vectors
            metadata (Dict[str, Any]): Document metadata
        """
        try:
            if not chunks or not embeddings:
                raise ValueError("No chunks or embeddings provided")
                
            if len(chunks) != len(embeddings):
                raise ValueError(f"Number of chunks ({len(chunks)}) does not match number of embeddings ({len(embeddings)})")
            
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{doc_id}_{i}"
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "doc_id": doc_id,
                        "chunk_id": i,
                        **metadata
                    }
                })
            
            # Upsert vectors in batches of 100
            batch_size = 100
            total_batches = (len(vectors) + batch_size - 1) // batch_size
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                try:
                    self.index.upsert(vectors=batch)
                    logger.info(f"Indexed batch {i//batch_size + 1}/{total_batches} for document {doc_id}")
                except Exception as e:
                    logger.error(f"Error indexing batch {i//batch_size + 1}/{total_batches} for document {doc_id}: {str(e)}")
                    raise
            
            logger.info(f"Successfully indexed document {doc_id} with {len(vectors)} vectors")
            
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {str(e)}")
            raise 