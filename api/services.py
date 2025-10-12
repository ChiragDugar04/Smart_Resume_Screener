from .models import MatchResult
import fitz 
from typing import IO

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
        # In a real app, you'd want more robust error logging
        return ""
    
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from .models import ParsedResume # Import our Pydantic model

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except TypeError:
    # This happens if the API key is not set, handle it gracefully
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    # Exit or raise a custom exception in a real application
    exit()

def parse_resume_with_llm(resume_text: str) -> ParsedResume:
    model = genai.GenerativeModel('gemini-1.5-flash') # Using the fast and cost-effective model

    # This is our engineered prompt. Note the explicit instructions for JSON output.
    prompt = f"""
    You are an expert resume parser. Your task is to analyze the following resume text and extract key information in a structured JSON format.
    The JSON output *must* strictly adhere to the provided schema. Do not add any extra text, explanations, or markdown formatting around the JSON.

    Resume Text:
    ---
    {resume_text}
    ---

    Required JSON Schema:
    {{
      "full_name": "string",
      "email": "string | null",
      "phone_number": "string | null",
      "linkedin_url": "string | null",
      "skills": ["string", "string", ...],
      "education": [
        {{
          "institution": "string",
          "degree": "string",
          "major": "string | null",
          "graduation_year": integer | null
        }}
      ],
      "experience": [
        {{
          "company": "string",
          "role": "string",
          "start_date": "string",
          "end_date": "string | null",
          "description": ["string", "string", ...]
        }}
      ]
    }}

    Now, parse the resume text and provide the output in the specified JSON format only.
    """

    try:
        response = model.generate_content(prompt)
        
        # The API might return the JSON wrapped in markdown, so we clean it.
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        # Parse the cleaned string into a Python dictionary
        parsed_data = json.loads(cleaned_json_string)
        
        # Validate the dictionary against our Pydantic model
        validated_resume = ParsedResume(**parsed_data)
        
        return validated_resume

    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error decoding LLM response: {e}")
        print(f"Raw response was: {response.text}")
        # In a real app, you might want to retry or handle this more elegantly
        raise ValueError("Failed to parse resume. The LLM response was not valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
    
def match_resume_to_jd_with_llm(resume_json: str, job_description: str) -> MatchResult:
    """
    Compares a parsed resume (in JSON format) with a job description using the Gemini API.

    Args:
        resume_json: The parsed resume data as a JSON string.
        job_description: The text of the job description.

    Returns:
        A MatchResult Pydantic object with score and justification.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are an expert HR analyst and technical recruiter with 15 years of experience, specializing in AI-driven talent acquisition.
    Your task is to perform a detailed, unbiased comparison between a candidate's resume and a job description.

    Analyze the provided structured resume data and the job description. Focus on the alignment of skills, the relevance of experience, and educational background.

    ---JOB DESCRIPTION START---
    {job_description}
    ---JOB DESCRIPTION END---

    ---CANDIDATE'S RESUME (JSON) START---
    {resume_json}
    ---CANDIDATE'S RESUME (JSON) END---

    Based on your analysis, provide your output *only* in the following JSON format. Do not include any other text, explanations, or markdown formatting.

    {{
      "match_score": <An integer score from 1 to 10, where 1 is a very poor fit and 10 is a perfect match>,
      "summary": "<A concise, one-sentence summary of the candidate's suitability.>",
      "strengths": [
        "<A specific skill, experience, or qualification from the resume that directly aligns with the job description.>",
        "<Another key strength.>"
      ],
      "weaknesses": [
        "<A key requirement from the job description that is missing or weakly represented in the resume.>",
        "<Another potential gap.>"
      ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
        parsed_data = json.loads(cleaned_json_string)
        
        # Validate against the MatchResult Pydantic model
        validated_result = MatchResult(**parsed_data)
        return validated_result

    except Exception as e:
        print(f"Error during resume matching: {e}")
        print(f"Raw LLM response was: {response.text}")
        raise ValueError("Failed to match resume. The LLM response was not valid JSON.")