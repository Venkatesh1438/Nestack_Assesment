import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# We'll need this for the Gemini service
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Print warning if API key is not set
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set in .env file. The API will not work properly.")

# Threshold for flagging fields for human review
REVIEW_THRESHOLD = 0.75