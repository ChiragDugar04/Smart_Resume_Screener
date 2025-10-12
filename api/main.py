from fastapi import FastAPI, UploadFile, File, HTTPException
from . import services, models

app = FastAPI(
    title="Smart Resume Screener API",
    description="An API to parse resumes and match them with job descriptions using AI.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok", "message": "Welcome to the Smart Resume Screener API!"}

@app.post("/parse-resume/", response_model=models.ParsedResume)
async def parse_resume_endpoint(resume_file: UploadFile = File(...)):
    """
    Parses a resume PDF file and returns structured data.

    - **resume_file**: The PDF file of the candidate's resume.
    """
    # Check if the uploaded file is a PDF
    if resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Extract text from the PDF
        resume_text = services.extract_text_from_pdf(resume_file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

        # Parse the text using the LLM
        parsed_resume = services.parse_resume_with_llm(resume_text)
        
        return parsed_resume

    except ValueError as e:
        # Catches the specific error from our service for bad LLM responses
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # A general catch-all for other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")