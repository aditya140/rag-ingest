import pdfplumber
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

def extract_text_from_pdf(file_path: str) -> Optional[str]:
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        Optional[str]: Extracted text or None if extraction fails
    """
    try:
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        if not text_content:
            logger.warning(f"No text content extracted from PDF: {file_path}")
            return None
            
        return "\n\n".join(text_content)
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return None 