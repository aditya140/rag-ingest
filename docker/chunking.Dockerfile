FROM rag-ingest-base:latest

# Set the worker type
ENV WORKER_TYPE=chunking

# Run the chunking worker
CMD ["python", "-m", "app.runners.chunking_worker"] 