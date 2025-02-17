from typing import Dict, Any
from temporalio import activity
from app.utils.logger import get_logger

logger = get_logger(__name__)

@activity.defn(name="process_document_activity")
async def process_document_activity(file_path: str) -> Dict[str, Any]:
    """Process a document and return the results.
    
    Args:
        file_path (str): Path to the document to process
        
    Returns:
        Dict[str, Any]: Processing results including status and any errors
    """
    # Get workflow information
    info = activity.info()
    workflow_id = info.workflow_id
    
    try:
        # Lazy import to avoid workflow sandbox issues
        from app.services.processing import process_document
        
        # Process document using the processing service
        result = await process_document(file_path, workflow_id)
        return {
            "status": "success",
            "file_path": file_path,
            **result
        }
        
    except Exception as e:
        error_msg = f"[{workflow_id}] Error processing document: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "file_path": file_path,
            "error": str(e),
            "workflow_id": workflow_id
        } 