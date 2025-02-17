import uuid
from typing import Dict, Any
from app.services.parser import parse_document
from app.services.chunking import split_into_chunks
from app.services.embeddings import EmbeddingService
from app.services.indexing import IndexingService
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize services
embedding_service = EmbeddingService()
indexing_service = IndexingService()

async def process_document(file_path: str, workflow_id: str) -> Dict[str, Any]:
    """Process a document through the pipeline.
    
    Args:
        file_path (str): Path to the document
        workflow_id (str): ID of the workflow for logging
        
    Returns:
        Dict[str, Any]: Processing results
    """
    try:
        logger.info(f"[{workflow_id}] Starting document processing for file: {file_path}")
        
        # Parse document
        parse_result = await parse_document(file_path)
        text = parse_result["text"]
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        logger.info(f"[{workflow_id}] Generated document ID: {doc_id}")
        
        # Split into chunks
        logger.info(f"[{workflow_id}] Splitting document into chunks")
        chunks = split_into_chunks(text, chunk_size=1000, overlap=200)
        logger.info(f"[{workflow_id}] Created {len(chunks)} chunks")
        
        # Generate embeddings
        logger.info(f"[{workflow_id}] Generating embeddings")
        embeddings = embedding_service.generate_embeddings(chunks)
        logger.info(f"[{workflow_id}] Generated {len(embeddings)} embeddings")
        
        # Create metadata
        metadata = {
            "doc_id": doc_id,
            "file_path": file_path,
            "file_type": parse_result["file_type"],
            "file_size": parse_result["size"],
            "char_count": parse_result["char_count"],
            "chunk_count": len(chunks)
        }
        
        # Index document
        logger.info(f"[{workflow_id}] Indexing document")
        indexing_service.index_document(doc_id, chunks, embeddings, metadata)
        logger.info(f"[{workflow_id}] Successfully indexed document")
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"[{workflow_id}] Error processing document: {str(e)}")
        raise 