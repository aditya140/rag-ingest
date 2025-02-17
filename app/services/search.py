from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from app.services.embeddings import EmbeddingService
from app.utils.logger import get_logger
import time

logger = get_logger()

class SearchService:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self._init_index()
        self.embedding_service = EmbeddingService()
    
    def _init_index(self):
        """Initialize connection to Pinecone index with retries"""
        max_retries = 5
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Check if index exists
                if PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
                    logger.warning(f"Index {PINECONE_INDEX_NAME} does not exist yet")
                    time.sleep(retry_delay)
                    continue
                
                # Try to connect to the index
                desc = self.pc.describe_index(PINECONE_INDEX_NAME)
                if desc.status['ready']:
                    self.index = self.pc.Index(PINECONE_INDEX_NAME)
                    logger.info(f"Successfully connected to index {PINECONE_INDEX_NAME}")
                    return
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} to connect to index failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to connect to index after {max_retries} attempts")
    
    def _check_required_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if all required keywords are present in text."""
        text_lower = text.lower()
        return all(keyword.lower() in text_lower for keyword in keywords)
    
    def hybrid_search(
        self,
        query: str,
        required_keywords: Optional[List[str]] = None,
        similarity_threshold: float = 0.7,
        hybrid_alpha: float = 0.5,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using Pinecone's vector search with metadata filtering
        
        Args:
            query (str): Search query
            required_keywords (Optional[List[str]]): Keywords that must be present in results
            similarity_threshold (float): Minimum similarity score (0-1)
            hybrid_alpha (float): Weight between vector (1.0) and keyword search (0.0)
            limit (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results
        """
        try:
            logger.info(f"Performing hybrid search with query: {query}")
            
            # Generate query embedding for dense vector search
            query_vector = self.embedding_service.generate_query_embedding(query)
            
            # Configure search parameters
            search_params = {
                "vector": query_vector,
                "top_k": min(limit * 3, 100),  # Get more results for post-filtering, max 100
                "include_metadata": True
            }
            
            # Execute search
            results = self.index.query(**search_params)
            
            # Process and filter results
            processed_results = []
            seen_chunks = set()
            
            for match in results.matches:
                # Skip if below similarity threshold
                if match.score < similarity_threshold:
                    continue
                    
                chunk_id = f"{match.metadata['doc_id']}_{match.metadata['chunk_id']}"
                text = match.metadata['text']
                
                # Check required keywords if specified
                if required_keywords and not self._check_required_keywords(text, required_keywords):
                    continue
                
                # Add result if it's a new chunk
                if chunk_id not in seen_chunks:
                    processed_results.append({
                        "score": match.score,
                        "text": text,
                        "doc_id": match.metadata["doc_id"],
                        "chunk_id": match.metadata["chunk_id"],
                        "metadata": {
                            k: v for k, v in match.metadata.items()
                            if k not in ['text', 'doc_id', 'chunk_id']
                        }
                    })
                    seen_chunks.add(chunk_id)
                
                if len(processed_results) >= limit:
                    break
            
            logger.info(f"Found {len(processed_results)} results for query: {query}")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid search: {str(e)}")
            raise 