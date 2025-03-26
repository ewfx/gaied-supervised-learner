from config.database import engine, DB_SCHEMA
from models.db_models import Base
from sqlalchemy import text

def init_db():
    """Initialize the database by creating schema and tables"""
    try:
        # Create schema if it doesn't exist
        with engine.connect() as connection:
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}'))
            connection.commit()
        
        # Create all tables in the schema
        Base.metadata.create_all(bind=engine)
        print(f"Database schema '{DB_SCHEMA}' and tables created successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    print("Creating database schema and tables...")
    init_db() 