from config import REVIEW_THRESHOLD

def format_extraction_response(llm_data: dict) -> dict:
    """
    Takes the raw JSON from the LLM, applies the confidence threshold logic,
    and ensures all required fields are present to prevent crashes.
    """
    expected_fields = [
        "vendor_name", "amount", "currency", 
        "date", "category", "description", "invoice_id"
    ]
    
    processed_fields = {}
    review_required = False
    
    for field in expected_fields:
        # Get field data from LLM, or fallback if it hallucinates/misses a key
        field_data = llm_data.get(field, {})
        
        value = field_data.get("value", None)
        
        # Default confidence is very low if something goes wrong
        try:
            confidence = float(field_data.get("confidence", 0.1))
        except (ValueError, TypeError):
            confidence = 0.1
            
        # Apply the review logic
        needs_review = confidence < REVIEW_THRESHOLD
        
        if needs_review:
            review_required = True
            
        processed_fields[field] = {
            "value": value,
            "confidence": confidence,
            "needs_review": needs_review
        }
        
    return {
        "review_required": review_required,
        "fields": processed_fields
    }

    # Default low confidence if model output is invalid or missing