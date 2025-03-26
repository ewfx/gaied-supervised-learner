import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    """Create database tables using direct psycopg2 connection"""
    # Get database credentials from environment variables
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_DATABASE', 'dbName'),
        'user': os.getenv('DB_USERNAME', 'user_dev'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Read and execute the SQL script
        with open('scripts/create_service_requests_table.sql', 'r') as file:
            sql_script = file.read()
            cur.execute(sql_script)

        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_tables() 