FROM rag-ingest-base:latest

# Install additional dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set the worker type
ENV WORKER_TYPE=parsing

# Run the parsing worker
CMD ["python", "-m", "app.runners.parsing_worker"] 