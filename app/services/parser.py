import os
from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def parse_document(file_path: str) -> Dict[str, Any]:
    """Parse a document and extract text/metadata.
    
    Args:
        file_path (str): Path to the document to process
        
    Returns:
        Dict[str, Any]: Extracted text and metadata
    """
    try:
        # Get file info
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        logger.info(f"Processing {file_ext} file of size {file_size} bytes: {file_path}")
        
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Lazy import OCR module only when needed
        if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            logger.info(f"Using OCR for image file: {file_path}")
            from app.services.ocr import extract_text_from_image
            text = await extract_text_from_image(file_path)
            
        elif file_ext == '.pdf':
            logger.info(f"Processing PDF file: {file_path}")
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = '\n'.join(page.extract_text() for page in pdf.pages)
                
        elif file_ext in ['.doc', '.docx']:
            logger.info(f"Processing Word document: {file_path}")
            from docx import Document
            doc = Document(file_path)
            text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
            
        else:
            error_msg = f"Unsupported file type: {file_ext}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not text:
            error_msg = f"No text extracted from document {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Log success and text length
        logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
        
        return {
            "text": text,
            "file_type": file_ext,
            "file_path": file_path,
            "size": file_size,
            "char_count": len(text)
        }
        
    except Exception as e:
        logger.error(f"Error parsing document {file_path}: {str(e)}")
        raise 