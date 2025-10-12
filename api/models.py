from pydantic import BaseModel, Field
from typing import List, Optional

class Education(BaseModel):
    institution: str = Field(description="Name of the university or institution.")
    degree: str = Field(description="Degree obtained, e.g., Bachelor of Science.")
    major: Optional[str] = Field(None, description="Major or field of study.")
    graduation_year: Optional[int] = Field(None, description="Year of graduation.")

class Experience(BaseModel):
    company: Optional[str] = Field(None, description="Name of the company.")
    role: str = Field(description="Job title or role.")
    start_date: str = Field(description="Start date of the employment.")
    end_date: Optional[str] = Field(description="End date of the employment (or 'Present').")
    description: List[str] = Field(description="List of responsibilities or achievements.")

class ParsedResume(BaseModel):
    full_name: str = Field(description="Candidate's full name.")
    email: Optional[str] = Field(None, description="Candidate's email address.")
    phone_number: Optional[str] = Field(None, description="Candidate's phone number.")
    linkedin_url: Optional[str] = Field(None, description="URL to the candidate's LinkedIn profile.")
    skills: List[str] = Field(description="List of technical and soft skills mentioned.")
    education: List[Education] = Field(description="List of educational qualifications.")
    experience: List[Experience] = Field(description="List of professional experiences.")

# --- NEW MODEL FOR DETAILED BREAKDOWN ---
class MatchBreakdownItem(BaseModel):
    category: str = Field(description="The category of the match, e.g., 'Skills', 'Experience'.")
    match_percentage: int = Field(description="How well this category matches the job, from 0 to 100.")

class MatchResult(BaseModel):
    match_score: int = Field(description="An integer score from 1 to 100 for candidate-job fit.")
    summary: str = Field(description="A concise, one-sentence summary of the candidate's suitability.")
    strengths: List[str] = Field(description="Specific skills or experiences that align well with the job.")
    weaknesses: List[str] = Field(description="Key requirements from the job that are missing or weak in the resume.")
    # --- ADDING THE BREAKDOWN LIST ---
    breakdown: List[MatchBreakdownItem] = Field(description="A detailed breakdown of matches by category.")

class CombinedScreeningResult(BaseModel):
    resume_data: ParsedResume
    match_data: MatchResult