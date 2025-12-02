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


class ChatbotService:

    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name
    

    def chat(self, school_id: str, question: str):
        retriever = chroma_db_service.get_retrieval_for_school(school_id=school_id)

        SYSTEM = (
            "you are a helpful assistant that answering questions about school policies."
            "Use only the provided context. If you don't know the answer, just say that you don't know, don't try to make up an answer."
            "If the question is not about school policies, ignore the question. Do not answer any questions that are not about school policies."
            "Your tone should be professional and concise."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM),
            ("human", "Context:\n{context}\n\nQuestion: {input}")
        ])

        llm = LLMModelFactory.get_model_provider('gemini').get_model()

        chain = (
            {
            "context": retriever,
            "input": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        answer = chain.invoke({"input": question})

        return answer

        