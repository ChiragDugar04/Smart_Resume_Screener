AI-Powered Resume Screener
This is a Streamlit web application that uses Google's Gemini API to screen and rank resumes based on a given job description.

Features
Resume Screening: Upload multiple resumes and a job description to get a ranked list of candidates. View detailed analysis including skill match, experience match, strengths, and weaknesses for each candidate.

Talent Pool Search: Search a database of previously uploaded resumes against a new job description to find suitable candidates.

Setup and Installation
Clone the repository:

git clone <your-repository-url>
cd <repository-name>

Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the dependencies:

pip install -r requirements.txt

Set up your environment variables:
Create a .env file in the root directory and add your Google API key:

GOOGLE_API_KEY="YOUR_API_KEY"

Run the Streamlit application:

streamlit run app.py
