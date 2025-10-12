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