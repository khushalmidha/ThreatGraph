from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://netraptor:netraptor_pass@localhost:5432/netraptor_db")

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
