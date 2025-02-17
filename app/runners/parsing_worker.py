import asyncio
from app.workers.tasks import run_parsing_worker
from app.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting page parsing worker")
    asyncio.run(run_parsing_worker()) 