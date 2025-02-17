FROM rag-ingest-base:latest

# Set the worker type
ENV WORKER_TYPE=workflow

# Run the workflow worker
CMD ["python", "-m", "app.runners.workflow_worker"] 