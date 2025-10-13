from sqlalchemy.orm import Session
from . import database, models

def save_screening_result(db: Session, result: models.CombinedScreeningResult, job_description: str):
    resume_data = result.resume_data
    match_data = result.match_data
    candidate_email = resume_data.email

    # Check if a candidate with this email already exists
    db_candidate = db.query(database.Candidate).filter(database.Candidate.email == candidate_email).first()

    if not db_candidate:
        # If not, create a new candidate record
        db_candidate = database.Candidate(
            full_name=resume_data.full_name,
            email=candidate_email,
            parsed_resume_data=resume_data.model_dump_json()
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)

    # Now, create the new screening record linked to the candidate
    db_screening_record = database.ScreeningRecord(
        # A more advanced version could extract the title from the JD. For now, we'll use a placeholder.
        job_role_title="Software Development Engineer",
        match_score=match_data.match_score,
        job_description_text=job_description,
        candidate_id=db_candidate.id
    )
    db.add(db_screening_record)
    db.commit()
    db.refresh(db_screening_record)

def get_all_candidates(db: Session):
    """Retrieves all candidate records from the database."""
    return db.query(database.Candidate).all()