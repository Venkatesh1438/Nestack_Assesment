from fastapi import FastAPI
from routes import extract

app = FastAPI(
    title="Structured Data Extractor API",
    description="API to extract structured fields from raw text using Gemini",
    version="1.0.0"
)

# Include the extraction router
app.include_router(extract.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)