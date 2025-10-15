# Smart AI Resume Screener

A sophisticated, full-stack application designed to automate and enhance the resume screening process. This tool leverages a Large Language Model (LLM) to intelligently parse resumes, score them against a job description, and provide detailed, actionable insights for recruiters.

## Project Structure

```
RESUME-SCREENER/
├── backend/
│ ├── database.py
│ ├── main.py
│ ├── resume_database.db
│ └── utils.py
├── frontend/
│ ├── app.py
│ └── requirements.txt
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```
## Demo Video

- **Video Demo:** [Watch the walkthrough]([https://youtu.be/JzD-zPvhGPw](https://drive.google.com/file/d/1CudUOxlNVSmCuZ0OIsCWfJ1VP894eYh0/view?usp=sharing))

## Architecture

This application is built on a modern Client-Server Architecture to ensure scalability, modularity, and maintainability, reflecting best practices in web application development.


*   **Backend API (Python & FastAPI)**: A robust RESTful API that serves as the application's "brain." It handles all core business logic, including securely processing PDF resume uploads, interfacing with the Google Gemini LLM for analysis, managing data persistence with a SQLite database, and providing structured JSON data to the frontend.
*   **Frontend Client (Python & Streamlit)**: A user-friendly and interactive web dashboard that serves as the "face" of the application. Its sole responsibility is to present the UI and communicate with the backend via HTTP requests.
*   **Database (SQLite)**: A lightweight, serverless, and self-contained SQL database engine. It stores all processed resumes, creating a persistent and searchable Talent Pool without requiring a separate database server.

This separation of concerns allows the backend logic and the frontend presentation to be developed, scaled, and maintained independently.

## Features

*   **Intelligent Resume Screening**: Upload multiple PDF resumes and a job description to get an instant, AI-powered analysis and ranking.
*   **Color-Coded Scoring**: Candidates receive a percentage match score that is color-coded for immediate visual feedback (Green for high, Yellow for medium, Red for low).
*   **Detailed Analysis**: Each candidate's result includes a detailed breakdown of partial scores (Skills, Experience, etc.) and a qualitative summary of their specific Strengths and Weaknesses relative to the role.
*   **Persistent Talent Pool**: All screened resumes are automatically saved to a local database.
*   **Talent Pool Search**: Recruiters can search the entire database of previously screened candidates against a new job description, with custom filtering for score thresholds.

## LLM Prompt Engineering

The core of the analysis is powered by a carefully engineered prompt sent to Google's `gemini-2.5-flash` model. The prompt is designed to act as a strict contract, constraining the model's output to a specific JSON format. This ensures that the data returned is always structured, reliable, and machine-readable, which is crucial for application stability.

### Core Prompt Template

```
Act as an expert technical recruiter. Analyze the resume against the job description and return a structured JSON object.

Constraint: You must only output the JSON object. Do not include any introductory text, markdown formatting, or explanations.

The JSON object must have this exact structure:
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
      "<A detailed strength (1-2 sentences)>"
    ],
    "weaknesses": [
      "<A detailed weakness or gap (1-2 sentences)>"
    ]
  }}
}}
...
```


## Setup and Installation

To run this project locally, set up and run the backend and frontend servers in two separate terminals.

### Prerequisites
*   Python 3.8+
*   A Google Gemini API Key

### 1. Backend Setup

1.  Navigate to the backend directory.
    ```
    cd backend
    ```

2.  Create and activate a virtual environment.

    *   On **Mac/Linux**:
        ```
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   On **Windows**:
        ```
        python -m venv .venv
        .\.venv\Scripts\activate
        ```

3.  Install dependencies.
    ```
    pip install -r requirements.txt
    ```

4.  Create a `.env` file and add your API key.
    ```
    echo "GOOGLE_API_KEY='YOUR_API_KEY_HERE'" > .env
    ```

5.  Run the FastAPI server.
    ```
    uvicorn main:app --reload
    ```
    The API server will be accessible at `http://127.0.0.1:8000`.

### 2. Frontend Setup

1.  Open a **new terminal** and navigate to the frontend directory.
    ```
    cd frontend
    ```

2.  Create and activate a virtual environment.

    *   On **Mac/Linux**:
        ```
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   On **Windows**:
        ```
        python -m venv .venv
        .\.venv\Scripts\activate
        ```

3.  Install dependencies.
    ```
    pip install -r requirements.txt
    ```

4.  Run the Streamlit application.
    ```
    streamlit run app.py
    ```
    The web application will open in your browser at `http://localhost:8501`.

## API Endpoints

The backend exposes the following RESTful endpoints:

*   `POST /screen/`: Accepts a job description and a resume file (`.pdf` or `.txt`) to return a detailed JSON analysis.
*   `GET /resumes/`: Retrieves all resumes currently stored in the talent pool database.
*   `GET /docs`: Provides interactive API documentation (via Swagger UI) for testing.

