from fastapi import APIRouter
from pydantic import BaseModel
from services.gemini_service import call_llm_for_extraction
from utils.helpers import format_extraction_response

router = APIRouter()

# Request model
class ExtractRequest(BaseModel):
    text: str
    
    class Config:
        max_anystr_length = 50000  # Reasonable limit to prevent abuse

@router.post("/extract")
async def extract_data(request: ExtractRequest):
    # 1. Handle empty input without calling the LLM
    if not request.text or not request.text.strip():
        return format_extraction_response({})
    
    # 2. Send the text to Gemini
    raw_llm_data = call_llm_for_extraction(request.text)
    
    # 3. Process the results, check confidence, and apply the schema
    final_response = format_extraction_response(raw_llm_data)
    
    return final_response