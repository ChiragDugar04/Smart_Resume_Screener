from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json

# Define the database URL. SQLite will create a file named 'screener.db'
DATABASE_URL = "sqlite:///./screener.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Define a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our declarative models
Base = declarative_base()

# Define the 'screenings' table model
class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, index=True)
    job_description = Column(Text, nullable=False)

    # We will store JSON data as text
    resume_data = Column(Text, nullable=False) # Storing ParsedResume as a JSON string
    match_result = Column(Text, nullable=False) # Storing MatchResult as a JSON string

# Create the table in the database (if it doesn't exist)
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)