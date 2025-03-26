# Email Classification and OCR

A system for processing and triaging banking service requests using AI-powered classification and team assignment.

## Features

- Email classification using Gemini AI
- Duplicate detection using sentence transformers
- Service request creation and management
- Team assignment based on request types
- PostgreSQL database integration
- RESTful API endpoints

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd banking-triage-system-v2
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database Configuration
   DB_HOST=your_db_host
   DB_PORT=5432
   DB_DATABASE=your_database_name
   DB_USERNAME=your_username
   DB_PASSWORD=your_password
   DB_SCHEMA=banking_triage

   # Google API Configuration
   GOOGLE_API_KEY=your_gemini_api_key
   MODEL_NAME=gemini-2.0-flash
   MODEL_TEMPERATURE=0

   # Flask Configuration
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_DEBUG=0

   # Server Configuration
   HOST=0.0.0.0
   PORT=5000
   ```

5. **Set up the database**
   ```bash
   # Create database schema and tables
   python scripts/create_tables.py
   ```

6. **Run the application**
   ```bash
   # Start the Flask server
   python app.py
   ```

## Project Structure

```
banking-triage-system-v2/
├── api/
│   └── routes.py              # API endpoints
├── config/
│   ├── database.py           # Database configuration
│   ├── gemini_config.py      # Gemini AI configuration
│   └── constants.py          # Global constants
├── models/
│   ├── service_request.py    # Service request model
│   └── db_models.py          # Database models
├── services/
│   ├── email_classifier.py   # Email classification service
│   ├── duplicate_detector.py # Duplicate detection service
│   └── service_request_manager.py # Service request management
├── scripts/
│   ├── create_tables.py      # Database table creation
│   └── test_db_connection.py # Database connection testing
├── app.py                    # Main application file
├── requirements.txt          # Project dependencies
└── .env                      # Environment variables
```

## API Endpoints

### Process Email
- **POST** `/process-email`
  - Process and classify an email
  - Creates a service request if not duplicate
  - Returns classification and service request details

### Service Requests
- **GET** `/service-requests/<request_id>`
  - Get details of a specific service request

- **GET** `/service-requests/team/<team>`
  - Get all service requests assigned to a team

- **PUT** `/service-requests/<request_id>/status`
  - Update the status of a service request

## Database Schema

The system uses a PostgreSQL database with the following main table:

### service_requests
- `id`: UUID (Primary Key)
- `request_type`: VARCHAR
- `sub_request_type`: VARCHAR
- `deal_id`: VARCHAR
- `extracted_fields`: JSONB
- `confidence_score`: FLOAT
- `team_assigned`: VARCHAR
- `status`: VARCHAR
- `created_at`: TIMESTAMP WITH TIME ZONE
- `updated_at`: TIMESTAMP WITH TIME ZONE

## Team Assignment

Service requests are automatically assigned to teams based on request type:
- Adjustment → ADJUSTMENT_TEAM
- AU Transfer → TRANSFER_TEAM
- Closing Notice → CLOSING_TEAM
- Commitment Change → COMMITMENT_TEAM
- Fee Payment → FEE_TEAM
- Money Movement - Inbound → INBOUND_TEAM
- Money Movement - Outbound → OUTBOUND_TEAM

## Error Handling

The system includes comprehensive error handling for:
- Database connection issues
- Invalid email formats
- Duplicate detection
- Classification errors
- API request validation

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Add docstrings for functions and classes

2. **Testing**
   - Write unit tests for new features
   - Test database operations
   - Test API endpoints

3. **Security**
   - Never commit sensitive information
   - Use environment variables for credentials
   - Validate all input data

## Troubleshooting

1. **Database Connection Issues**
   - Verify database credentials in `.env`
   - Check database server status
   - Ensure database and schema exist

2. **API Errors**
   - Check request format
   - Verify API keys
   - Check server logs

3. **Classification Issues**
   - Verify Gemini API key
   - Check email format
   - Review classification criteria

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]