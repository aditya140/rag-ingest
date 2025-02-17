# Document Processing Pipeline

A scalable document processing pipeline built with Python, Temporal, and OpenAI for processing, chunking, and embedding documents. The system processes documents in parallel, generating thumbnails, extracting text, and creating embeddings for efficient search and retrieval.

## Architecture

### Components

1. **Workflow Orchestrator**
   - Manages the overall document processing flow
   - Handles retries and error recovery
   - Coordinates parallel processing activities

2. **Specialized Workers**
   - Thumbnail Generator: Creates thumbnails for document pages
   - Page Parser: Extracts text from document pages
   - Text Chunker: Splits text into semantic chunks
   - Embedding Generator: Creates embeddings using OpenAI

### Process Flow

1. Document intake starts the workflow
2. Thumbnails are generated for all pages
3. Pages are parsed in parallel
4. Extracted text is chunked
5. Chunks are embedded in parallel batches
6. Results are indexed for search

## Local Setup (macOS)

### Prerequisites

```bash
# Install Python 3.11+ if not already installed
brew install python@3.11

# Install system dependencies
brew install poppler  # For PDF processing
brew install tesseract  # For OCR
```

### Project Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-ingest
```

2. **Set up Python virtual environment**
```bash
uv venv --python=3.12
source .venv/bin/activate
```

3. **Install dependencies**
```bash
uv pip install -r requirements.txt
uv pip install pip
python -m spacy download en_core_web_sm
```

4. **Environment Configuration**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configurations:
# - OpenAI API key
# - Temporal server details
# - Vector DB credentials
```

5. **Create required directories**
```bash
mkdir -p assets/thumbnails
mkdir -p storage
```

6. **Setup Temporal**
```bash
brew install temporal
```

### Running Locally

1. **Start Temporal server**
```bash
temporal server start-dev
```

2. **Run  Server**
```bash
uvicorn app.main:app --reload
```

3. **Run development workers**
```bash
# Start all workers in development mode
./dev_workers.sh

# To stop workers
./stop_workers.sh
```

## Deployment

### Docker Deployment

1. **Build images**
```bash
# Build base image
docker build -f docker/base.Dockerfile -t rag-ingest-base:latest .

# Build worker images
docker-compose build
```

2. **Deploy with Docker Compose**
```bash
docker-compose up -d
```

3. **Scale workers as needed**
```bash
# Scale up parsing workers
docker-compose up -d --scale parsing=5

# Scale up embedding workers
docker-compose up -d --scale embedding=4
```

### Kubernetes Deployment

1. **Apply Kubernetes manifests**
```bash
kubectl apply -f k8s/
```

2. **Scale deployments**
```bash
kubectl scale deployment thumbnail-worker --replicas=3
kubectl scale deployment parsing-worker --replicas=5
kubectl scale deployment embedding-worker --replicas=4
```

## Worker Types and Scaling

### Thumbnail Worker
- Generates page thumbnails
- CPU and memory intensive
- Default: 2 replicas
- Resource limits: 1 CPU, 1GB RAM

### Parsing Worker
- Extracts text from pages
- CPU intensive
- Default: 3 replicas
- Resource limits: 1 CPU, 1GB RAM

### Chunking Worker
- Splits text into semantic chunks
- CPU light
- Default: 2 replicas
- Resource limits: 0.5 CPU, 512MB RAM

### Embedding Worker
- Generates embeddings via OpenAI
- Network and API intensive
- Default: 3 replicas
- Resource limits: 1 CPU, 1GB RAM

## Monitoring and Logs

### Local Development
```bash
# View all worker logs
tail -f logs/*.log

# View specific worker logs
tail -f logs/thumbnail.log
tail -f logs/parsing.log
```

### Docker Deployment
```bash
# View logs for specific workers
docker-compose logs -f thumbnail
docker-compose logs -f parsing

# View all logs
docker-compose logs -f
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `TEMPORAL_HOST`: Temporal server address
- `VECTOR_DB_HOST`: Vector database host
- `VECTOR_DB_PORT`: Vector database port

### Worker Configuration

Each worker type can be configured in `docker-compose.yml`:
- Number of replicas
- Resource limits
- Concurrency settings
- Queue sizes

## Development

### Adding New Worker Types

1. Create activity in `app/workers/parallel_activities.py`
2. Add worker configuration in `app/workers/tasks.py`
3. Update workflow in `app/workers/parallel_workflows.py`
4. Create Docker configuration in `docker/`

### Testing

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_processing.py
```

## Troubleshooting

### Common Issues

1. **Worker Connection Issues**
   - Check Temporal server is running
   - Verify network connectivity
   - Check task queue names match

2. **Processing Errors**
   - Check file permissions
   - Verify input file formats
   - Check system dependencies

3. **Resource Issues**
   - Monitor CPU/memory usage
   - Adjust worker resource limits
   - Scale workers as needed

### Getting Help

- Check worker logs for detailed error messages
- Review Temporal UI for workflow status
- Consult documentation for specific components
