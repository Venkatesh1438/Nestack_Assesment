import json
import google.generativeai as genai
from config import GEMINI_API_KEY
import os

# Load environment variables explicitly (already done in config.py, but being explicit here too)
from dotenv import load_dotenv
load_dotenv()

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"✓ Gemini API configured successfully. Key length: {len(GEMINI_API_KEY)}")
else:
    print("✗ ERROR: GEMINI_API_KEY is not set in .env file! Extraction will fail.")

# Using flash as it is fast and cheap, perfect for this kind of extraction
model = genai.GenerativeModel('gemini-1.5-flash')

def get_prompt() -> str:
    """Reads the prompt template from the file system."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", "extraction_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def call_llm_for_extraction(text: str) -> dict:
    """Calls Gemini to extract data. Returns a raw dict."""
    
    # Validate input
    if not text or not text.strip():
        print("⚠ Empty input text provided to LLM")
        return {}
    
    print(f"\n[DEBUG] Starting extraction for text: {text[:100]}...")
    
    try:
        # Get the prompt template
        prompt_template = get_prompt()
        prompt = prompt_template.replace("{{TEXT}}", text)
        print(f"[DEBUG] Prompt prepared (length: {len(prompt)})")
        
        # Call Gemini with JSON mode
        print("[DEBUG] Calling Gemini API...")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        print(f"[DEBUG] Gemini response received")
        print(f"[DEBUG] Response text: {response.text[:500]}")
        
        # Parse the JSON response
        # Sometimes the model wraps JSON in markdown code blocks, so clean it up
        response_text = response.text.strip()
        
        # Remove markdown code block markers if present
        if response_text.startswith("```"):
            # Extract JSON from markdown code block
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]  # Remove "json" prefix
            response_text = response_text.strip()
            print("[DEBUG] Cleaned markdown wrapper from response")
        
        # Parse JSON
        data = json.loads(response_text)
        print(f"[DEBUG] Successfully parsed JSON. Fields: {list(data.keys())}")
        
        # Validate: ensure we got a dict with expected fields
        if not isinstance(data, dict):
            print(f"✗ ERROR: Response is not a dict, got {type(data)}")
            return {}
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON Parse Error: {e}")
        print(f"  Response was: {response.text if 'response' in locals() else 'No response'}")
        return {}
    
    except Exception as e:
        print(f"✗ LLM Extraction Failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}