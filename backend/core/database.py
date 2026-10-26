import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("A DATABASE_URL não foi encontrada no ficheiro .env")

engine = create_engine(DATABASE_URL)