from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PyPDF2 import PdfReader
import io
import json

# Local imports
import database
import utils

app = FastAPI(
    title="Smart Resume Screener API",
    description="An API to screen resumes against job descriptions using an LLM.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """Initialize the database when the application starts."""
    database.init_db()

@app.post("/screen/")
async def screen_resume(
    job_description: str = Form(...), 
    resume_file: UploadFile = File(...)
):
    """
    Screens a single resume against a job description.
    Accepts both PDF and plain text files.
    """
    try:
        filename = resume_file.filename
        file_contents = await resume_file.read()
        resume_text = ""

        # --- THIS IS THE CRUCIAL CHANGE ---
        # Check if the uploaded file is a PDF or a text file from the talent pool
        if resume_file.content_type == 'application/pdf':
            pdf_reader = PdfReader(io.BytesIO(file_contents))
            for page in pdf_reader.pages:
                resume_text += page.extract_text() or ""
        else: # Assumes plain text
            resume_text = file_contents.decode('utf-8')
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the file.")

        analysis_text = utils.get_gemini_response(job_description, resume_text)
        if not analysis_text:
            raise HTTPException(status_code=500, detail="Failed to get analysis from LLM.")
        
        start_index = analysis_text.find('{')
        end_index = analysis_text.rfind('}') + 1
        json_str = analysis_text[start_index:end_index]
        parsed_json = json.loads(json_str)

        # Only add to DB if it's a new PDF upload, not a re-screen
        if resume_file.content_type == 'application/pdf':
             database.add_resume(filename, resume_text, parsed_json)

        return parsed_json

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing LLM response.")
    except Exception as e:
        # It's good practice to log the actual error for debugging
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/resumes/")
async def get_resumes_from_db():
    resumes = database.get_all_resumes()
    return [{"filename": r[0], "text": r[1]} for r in resumes]