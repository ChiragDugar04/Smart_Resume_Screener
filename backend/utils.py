import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

JSON_PROMPT_TEMPLATE = """
Act as an expert technical recruiter and resume parser. Your task is to analyze a resume against a job description and return a structured JSON object.

Constraint: You must only output the JSON object. Do not include any introductory text, markdown formatting, or explanations.

The JSON object must have this exact nested structure:
{{
  "name": "Candidate's Full Name",
  "score": <A single overall percentage match score from 0-100>,
  "partial_scores": {{
    "Skill Match": <0-100>,
    "Experience Match": <0-100>,
    "Education Match": <0-100>,
    "Soft Skill Match": <0-100>
  }},
  "summary": {{
    "strengths": [
      "<Provide 2-3 detailed strengths (1-2 sentences each), citing evidence from the resume.>"
    ],
    "weaknesses": [
      "<Provide 2-3 detailed weaknesses or gaps (1-2 sentences each), based on the job description.>"
    ]
  }}
}}

Job Description:
{jd}

Resume:
{resume_text}

Remember: Your entire output must be a single, valid JSON object and nothing else.
"""

# --- THIS IS THE CORRECTED FUNCTION ---
def get_gemini_response(jd, resume_text):
    """
    This function now correctly accepts two arguments, formats the prompt,
    and then calls the Gemini model.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        # The prompt is now formatted inside this function
        prompt = JSON_PROMPT_TEMPLATE.format(jd=jd, resume_text=resume_text)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return None

