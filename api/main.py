from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from . import services, models, database
from .database import SessionLocal
from . import crud
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

@app.post("/screen/", response_model=models.CombinedScreeningResult)
async def screen_resume_endpoint(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Screens a resume and saves the result to the database talent pool.
    """
    if resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type.")

    db = SessionLocal()
    try:
        resume_text = services.extract_text_from_pdf(resume_file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text.")

        combined_result = services.perform_combined_screening_with_llm(resume_text, job_description)
        
        # --- This is the new logic to save the results ---
        crud.save_screening_result(
            db=db, 
            result=combined_result, 
            job_description=job_description
        )

        return combined_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always close the database session
        db.close()
        
@app.post("/search-talent-pool/")
async def search_talent_pool_endpoint(
    job_description: str = Form(...),
    score_threshold: int = Form(...)
):
    """
    Searches the existing talent pool for candidates matching a new job description.
    """
    db = SessionLocal()
    try:
        all_candidates = crud.get_all_candidates(db)
        if not all_candidates:
            return []

        matching_candidates = []
        for candidate in all_candidates:
            # Re-score the candidate's stored resume against the NEW job description
            # We use the raw resume data, not the parsed JSON, for a fresh analysis
            # Assuming `parsed_resume_data` contains the full text or can be derived.
            # For simplicity, let's assume we need to re-parse. A more optimized
            # system might store raw text separately.
            
            # This is a simplified approach. A fully optimized version would require
            # storing the raw resume text in the DB to avoid re-parsing from JSON.
            # For this project, we'll re-run the full analysis.
            
            # Let's call the same service, assuming it can handle the JSON resume data
            # To do this properly, we need to adapt our service function slightly.
            # For now, let's just simulate the re-scoring.
            
            # A proper implementation requires a dedicated re-scoring logic.
            # Let's build a simplified version for this project.
            
            # Let's assume a simplified re-scoring for now.
            # We will use the existing `perform_combined_screening_with_llm`
            # and extract the parsed resume text from the stored JSON.
            # Note: This is computationally intensive.
            import json
            parsed_data = json.loads(candidate.parsed_resume_data)
            # Re-create a text representation for the LLM
            resume_text_for_rescore = f"Name: {parsed_data.get('full_name')}\nSkills: {', '.join(parsed_data.get('skills', []))}"

            rescore_result = services.perform_combined_screening_with_llm(resume_text_for_rescore, job_description)

            new_score = rescore_result.match_data.match_score
            
            if new_score >= score_threshold:
                matching_candidates.append({
                    "full_name": candidate.full_name,
                    "email": candidate.email,
                    "new_match_score": new_score,
                    "summary": rescore_result.match_data.summary
                })
        
        # Sort the final list by the new score
        sorted_matches = sorted(matching_candidates, key=lambda x: x['new_match_score'], reverse=True)
        return sorted_matches

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()