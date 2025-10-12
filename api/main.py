from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI(
    title="Smart Resume Screener API",
    description="An API to parse resumes and match them with job descriptions using AI.",
    version="1.0.0"
)

# Define a root endpoint
@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok", "message": "Welcome to the Smart Resume Screener API!"}