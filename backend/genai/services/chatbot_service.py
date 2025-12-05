from ..prompt import PromptManager
from ..llm_factory import LLMModelFactory
from utils import TextUtility
from operator import itemgetter

import os
from pathlib import Path


from database.vector_db import chroma_db_service
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import google.generativeai as genai
from dotenv import load_dotenv
from config import Config

load_dotenv()

class ChatbotService:

    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name
        # Configure Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Add school policy document to vector store
        try:
            self.add_doc_embedding = chroma_db_service.add_school_policy(
                path='./uploads/documents\knowledge_doc.pdf', 
                school_id=1
            )
        except Exception as e:
            print(f"Warning: Could not load policy document: {e}")

    def chat(self, school_id: str, question: str):
        """
        Chat with AI assistant using retrieval from vector database
        
        Args:
            school_id: The school ID for context retrieval
            question: User's question
            
        Returns:
            str: AI-generated answer based on context
        """
        try:
            # Get relevant context from vector database
            retriever = chroma_db_service.get_retrieval_for_school(school_id=1)
            relevant_docs = retriever.invoke(question)
            
            # Combine retrieved documents into context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Create the prompt
            system_instruction = (
                "You are a helpful HR assistant that answers questions about company policies, "
                "leave requests, benefits, and general HR questions. "
                "Use only the provided context. If you don't know the answer, just say that you don't know. "
                "Don't try to make up an answer. Your tone should be professional and concise."
            )
            
            prompt = f"""System: {system_instruction}

Context:
{context}

User Question: {question}

Assistant Answer:"""
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error in chatbot: {str(e)}")
            # Fallback to direct answer without context if retrieval fails
            try:
                fallback_prompt = f"""You are a helpful HR assistant. 
                
User Question: {question}

Please provide a helpful answer:"""
                
                response = self.model.generate_content(fallback_prompt)
                return response.text
            except Exception as fallback_error:
                return "I apologize, but I'm having trouble processing your request. Please try again or contact HR directly."

        