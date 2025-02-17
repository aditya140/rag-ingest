import asyncio
from app.workers.tasks import run_chunking_worker
from app.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting text chunking worker")
    asyncio.run(run_chunking_worker()) 