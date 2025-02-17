from typing import Dict, Any, List
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

# Define task queues
THUMBNAIL_QUEUE = "thumbnail-generation"
PARSING_QUEUE = "page-parsing"
CHUNKING_QUEUE = "text-chunking"
EMBEDDING_QUEUE = "chunk-embedding"

@workflow.defn
class DocumentIntakeWorkflow:
    @workflow.run
    async def run(self, file_path: str) -> Dict[str, Any]:
        """Main workflow that orchestrates the document processing pipeline."""
        workflow.logger.info(f"Starting document intake workflow for {file_path}")
        
        try:
            # Step 1: Generate thumbnails for all pages
            thumbnail_result = await workflow.execute_activity(
                "generate_thumbnails_activity",
                args=[file_path],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3
                ),
                task_queue=THUMBNAIL_QUEUE
            )
            
            # Step 2: Process pages in parallel
            page_count = thumbnail_result["page_count"]
            page_results = []
            
            for page_num in range(page_count):
                result = await workflow.execute_activity(
                    "parse_page_activity",
                    args=[file_path, page_num],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=5),
                        maximum_interval=timedelta(minutes=1),
                        maximum_attempts=3
                    ),
                    task_queue=PARSING_QUEUE
                )
                page_results.append(result)
            
            # Step 3: Chunk the extracted text
            texts = [result["text"] for result in page_results if result["status"] == "success"]
            doc_id = workflow.info().workflow_id
            
            chunk_results = await workflow.execute_activity(
                "chunk_text_activity",
                args=[texts, doc_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3
                ),
                task_queue=CHUNKING_QUEUE
            )
            
            # Step 4: Process chunks in parallel batches for embedding
            batch_size = 100
            chunks = chunk_results["chunks"]
            total_chunks = len(chunks)
            embedded_chunks = []
            
            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:min(i + batch_size, total_chunks)]
                result = await workflow.execute_activity(
                    "embed_chunks_activity",
                    args=[batch, doc_id],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=5),
                        maximum_interval=timedelta(minutes=1),
                        maximum_attempts=3
                    ),
                    task_queue=EMBEDDING_QUEUE
                )
                embedded_chunks.extend(result["embedded_chunks"])
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "metadata": {
                    "file_path": file_path,
                    "page_count": page_count,
                    "thumbnail_paths": thumbnail_result["thumbnail_paths"],
                    "chunk_count": len(embedded_chunks),
                    "processing_status": "completed"
                }
            }
            
        except Exception as e:
            workflow.logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 