import asyncio
from app.workers.tasks import run_embedding_worker
from app.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting chunk embedding worker")
    asyncio.run(run_embedding_worker()) 