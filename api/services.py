import fitz
from typing import IO
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from .models import CombinedScreeningResult

def extract_text_from_pdf(pdf_file: IO[bytes]) -> str:
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        full_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            full_text += page.get_text()
        return full_text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

load_dotenv()

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except TypeError:
    print("Error: GOOGLE_API_key not found in environment variables.")
    exit()

def perform_combined_screening_with_llm(resume_text: str, job_description: str) -> CombinedScreeningResult:
    model = genai.GenerativeModel('gemini-2.5-flash')

    # --- NEW, ENHANCED PROMPT ---
    prompt = f"""
    You are an expert HR AI assistant. Your task is to perform a detailed analysis of a resume against a job description.

    Actions:
    1. Parse the raw resume text into a structured JSON object.
    2. Compare the parsed resume to the job description to generate a match analysis.
    3. Provide a detailed, categorical breakdown of the match using ONLY the four specified categories.

    ---RESUME TEXT START---
    {resume_text}
    ---RESUME TEXT END---

    ---JOB DESCRIPTION START---
    {job_description}
    ---JOB DESCRIPTION END---

    Your output MUST be a single, valid JSON object that strictly follows this schema. Do not include any other text or explanations.

    {{
    "resume_data": {{
        "full_name": "string", "email": "string | null", "phone_number": "string | null", "linkedin_url": "string | null",
        "skills": ["string", ...],
        "education": [{{ "institution": "string", "degree": "string", "major": "string | null", "graduation_year": integer | null }}],
        "experience": [{{ "company": "string | null", "role": "string", "start_date": "string", "end_date": "string | null", "description": ["string", ...] }}]
    }},
    "match_data": {{
        "match_score": integer, "summary": "string", "strengths": ["string", ...], "weaknesses": ["string", ...],
        "breakdown": [
            {{ "category": "Educational Background", "match_percentage": integer (0-100) }},
            {{ "category": "Technical Skills", "match_percentage": integer (0-100) }},
            {{ "category": "Relevant Experience/Projects", "match_percentage": integer (0-100) }},
            {{ "category": "Soft Skills", "match_percentage": integer (0-100) }}
        ]
    }}
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
        parsed_data = json.loads(cleaned_json_string)
        validated_result = CombinedScreeningResult(**parsed_data)
        return validated_result
    except json.JSONDecodeError as e:
        print(f"Error decoding LLM JSON response: {e}")
        print(f"Raw LLM response that failed to parse: {response.text}")
        raise ValueError("Failed to process the screening. The LLM response was not valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred during the screening process: {e}")
        raise ValueError("Failed to process the screening due to an unexpected API or network error.")