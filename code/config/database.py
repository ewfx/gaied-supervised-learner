from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'banking_triage')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'banking_triage')

# URL encode the password to handle special characters
encoded_password = quote_plus(DB_PASSWORD)

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Set the schema for all connections
@event.listens_for(engine, 'connect')
def set_schema(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f'SET search_path TO {DB_SCHEMA}')
    cursor.close()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 