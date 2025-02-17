FROM rag-ingest-base:latest

# Set the worker type
ENV WORKER_TYPE=embedding

# Run the embedding worker
CMD ["python", "-m", "app.runners.embedding_worker"] 