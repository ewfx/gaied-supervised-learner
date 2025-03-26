import google.generativeai as genai
from config.gemini_config import GeminiConfig
import email
import json
import re
from services.duplicate_detector import DuplicateDetectorService
from services.service_request_manager import ServiceRequestManager

class EmailClassifierService:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=GeminiConfig.API_KEY)
        self.model = genai.GenerativeModel(
            model_name=GeminiConfig.MODEL_NAME,
            generation_config={
                "temperature": GeminiConfig.TEMPERATURE,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
        )
        
        self.classification_criteria = {
            "Request Type": {
                "Adjustment": None,
                "AU Transfer": [
                    "Reallocation Fees",
                    "Amendment Fees",
                    "Reallocation Principal"
                ],
                "Closing Notice": None,
                "Commitment Change": [
                    "Cashless Roll",
                    "Decrease",
                    "Increase"
                ],
                "Fee Payment": [
                    "Ongoing Fee",
                    "Letter of Credit Fee",
                    "Principal",
                    "Interest",
                    "Principal + Interest",
                    "Principal + Interest + Fee"
                ],
                "Money Movement - Inbound": None,
                "Money Movement - Outbound": [
                    "Timebound",
                    "Foreign Currency"
                ]
            }
        }

        # Add extraction fields mapping
        self.extraction_fields = {
            "Adjustment": {
                "default": [
                    "deal_id",
                    "transfer_amount",
                    "from_account",
                    "to_account",
                    "effective_date"
                ]
            },
            "Closing Notice": {
                "default": [
                    "deal_id",
                    "new_commitment_amount",
                    "change_reason",
                    "effective_date"
                ]
            },
            "Fee Payment": {
                "default": [
                    "deal_id",
                    "fee_type",
                    "amount",
                    "due_date",
                    "payment_reference"
                ]
            },
            "Money Movement - Inbound": {
                "default": [
                    "deal_id",
                    "funding_amount",
                    "currency",
                    "credit_account",
                    "value_date",
                    "remitter_name"
                ]
            },
            "Money Movement - Outbound": {
                "default": [
                    "deal_id",
                    "disbursement_amount",
                    "currency",
                    "debit_account",
                    "beneficiary_name",
                    "payment_method",
                    "value_date"
                ]
            }
        }

        self.duplicate_detector = DuplicateDetectorService()
        self.service_request_manager = ServiceRequestManager()

    def process_email(self, file):
        """Process email file with duplicate detection and service request creation"""
        try:
            # Validate file
            self.validate_email_file(file)
            
            # Extract email content
            email_content = self.extract_email_content(file)
            
            # Check for duplicates
            is_duplicate, confidence_score = self.duplicate_detector.check_duplicate(email_content)
            
            if is_duplicate:
                return {
                    'is_duplicate': True,
                    'confidence_score': confidence_score,
                    'error': 'Duplicate email detected'
                }
            
            # Continue with regular processing for non-duplicates
            classification_prompt = self.create_classification_prompt(email_content)
            classification_response = self.model.generate_content(classification_prompt)
            classification_result = self._parse_json_response(classification_response.text)
            
            # Get request type from classification
            request_type = classification_result.get('request_type')
            
            # Get deal details based on request type
            extraction_prompt = self.create_deal_extraction_prompt(email_content, request_type)
            extraction_response = self.model.generate_content(extraction_prompt)
            deal_details = self._parse_json_response(extraction_response.text)
            
            # Create service request
            service_request = self.service_request_manager.create_service_request(
                request_type=request_type,
                sub_request_type=classification_result.get('sub_request_type'),
                deal_id=deal_details.get('deal_id'),
                extracted_fields=deal_details,
                confidence_score=classification_result.get('confidence_score', 0.0),
                email_content=email_content
            )
            
            # Prepare response
            result = {
                'is_duplicate': False,
                'classification': classification_result,
                'extracted_fields': deal_details,
                'service_request': service_request.to_dict() if service_request else None
            }
            
            return result
                    
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise ValueError(f'Error processing email: {e}')

    def _parse_json_response(self, response_text):
        """Parse and validate JSON response"""
        try:
            # First attempt: direct JSON parsing
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Clean up the response and try again
            cleaned_response = self._clean_response_text(response_text)
            try:
                return json.loads(cleaned_response)
            except json.JSONDecodeError:
                print("Debug - Raw Response:", response_text)  # For debugging
                raise ValueError('Failed to parse response. Raw response: ' + response_text[:200])

    def _clean_response_text(self, text):
        """Clean and format response text to make it valid JSON"""
        # Remove any markdown code block indicators
        text = re.sub(r'```json\s*|\s*```', '', text)
        
        # Find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            text = text[start:end + 1]
        
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        return text

    def validate_email_file(self, file):
        """Validate if the uploaded file is a valid .eml file"""
        if not file.filename.endswith('.eml'):
            raise ValueError('Invalid file format. Please upload .eml file')
        return True

    def extract_email_content(self, eml_file):
        """Extract content from .eml file"""
        msg = email.message_from_bytes(eml_file.read())
        
        # Extract subject and body
        subject = msg.get('subject', '')
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()
        
        return f"Subject: {subject}\n\nBody: {body}"

    def create_classification_prompt(self, email_content):
        """Create prompt for email classification"""
        prompt = f"""You are an expert email classifier for a Commercial Bank Lending Service. 
        Analyze the following email and classify it based on the request type and sub-request type.
        
        Classification Criteria:
        {json.dumps(self.classification_criteria, indent=2)}
        
        Email Content:
        {email_content}
        
        Important Instructions:
        1. Analyze the email content carefully
        2. Choose the most appropriate request type and sub-request type from the provided criteria
        3. Provide a confidence score between 0 and 1
        4. Include a detailed reason for your classification
        5. Return ONLY a valid JSON object with no additional text or formatting
        6. The JSON response MUST follow this EXACT format:
        {{
            "request_type": "<classified request type>",
            "sub_request_type": "<classified sub-request type if applicable, otherwise null>",
            "confidence_score": <float between 0 and 1>,
            "reason": "<detailed explanation for the classification>"
        }}
        
        Remember: Return ONLY the JSON object, no other text or explanation.
        """
        return prompt

    def create_deal_extraction_prompt(self, email_content, request_type):
        """Create prompt for extracting deal details based on request type"""
        # Get required fields for the request type
        required_fields = self.extraction_fields.get(request_type, {}).get("default", [])
        
        fields_description = {
            "deal_id": "Deal identifier or reference number",
            "transfer_amount": "Amount to be transferred (numeric value)",
            "from_account": "Source account details",
            "to_account": "Destination account details",
            "effective_date": "Date when transfer takes effect (YYYY-MM-DD)",
            "new_commitment_amount": "Updated commitment amount (numeric value)",
            "change_reason": "Reason for commitment change",
            "fee_type": "Type of fee being paid",
            "amount": "Payment amount (numeric value)",
            "due_date": "Date when payment is due (YYYY-MM-DD)",
            "payment_reference": "Reference number for the payment",
            "funding_amount": "Amount being funded (numeric value)",
            "currency": "Currency code (e.g., USD, EUR)",
            "credit_account": "Account to be credited",
            "value_date": "Date of value (YYYY-MM-DD)",
            "remitter_name": "Name of the remitting party",
            "disbursement_amount": "Amount to be disbursed (numeric value)",
            "debit_account": "Account to be debited",
            "beneficiary_name": "Name of the beneficiary",
            "payment_method": "Method of payment"
        }

        prompt = f"""You are an expert financial data extractor for a Commercial Bank Lending Service.
        Extract specific transaction details from the email content based on the request type: {request_type}

        Email Content:
        {email_content}

        Required Fields for {request_type}:
        {json.dumps(required_fields, indent=2)}

        Field Descriptions:
        {json.dumps({field: fields_description[field] for field in required_fields}, indent=2)}

        Instructions:
        1. Carefully analyze the email content
        2. Extract ONLY the fields listed above for {request_type}
        3. Format numeric values as numbers (not strings)
        4. Use null for any required fields not found in the email
        5. Ensure dates are in YYYY-MM-DD format
        6. Return ONLY a valid JSON object
        7. If email content does not contain any of the required fields, return null for those fields

        The JSON response MUST contain exactly these fields:
        {{
            {', '.join(f'"{field}": "<appropriate value>"' for field in required_fields)}
        }}

        Important:
        - All monetary values should be numeric (e.g., 1000000.00)
        - Dates must be in YYYY-MM-DD format
        - Use null for any fields not found in the email
        - Extract values exactly as they appear in the email
        - Do not include any fields not listed in the requirements

        Remember: Return ONLY the JSON object, no other text or explanation.
        """
        return prompt 