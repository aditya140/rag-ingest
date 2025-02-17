import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Storage
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
S3_BUCKET = os.getenv("S3_BUCKET", "my-bucket")

# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")  # AWS region
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "document-search")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")  # AWS cloud provider

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Temporal
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 