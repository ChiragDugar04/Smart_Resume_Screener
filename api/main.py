from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from . import services, models, database  # Import database
from contextlib import asynccontextmanager

# LifeSpan event to create DB tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_db_and_tables()
    yield

app = FastAPI(
    title="Smart Resume Screener API",
    description="An API to parse resumes and match them with job descriptions using AI.",
    version="1.0.0",
    lifespan=lifespan # Add the lifespan event
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

# ... (keep other endpoints)

@app.post("/screen/", response_model=models.ScreeningResult)
async def screen_resume_endpoint(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    The main endpoint to screen a resume against a job description. It performs the following steps:
    1. Parses the resume PDF to extract structured data.
    2. Matches the parsed resume against the provided job description using an LLM.
    3. (Future Step) Saves the result to the database.
    4. Returns the combined result.
    """
    if resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Step 1: Parse the resume
        resume_text = services.extract_text_from_pdf(resume_file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        
        parsed_resume = services.parse_resume_with_llm(resume_text)
        
        # Convert parsed resume to JSON string for the next LLM call
        resume_json_str = parsed_resume.model_dump_json()

        # Step 2: Match resume to job description
        match_result = services.match_resume_to_jd_with_llm(resume_json_str, job_description)

        # Step 3: (For now, we just return. We will add DB logic next)
        # In a real app, you might save to DB here.
        # For simplicity in this step, we construct the response directly.

        # Step 4: Return the combined result
        return models.ScreeningResult(resume_data=parsed_resume, match_data=match_result)

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")