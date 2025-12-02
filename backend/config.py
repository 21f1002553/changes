from dotenv import dotenv_values


_properties = dotenv_values('.env')

class Config:
    GEMINI_API_KEY=_properties['GEMINI_API_KEY']
    LANGCHAIN_API_KEY=_properties['LANGCHAIN_API_KEY']
    OPENAI_API_KEY=_properties['OPENAI_API_KEY']
    DATA_ROOT=_properties['DATA_ROOT']
    ONBOARDING_REQUIRED_DOCS = [
        "id_proof",
        "address_proof",
        "education_certificate",
        "work_experience_certificate"
    ]
    ONBOARDING_FORM_SCHEMAS = {
    "offer-letter": {
        "title": "Offer Letter",
        "fields": [
            {"name": "ctc", "type": "text", "required": True},
            {"name": "designation", "type": "text", "required": True},
            {"name": "start_date", "type": "date", "required": True}
        ],
        "allow_upload_signed": True
    },

    "code-of-conduct": {
        "title": "Code of Conduct",
        "fields": [
            {"name": "full_name", "type": "text", "required": True},
            {"name": "accept_terms", "type": "checkbox", "required": True}
        ],
        "allow_upload_signed": True
    }
}