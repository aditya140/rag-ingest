from fastapi import APIRouter, UploadFile, File
from app.services.parser import parse_document
from app.utils.storage import save_file
from app.workers.tasks import start_parsing_task

router = APIRouter()

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = save_file(file)
        await start_parsing_task(file_path)
        return {"message": "File uploaded successfully", "file_path": file_path}
    except Exception as e:
        return {"error": str(e)}, 500 