from typing import List
import re

def split_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks using a simple sentence-based approach.
    
    Args:
        text (str): Text to split into chunks
        chunk_size (int): Target size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Split text into sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_size = len(sentence)
        
        # If this sentence alone is bigger than chunk_size, split it
        if sentence_size > chunk_size:
            # If we have a current chunk, add it to chunks
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Split long sentence into smaller pieces
            words = sentence.split()
            current_piece = []
            current_piece_size = 0
            
            for word in words:
                word_size = len(word) + 1  # +1 for space
                if current_piece_size + word_size > chunk_size:
                    if current_piece:
                        chunks.append(" ".join(current_piece))
                        # Keep some words for overlap
                        overlap_words = current_piece[-3:]  # Keep last 3 words for context
                        current_piece = overlap_words + [word]
                        current_piece_size = sum(len(w) + 1 for w in current_piece)
                    else:
                        # If a single word is too long, just add it
                        chunks.append(word)
                        current_piece = []
                        current_piece_size = 0
                else:
                    current_piece.append(word)
                    current_piece_size += word_size
            
            if current_piece:
                chunks.append(" ".join(current_piece))
            continue
        
        # If adding this sentence would exceed chunk_size
        if current_size + sentence_size + 1 > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                # Keep last sentence for overlap
                current_chunk = current_chunk[-1:] + [sentence]
                current_size = sum(len(s) + 1 for s in current_chunk)
            else:
                chunks.append(sentence)
                current_chunk = []
                current_size = 0
        else:
            current_chunk.append(sentence)
            current_size += sentence_size + 1
    
    # Add any remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks 