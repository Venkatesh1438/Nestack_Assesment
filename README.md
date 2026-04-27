# Structured Data Extractor API

A simple and robust backend API built with FastAPI that extracts structured transaction data from unstructured text (emails, receipts, chat messages) using Google's Gemini LLM.

## Project Overview

This API takes raw text, sends it to Gemini for extraction, and returns structured JSON. It determines confidence scores for each extracted field. If the model is uncertain (confidence < 0.75), the field is flagged for manual human review.

### Why Gemini?

I chose `google-generativeai` with the `gemini-1.5-flash` model. It is incredibly fast, cost-effective, and natively supports strict JSON output using `response_mime_type="application/json"`.

### How Confidence Scoring Works

The prompt specifically instructs the model to return two things for every single field: a `value` and a `confidence` score (0.0 to 1.0).

- Clean, obvious data (like an exact date or exact invoice number) gets a high score like `0.99`.
- Vague data (like "last Tuesday") gets a lower score.
- If the model can't find the data at all, it returns `null` with a low score like `0.1`.

The helper function (`utils/helpers.py`) then scans these scores. Any score below `0.75` sets `needs_review: true`, which also flips the global `review_required` flag.

## Challenges Faced

- Handling cases where the input had no transaction data was tricky.
- Sometimes Gemini returned slightly inconsistent JSON, so I added fallback handling.
- Confidence scoring needed tuning to make sure ambiguous inputs are flagged correctly.

## Required Fields

The API always returns these 7 fields:

1. **vendor_name** - The name of the vendor/merchant
2. **amount** - The transaction amount
3. **currency** - Currency code (e.g., INR, USD)
4. **date** - Transaction date (YYYY-MM-DD format)
5. **category** - Type of expense (food | travel | utilities | software | other)
6. **description** - Details about the transaction
7. **invoice_id** - Invoice or reference number

Each field has:

- `value` - The extracted value (or null if missing)
- `confidence` - Confidence score (0.0 to 1.0)
- `needs_review` - True if confidence < 0.75

## Setup & Installation

### Prerequisites

- Python 3.8+
- pip

### Step 1: Clone and Setup

```bash
cd Assesment
python -m venv venv
```

On **Windows**:

```bash
venv\Scripts\activate
```

On **macOS/Linux**:

```bash
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key

Create a `.env` file in the project root with your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

Get your free API key from: https://aistudio.google.com/app/apikey

### Step 4: Run the API

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

## API Usage

### Endpoint: POST /extract

**Request:**

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Paid ₹1250 to AWS India on 12 March 2024. Invoice #INV-2024-0312."}'
```

**Python Example:**

```python
import requests

response = requests.post(
    "http://localhost:8000/extract",
    json={"text": "Paid ₹1250 to AWS India on 12 March 2024. Invoice #INV-2024-0312."}
)

print(response.json())
```

**Response:**

```json
{
  "review_required": false,
  "fields": {
    "vendor_name": {
      "value": "AWS India",
      "confidence": 0.98,
      "needs_review": false
    },
    "amount": {
      "value": 1250,
      "confidence": 0.99,
      "needs_review": false
    },
    "currency": {
      "value": "INR",
      "confidence": 0.95,
      "needs_review": false
    },
    "date": {
      "value": "2024-03-12",
      "confidence": 0.99,
      "needs_review": false
    },
    "category": {
      "value": "software",
      "confidence": 0.9,
      "needs_review": false
    },
    "description": {
      "value": "cloud compute",
      "confidence": 0.85,
      "needs_review": false
    },
    "invoice_id": {
      "value": "INV-2024-0312",
      "confidence": 0.99,
      "needs_review": false
    }
  }
}
```

### Health Check

```bash
curl http://localhost:8000/
```

## Project Structure

```
Assesment/
├── main.py                 # FastAPI app definition
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── .env                   # API key (NOT committed to git)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── routes/
│   └── extract.py        # API endpoint implementation
├── services/
│   └── gemini_service.py # Gemini API integration
├── utils/
│   └── helpers.py        # Response formatting and validation
├── prompts/
│   └── extraction_prompt.txt # LLM prompt template
├── tests/
│   └── sample_inputs.json    # Test data
└── result.json           # Sample outputs for all test inputs
```

## File Descriptions

- **main.py**: Defines the FastAPI app and includes the health check endpoint
- **config.py**: Loads environment variables from `.env` and sets up configurations
- **routes/extract.py**: Handles POST /extract requests and coordinates the extraction flow
- **services/gemini_service.py**: Calls the Gemini LLM and returns raw extracted data
- **utils/helpers.py**: Formats responses, ensures all fields are present, and applies review logic
- **prompts/extraction_prompt.txt**: The LLM prompt with schema definition and examples

## Testing

Review the sample outputs in `result.json` for examples of how the API handles different inputs:

- **Input 1**: Clean receipt data → High confidence, no review needed
- **Input 2**: Email with some ambiguity → Some fields flagged for review
- **Input 3**: Chat message with vague date → Date flagged for review
- **Input 4**: Scanned receipt → High confidence overall
- **Input 5**: Non-transaction text → All fields null, all flagged for review

## Future Improvements

- Add better date parsing for phrases like "last Tuesday"
- Improve category classification with more categories
- Add structured logging for debugging LLM outputs
- Add request rate limiting
- Add authentication for production use
- Store extraction results in a database
