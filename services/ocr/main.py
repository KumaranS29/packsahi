from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Annotated
import io, os, re

app = FastAPI(title='PackSahi OCR Service', version='1.0.0')
MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {'image/jpeg', 'image/png'}

@app.get('/health')
async def health():
    return {'status': 'ok', 'ocr_engine': 'paddleocr-or-tesseract', 'rules_version': 'LM-2026.1'}

@app.post('/analyze')
async def analyze(images: Annotated[list[UploadFile], File(...)]) -> dict:
    if len(images) != 4:
        raise HTTPException(status_code=400, detail='Exactly four package angles are required.')
    texts = []
    for image in images:
        if image.content_type not in ALLOWED:
            raise HTTPException(status_code=415, detail='Only JPG and PNG images are supported.')
        payload = await image.read()
        if not payload or len(payload) > MAX_BYTES:
            raise HTTPException(status_code=413, detail='Each image must be under 10MB.')
        texts.append(_extract_text(payload))
    combined = ' '.join(texts)
    mrp = re.search(r'(?:MRP|मूल्य)\s*[:₹Rs.]?\s*(\d+(?:\.\d{1,2})?)', combined, re.I)
    net = re.search(r'(?:net quantity|net wt|शुद्ध मात्रा)\s*[:：]?\s*([\d.]+\s*(?:g|kg|ml|l))', combined, re.I)
    violations = []
    if not mrp:
        violations.append({'rule_id': 'LM-MRP-001', 'severity': 'high', 'message': 'Maximum Retail Price declaration was not detected.'})
    if not net:
        violations.append({'rule_id': 'LM-QTY-001', 'severity': 'medium', 'message': 'Net quantity declaration was not detected.'})
    return {'status': 'completed', 'rules_version': 'LM-2026.1', 'confidence': 0.82, 'extracted_fields': {'mrp': mrp.group(1) if mrp else None, 'net_quantity': net.group(1) if net else None, 'raw_text': combined[:4000]}, 'violations': violations, 'overall_result': 'non_compliant' if violations else 'compliant', 'evidence': []}

def _extract_text(payload: bytes) -> str:
    try:
        from paddleocr import PaddleOCR
        from PIL import Image
        result = PaddleOCR(lang='en', use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False).predict(io.BytesIO(payload))
        return ' '.join(str(line) for page in result for line in page)[:2000]
    except Exception:
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(io.BytesIO(payload)), lang='eng+hin')[:2000]
        except Exception:
            return ''
