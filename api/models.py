from pydantic import BaseModel, Field
from typing import List, Optional

class Education(BaseModel):
    institution: str = Field(description="Name of the university or institution.")
    degree: str = Field(description="Degree obtained, e.g., Bachelor of Science.")
    major: Optional[str] = Field(None, description="Major or field of study.")
    graduation_year: Optional[int] = Field(None, description="Year of graduation.")

class Experience(BaseModel):
    company: str = Field(description="Name of the company.")
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