from fastapi import APIRouter, Body
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.search import SearchService

router = APIRouter()
search_service = SearchService()

class SearchConfig(BaseModel):
    query: str = Field(..., description="Search query text")
    required_keywords: Optional[List[str]] = Field(
        default=None,
        description="List of keywords that must be present in results"
    )
    similarity_threshold: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold (0-1)"
    )
    hybrid_alpha: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Weight between vector (1.0) and keyword search (0.0)"
    )
    limit: Optional[int] = Field(
        default=5,
        gt=0,
        le=20,
        description="Maximum number of results to return"
    )

@router.post("/")
async def search(config: SearchConfig = Body(...)):
    try:
        results = search_service.hybrid_search(
            query=config.query,
            required_keywords=config.required_keywords,
            similarity_threshold=config.similarity_threshold,
            hybrid_alpha=config.hybrid_alpha,
            limit=config.limit
        )
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}, 500 