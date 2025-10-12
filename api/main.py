from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from . import services, models, database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_db_and_tables()
    yield

app = FastAPI(
    title="Smart Resume Screener API",
    description="An API to parse resumes and match them with job descriptions using AI.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Smart Resume Screener API!"}

# Note: The /parse-resume/ endpoint is no longer needed but can be kept for debugging if desired.

@app.post("/screen/", response_model=models.CombinedScreeningResult) # Updated response_model
async def screen_resume_endpoint(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    The main endpoint to efficiently screen a resume against a job description
    in a single AI call.
    """
    if resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Step 1: Extract text from the PDF
        resume_text = services.extract_text_from_pdf(resume_file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        # Step 2: Perform combined parsing and matching in a single call
        combined_result = services.perform_combined_screening_with_llm(resume_text, job_description)
        
        # Step 3: Return the result
        return combined_result

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")