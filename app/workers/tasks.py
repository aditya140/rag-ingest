import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.config import TEMPORAL_HOST
from app.workers.workflows import DocumentProcessingWorkflow
from app.workers.parallel_workflows import (
    DocumentIntakeWorkflow,
    THUMBNAIL_QUEUE,
    PARSING_QUEUE,
    CHUNKING_QUEUE,
    EMBEDDING_QUEUE,
)
from app.workers.activities import process_document_activity
from app.workers.parallel_activities import (
    generate_thumbnails_activity,
    parse_page_activity,
    chunk_text_activity,
    embed_chunks_activity
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Define processing queue
PROCESSING_QUEUE = "document-processing"

async def start_parsing_task(file_path: str, use_parallel: bool = True):
    """Start a document processing workflow"""
    client = await Client.connect(TEMPORAL_HOST)
    
    if use_parallel:
        # Start the parallel workflow
        handle = await client.start_workflow(
            DocumentIntakeWorkflow.run,
            args=[file_path],
            id=f"doc-intake-{file_path}",
            task_queue=PROCESSING_QUEUE
        )
    else:
        # Start the original workflow
        handle = await client.start_workflow(
            DocumentProcessingWorkflow.run,
            args=[file_path],
            id=f"doc-processing-{file_path}",
            task_queue=PROCESSING_QUEUE
        )
    
    # Wait for result
    result = await handle.result()
    logger.info(f"Document processing completed: {result}")
    return result

async def run_processing_worker():
    """Run the main document processing worker"""
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=PROCESSING_QUEUE,
        workflows=[DocumentProcessingWorkflow, DocumentIntakeWorkflow],
        activities=[process_document_activity],
        max_concurrent_workflow_tasks=5,
        max_concurrent_activities=10,
        max_cached_workflows=5,
        debug_mode=True
    )
    logger.info(f"Starting processing worker on task queue {PROCESSING_QUEUE}")
    await worker.run()

async def run_thumbnail_worker():
    """Run the thumbnail generation worker"""
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=THUMBNAIL_QUEUE,
        activities=[generate_thumbnails_activity],
        max_concurrent_activities=5
    )
    logger.info(f"Starting thumbnail worker on task queue {THUMBNAIL_QUEUE}")
    await worker.run()

async def run_parsing_worker():
    """Run the page parsing worker"""
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=PARSING_QUEUE,
        activities=[parse_page_activity],
        max_concurrent_activities=20
    )
    logger.info(f"Starting parsing worker on task queue {PARSING_QUEUE}")
    await worker.run()

async def run_chunking_worker():
    """Run the text chunking worker"""
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=CHUNKING_QUEUE,
        activities=[chunk_text_activity],
        max_concurrent_activities=10
    )
    logger.info(f"Starting chunking worker on task queue {CHUNKING_QUEUE}")
    await worker.run()

async def run_embedding_worker():
    """Run the chunk embedding worker"""
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=EMBEDDING_QUEUE,
        activities=[embed_chunks_activity],
        max_concurrent_activities=15
    )
    logger.info(f"Starting embedding worker on task queue {EMBEDDING_QUEUE}")
    await worker.run()

async def run_all_workers():
    """Run all workers concurrently"""
    client = await Client.connect(TEMPORAL_HOST)
    
    # Create all workers
    workflow_worker = Worker(
        client,
        task_queue=PROCESSING_QUEUE,
        workflows=[DocumentProcessingWorkflow, DocumentIntakeWorkflow],
        activities=[],
        max_concurrent_workflow_tasks=5,
        max_cached_workflows=5,
        debug_mode=True
    )
    
    thumbnail_worker = Worker(
        client,
        task_queue=THUMBNAIL_QUEUE,
        activities=[generate_thumbnails_activity],
        max_concurrent_activities=5
    )
    
    parsing_worker = Worker(
        client,
        task_queue=PARSING_QUEUE,
        activities=[parse_page_activity],
        max_concurrent_activities=20
    )
    
    chunking_worker = Worker(
        client,
        task_queue=CHUNKING_QUEUE,
        activities=[chunk_text_activity],
        max_concurrent_activities=10
    )
    
    embedding_worker = Worker(
        client,
        task_queue=EMBEDDING_QUEUE,
        activities=[embed_chunks_activity],
        max_concurrent_activities=15
    )
    
    # Run all workers concurrently
    await asyncio.gather(
        workflow_worker.run(),
        thumbnail_worker.run(),
        parsing_worker.run(),
        chunking_worker.run(),
        embedding_worker.run()
    )

def start_all_workers():
    """Start all workers in the same process for development"""
    asyncio.run(run_all_workers())

if __name__ == "__main__":
    start_all_workers() 