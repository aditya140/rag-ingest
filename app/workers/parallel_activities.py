from typing import Dict, Any, List
import os
from PIL import Image
import pdfplumber
from temporalio import activity
from app.services.chunking import split_into_chunks
from app.services.embeddings import EmbeddingService
from app.services.indexing import IndexingService
from app.utils.logger import get_logger

logger = get_logger(__name__)
embedding_service = EmbeddingService()
indexing_service = IndexingService()

@activity.defn
async def generate_thumbnails_activity(file_path: str) -> Dict[str, Any]:
    """Generate thumbnails for each page of a document."""
    try:
        info = activity.info()
        workflow_id = info.workflow_id
        logger.info(f"[{workflow_id}] Generating thumbnails for {file_path}")
        
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = os.path.join("assets", "thumbnails", workflow_id)
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        thumbnail_paths = []
        page_count = 0
        
        if file_path.lower().endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    # Convert page to image with specific resolution
                    img = page.to_image(resolution=72)
                    # Generate thumbnail path
                    thumb_path = os.path.join(thumbnails_dir, f"page_{i+1}.png")
                    # Save thumbnail (pdfplumber's to_image already handles DPI)
                    img.save(thumb_path, format="PNG")
                    thumbnail_paths.append(thumb_path)
                    logger.info(f"[{workflow_id}] Generated thumbnail for page {i+1}")
        else:
            # Handle image files
            with Image.open(file_path) as img:
                page_count = 1
                thumb_path = os.path.join(thumbnails_dir, "page_1.png")
                
                # Calculate thumbnail size while maintaining aspect ratio
                max_size = (300, 300)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # For regular images, we can set DPI directly
                img.save(thumb_path, format="PNG", dpi=(72, 72))
                thumbnail_paths.append(thumb_path)
                logger.info(f"[{workflow_id}] Generated thumbnail for image")
        
        logger.info(f"[{workflow_id}] Successfully generated {len(thumbnail_paths)} thumbnails")
        return {
            "status": "success",
            "page_count": page_count,
            "thumbnail_paths": thumbnail_paths
        }
        
    except Exception as e:
        logger.error(f"Error generating thumbnails: {str(e)}")
        raise

@activity.defn
async def parse_page_activity(file_path: str, page_num: int) -> Dict[str, Any]:
    """Parse a single page from a document."""
    try:
        info = activity.info()
        workflow_id = info.workflow_id
        logger.info(f"[{workflow_id}] Parsing page {page_num} from {file_path}")
        
        if file_path.lower().endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    if text:
                        return {
                            "status": "success",
                            "page_num": page_num,
                            "text": text
                        }
        
        return {
            "status": "error",
            "page_num": page_num,
            "error": "No text extracted or invalid page number"
        }
        
    except Exception as e:
        logger.error(f"Error parsing page {page_num}: {str(e)}")
        raise

@activity.defn
async def chunk_text_activity(texts: List[str], doc_id: str) -> Dict[str, Any]:
    """Split texts into chunks for processing."""
    try:
        info = activity.info()
        workflow_id = info.workflow_id
        logger.info(f"[{workflow_id}] Chunking text for document {doc_id}")
        
        # Combine texts with page breaks
        combined_text = "\n\n".join(texts)
        
        # Split into chunks
        chunks = split_into_chunks(combined_text, chunk_size=1000, overlap=200)
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Error chunking text: {str(e)}")
        raise

@activity.defn
async def embed_chunks_activity(chunks: List[str], doc_id: str) -> Dict[str, Any]:
    """Generate embeddings for a batch of chunks and index them."""
    try:
        info = activity.info()
        workflow_id = info.workflow_id
        logger.info(f"[{workflow_id}] Embedding {len(chunks)} chunks for document {doc_id}")
        
        # Generate embeddings
        embeddings = embedding_service.generate_embeddings(chunks)
        
        # Prepare chunks with embeddings for indexing
        embedded_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            embedded_chunks.append({
                "chunk_id": f"{doc_id}_{i}",
                "text": chunk,
                "embedding": embedding,
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_index": i
                }
            })
        
        # Index the chunks
        indexing_service.index_document(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata={"doc_id": doc_id}
        )
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "embedded_chunks": embedded_chunks
        }
        
    except Exception as e:
        logger.error(f"Error embedding chunks: {str(e)}")
        raise 