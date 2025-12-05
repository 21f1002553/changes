from ..prompt import PromptManager
from ..llm_factory import LLMModelFactory
from utils import TextUtility
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .resume_service import ParseResume

# courses recommendation service
class RecommendationService:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name

    def generate_course_recommendations(self, resume_text, job_title, courses):
        """
        prompting LLM to generate course recommendations from resume and job description
        args:
            resume_text: resume text
            job_title: job title
            job_description: job description
        """
        if not resume_text or not job_title or not courses:
            raise ValueError("Resume text, job title, job description and courses are required")
        # get the prompts
        prompt=PromptManager.course_recommendation_prompt(resume_text, job_title, courses)
        # load gemini model
        llm=LLMModelFactory.get_model_provider(self.model_name).get_model()

        # generate content
        try:
            attempt = 0
            max_attempts = 3
            while True:
                try:
                    response = llm.generate_content(prompt)
                    if not response or not response.text:
                        raise ValueError("Empty response from LLM")
                    break
                except Exception as e:
                    attempt += 1
                    msg = str(e).lower()
                    if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                        import time
                        time.sleep(1 * (2 ** (attempt - 1)))
                        continue
                    raise
        except Exception as e:
            raise RuntimeError(f"Error generating course recommendations: {e}")

        output=TextUtility.remove_json_marker(response.text)
        return output


# Interview generation
class InterviewService:
    """
        Generate mock interview for candidates
        args:
            job_title: job title
            job_description: job description
            requirements: job requirements
    """
    def __init__(self,model_name: str = 'gemini'):
        self.model_name=model_name
    
    def generate_mock_interview(self,job_title, job_description, requirements, n_easy_questions: int, n_medium_questions: int , n_hard_questions: int):

        if not job_title or not job_description or not requirements:
            raise ValueError("Job title, job description and requirements are required")
        
        prompt=PromptManager.mock_interview_prompt(job_title, job_description, requirements, n_easy_questions, n_medium_questions, n_hard_questions)

        # load gemini model
        llm=LLMModelFactory.get_model_provider(self.model_name).get_model()

        # generate content
        try:
            attempt = 0
            max_attempts = 3
            while True:
                try:
                    response = llm.generate_content(prompt)
                    if not response or not response.text:
                        raise ValueError("Empty response from LLM")
                    break
                except Exception as e:
                    attempt += 1
                    msg = str(e).lower()
                    if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                        import time
                        time.sleep(1 * (2 ** (attempt - 1)))
                        continue
                    raise
        except Exception as e:
            raise RuntimeError(f"Error generating mock interview: {e}")
        
        output = TextUtility.remove_json_marker(response.text)
        return output

    


# resume tailoring
class ProfileEnhancementService:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name

    def generate_profile_enhancement(self, resume_id, job_title):

        resume_text = ParseResume.parse_resume_text(resume_id)
        
        if not resume_text or not job_title:
            raise ValueError("Resume text and job title are required")
        
        # load the prompt
        prompt=PromptManager.tailor_resume_prompt(resume_text, job_title)
        # load gemini model
        llm=LLMModelFactory.get_model_provider(self.model_name).get_model()

        # generate content
        try:
            attempt = 0
            max_attempts = 3
            while True:
                try:
                    response = llm.generate_content(prompt)
                    if not response or not response.text:
                        raise ValueError("Empty response from LLM")
                    break
                except Exception as e:
                    attempt += 1
                    msg = str(e).lower()
                    if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                        import time
                        time.sleep(1 * (2 ** (attempt - 1)))
                        continue
                    raise
        except Exception as e:
            raise RuntimeError(f"Error generating profile enhancement: {e}")

        output = TextUtility.remove_json_marker(response.text)
        return output
    

#  Make JD based on Job title

class JobDescriptionService:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name

    def generate_job_description(self, job_title):
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("assistant", "{output}"),
        ])

        few_shot = FewShotChatMessagePromptTemplate(
            examples=PromptManager.example_prompt(),
            example_prompt=example_prompt,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptManager.make_JD_prompt(job_title)),
            few_shot, (
                "human",
                """
                Generate a Job Description with same structure and tone
                Job title: {job_title}
                """)
        ])

        # llm chain
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        chain = prompt | llm | StrOutputParser()

        try:
            output = chain.invoke({
                "job_title": job_title
            })
        except Exception as e:
            raise RuntimeError(f"Error generating job description: {e}")
      
        return output


# get upskilling path
class UpskillingPathService:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name
    
    def get_upskilling_path(self, resume_text, job_title, job_description, courses):
        if not resume_text or not job_title:
            raise ValueError("Resume text and job title are required")
        
        # load the prompt
        prompt=PromptManager.skill_gap_suggest_upskill_prompt(resume_text, job_description, job_title, courses)
        # load gemini model
        llm=LLMModelFactory.get_model_provider(self.model_name).get_model()

        # generate content (with retry/backoff for transient rate limits)
        try:
            attempt = 0
            max_attempts = 3
            while True:
                try:
                    response = llm.generate_content(prompt)
                    if not response or not response.text:
                        raise ValueError("Empty response from LLM")
                    break
                except Exception as e:
                    attempt += 1
                    msg = str(e).lower()
                    if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                        import time
                        time.sleep(1 * (2 ** (attempt - 1)))
                        continue
                    raise
        except Exception as e:
            raise RuntimeError(f"Error generating upskilling path: {e}")

        output = TextUtility.remove_json_marker(response.text)
        return output
