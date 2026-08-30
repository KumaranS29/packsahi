from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Annotated

app = FastAPI(title="PackSahi OCR Service")

@app.post('/analyze')
async def analyze(images: Annotated[list[UploadFile], File(...)]):
    if len(images) < 4:
        raise HTTPException(status_code=400, detail='Four package angles are required.')
    # Production boundary: run PaddleOCR/Tesseract per angle, normalize fields,
    # then evaluate Legal Metrology rules before returning evidence-linked findings.
    return {
        'status': 'queued',
        'message': 'OCR pipeline boundary ready. Configure the worker with PaddleOCR and rules engine.',
        'image_count': len(images),
        'findings': [],
    }
