# backend/utils/text_utility.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader 
from langchain_community.document_loaders import PyPDFLoader
import os 
from pathlib import Path
import re
import json
from config import Config

class TextUtility:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        loader = PyPDFLoader(pdf_path)
        text = loader.load()
        content = ''
        for i in range(len(text)):
            content += text[i].page_content
        return content
    
    @staticmethod
    def extract_text_from_docx(file_path):
        docx_loader=Docx2txtLoader(file_path)
        docs=docx_loader.load()
        content=''
        for i in range(len(docs)):
            content+=docs[i].page_content
        return content
    
    @staticmethod
    def remove_pii(text: str):
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+','[EMAIL]', text)
        text = re.sub(r'\+?\d[\d\s\()]{7,}\d', '[PHONE]', text)
        text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)
        return text.strip()
    
    @staticmethod
    def remove_json_marker(text: str):

        if not text or not isinstance(text, str):
            return {}
        text=text.strip()
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3]
        
        text=text.strip()

        try:
            print("json")
            return json.loads(text)
        except json.JSONDecodeError:
            json_obj = TextUtility.extract_multiple_json_objects(text)
            if json_obj:
                print("json_obj")
                return json_obj
            print("text")
            return text
        
        
        # cleaned_json=text.strip('`json \n')
        # try:
        #     return json.loads(cleaned_json)
        # except json.JSONDecodeError:
        #     return cleaned_json


    @staticmethod
    def format_resume_text(resume) -> str:
        try:
            lines = []

            lines.append(f"Location: {resume.get('location', '')}")
            lines.append(f"Total Experience: {resume.get('total_experience', '')}")
            lines.append("Skills: " + ", ".join(resume.get("skills", [])))

            lines.append("\nWork Experience:")
            for exp in resume.get("work_experience", []):
                lines.append(f"- {exp['title']} at {exp['company']} ({exp['start_date']} to {exp['end_date']}): {exp['description']}")

            lines.append("\nEducation:")
            for edu in resume.get("education", []):
                lines.append(f"- {edu['degree']} in {edu['field_of_study']} from {edu['institute']} ({edu['start_date']}–{edu['end_date']})")

            lines.append("\nCertifications:")
            for cert in resume.get("certifications", []):
                lines.append(f"- {cert}")

            lines.append("\nProjects:")
            for proj in resume.get("projects", []):
                lines.append(f"- {proj['title']}: {proj['description']}")

            return "\n".join(lines)

        except Exception as e:
            print(f"Error formatting resume text: {e}")
            return json.dumps(resume)
    

    @staticmethod
    def resolve_path(file_path: str, data_root: str | None):
        """
        Resolve a DB-stored file_path into an absolute path.

        - If file_path is already absolute, returns it as-is.
        - If file_path is relative, prefixes it with DATA_ROOT (env or provided).

        Args:
            file_path: str - the path from DB (relative or absolute)
            data_root: optional override for DATA_ROOT env (e.g. during testing)

        Returns:
            Path object pointing to an absolute file location
        """

        p = Path(file_path)

        if p.is_absolute():
            return p.resolve()
        

        root = data_root or Config.DATA_ROOT
        root_path = Path(root)

        if not root_path.is_absolute():
            root_path = Path.cwd() / root_path

        return (root_path / p).resolve()
    

    @staticmethod
    def extract_multiple_json_objects(text: str):
        """
        Extracts multiple JSON objects from messy text.
        Returns a list of dicts or empty list.
        """
        # Regular expression to find JSON objects {...}
        pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'

        matches = re.findall(pattern, text, flags=re.DOTALL)
        json_list = []

        for m in matches:
            try:
                obj = json.loads(m)
                json_list.append(obj)
            except:
                continue

        return json_list if json_list else None