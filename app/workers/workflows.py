from typing import Dict, Any
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from app.workers.activities import process_document_activity

TASK_QUEUE_NAME = "document-processing"

@workflow.defn
class DocumentProcessingWorkflow:
    @workflow.run
    async def run(self, file_path: str) -> Dict[str, Any]:
        workflow.logger.info(f"Starting document processing workflow for {file_path}")
        
        try:
            result = await workflow.execute_activity(
                process_document_activity,
                args=[file_path],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                    non_retryable_error_types=["ValueError"]
                ),
                task_queue=TASK_QUEUE_NAME
            )
            
            if result["status"] == "success":
                workflow.logger.info(
                    f"Document processing completed successfully. "
                    f"Doc ID: {result.get('doc_id')}, "
                    f"Chunks: {result.get('metadata', {}).get('chunk_count', 0)}"
                )
            else:
                workflow.logger.error(f"Document processing failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            workflow.logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 