FROM rag-ingest-base:latest

# Install additional dependencies for image processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the worker type
ENV WORKER_TYPE=thumbnail

# Run the thumbnail worker
CMD ["python", "-m", "app.runners.thumbnail_worker"] 