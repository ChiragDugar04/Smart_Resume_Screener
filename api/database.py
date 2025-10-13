from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

DATABASE_URL = "sqlite:///./screener.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# NEW: Candidate Table - Stores unique information about each person.
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True) # Email is the unique identifier
    parsed_resume_data = Column(Text, nullable=False) # Full parsed resume as JSON
    
    # This links a candidate to all their screening records
    screenings = relationship("ScreeningRecord", back_populates="candidate")

# NEW: Screening Record Table - Stores each screening event.
class ScreeningRecord(Base):
    __tablename__ = "screening_records"
    
    id = Column(Integer, primary_key=True, index=True)
    job_role_title = Column(String, index=True) # e.g., "Senior Data Scientist"
    match_score = Column(Integer, index=True) # Score from 0-100
    candidate_id = Column(Integer, ForeignKey("candidates.id")) # Links to the candidate
    job_description_text = Column(Text)
    screening_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="screenings")

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)