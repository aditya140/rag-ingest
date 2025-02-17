from typing import Optional
import pytesseract
from PIL import Image
import cv2
import numpy as np
from app.utils.logger import get_logger

logger = get_logger(__name__)

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image for better OCR results.
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        np.ndarray: Preprocessed image
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    return gray

def extract_text_from_image(file_path: str) -> Optional[str]:
    """
    Extract text from an image using OCR.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        Optional[str]: Extracted text or None if extraction fails
    """
    try:
        # Read image using PIL
        pil_image = Image.open(file_path)
        
        # Convert to OpenCV format
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Perform OCR
        text = pytesseract.image_to_string(
            Image.fromarray(processed_image),
            lang='eng',
            config='--psm 6'  # Assume uniform block of text
        )
        
        if not text.strip():
            logger.warning(f"No text extracted from image: {file_path}")
            return None
            
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from image {file_path}: {str(e)}")
        return None 