from typing import List
import numpy as np
from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.utils.logger import get_logger

logger = get_logger()

class EmbeddingService:
    def __init__(self, model: str = "text-embedding-3-small"):
        """Initialize the OpenAI embedding service.
        
        Args:
            model (str): OpenAI embedding model to use
                Options: text-embedding-3-small (1536 dimensions)
                        text-embedding-3-large (3072 dimensions)
                        text-embedding-ada-002 (1536 dimensions, legacy)
        """
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url="https://api.openai.com/v1"  # Explicitly set the base URL
        )
        self.model = model
        logger.info(f"Initialized OpenAI embedding service with model: {model}")
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a list of texts using OpenAI's API.
        
        Args:
            texts (List[str]): List of text chunks to embed
            
        Returns:
            List[np.ndarray]: List of embedding vectors
        """
        try:
            # OpenAI has a rate limit, so we'll process in batches
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        Args:
            query (str): Search query text
            
        Returns:
            List[float]: Query embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[query],
                encoding_format="float"
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise 