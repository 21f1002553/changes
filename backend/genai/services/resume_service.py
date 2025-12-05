from ..prompt import PromptManager
from models import User, Role, Resume, JobPost, Application, PerformanceReview, db
from database.vector_db import chroma_db_service
from ..llm_factory import LLMModelFactory
from utils import TextUtility

class ResumeService:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name
    
    def resume_service(self,resume_id):

        parsed_resume = ParseResume.parse_resume_text(resume_id)
        chroma_db_service.clear_collection(collection_name='resume')
        # embed resume and store it in chroma
        chroma_db_service.add_resume(
            resume_id=resume_id,
            metadata={
                "resume_id": resume_id
            },
            text=parsed_resume,
            clear_first=True
        )

        # search top-n job based on resume
        jobs = chroma_db_service.search_jobs_for_resume(parsed_resume)
        print(jobs)
        sorted_jobs = sorted(jobs, key=lambda x: x['distance'])
        
        return sorted_jobs[0] # dict 
        

# store all the jobs in vector db
class JobService:

    def __init__(self, collection_name: str = 'job_post'):
        self.collection_name = collection_name

    def store_multiple_job_posts(self):
        job_posts=JobPost.query.all()
        chroma_db_service.clear_collection(collection_name=self.collection_name)
        for job_post in job_posts:
            job=job_post.to_dict()

            metadata= {
                "job_id": job['id'],
                "title": job['title'],
                "description": job['description'] or "",
                "requirements": job['requirements'] or "",
                "status": job['status'],
                "created_at": job['created_at']
            }

            text = f"{job['title']}\n{job['description']}\n{job['requirements']}"

            #load job data into vector store
            chroma_db_service.add_job_post(
                job_post_id=job['id'],
                metadata=metadata,
                text=text,
                clear_first=True
            )
        
    # delete job post from vector db
    def delete_job_post(self):
        chroma_db_service.clear_collection(collection_name=self.collection_name)

# resume matching with jobs
class ResumeMatch:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name

    # get score and key metrics
    def resume_match(self, job_title , job_description, job_requirements, job_id):
        # get all the resumes of candidates
        resumes_with_applications = (
            db.session.query(Resume, Application, User)
            .join(Application, Resume.id == Application.resume_id)
            .join(User, Resume.owner_id == User.id)
            .join(Role, User.role_id == Role.id)
            .filter(
                Role.name == 'candidate',
                Application.job_id == job_id,
                Application.status.in_(['applied', 'screening', 'shortlisted', 'submitted'])
            )
            .all()
        )
        chroma_db_service.clear_collection(collection_name='resume')
        # extract key details (skill,etc) from resume and parse it
        for resume, application, user in resumes_with_applications:
            

            if resume.file_url is not None and resume.file_url.endswith('.pdf'):

                parsed_resume = TextUtility.extract_text_from_pdf(resume.file_url)
                parsed_resume = TextUtility.remove_pii(parsed_resume)
                prompt = PromptManager.get_structure_json_resume(parsed_resume)
                llm = LLMModelFactory.get_model_provider(self.model_name).get_model()
                # call LLM with retry on transient failures (rate limit/resource exhausted)
                attempt = 0
                max_attempts = 3
                while True:
                    try:
                        response = llm.generate_content(prompt)
                        parsed_resume = TextUtility.remove_json_marker(response.text)
                        break
                    except Exception as e:
                        attempt += 1
                        msg = str(e).lower()
                        if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                            import time
                            time.sleep(1 * (2 ** (attempt - 1)))
                            continue
                        raise
                parsed_resume = TextUtility.format_resume_text(parsed_resume)
                # print(type(parsed_resume))
                
                chroma_db_service.add_resume(
                    resume_id = resume.id,
                    text = parsed_resume,
                    metadata={
                        "user_id": resume.owner_id,
                        "resume_id": resume.id,
                        "application_id": application.id,
                        "candidate_name": user.name,
                        "job_id": job_id,
                        "application_status": application.status
                    }
                )
                print(parsed_resume)
            elif resume.file_url is not None and resume.file_url.endswith('.docx'):

                parsed_resume = TextUtility.extract_text_from_docx(resume.file_url)
                parsed_resume = TextUtility.remove_pii(parsed_resume)
                prompt = PromptManager.get_structure_json_resume(parsed_resume)
                llm = LLMModelFactory.get_model_provider(self.model_name).get_model()
                attempt = 0
                max_attempts = 3
                while True:
                    try:
                        response = llm.generate_content(prompt)
                        parsed_resume = TextUtility.remove_json_marker(response.text)
                        break
                    except Exception as e:
                        attempt += 1
                        msg = str(e).lower()
                        if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                            import time
                            time.sleep(1 * (2 ** (attempt - 1)))
                            continue
                        raise
                parsed_resume = TextUtility.format_resume_text(parsed_resume)
                # print(parsed_resume)
                chroma_db_service.add_resume(
                    resume_id = resume.id,
                    text = parsed_resume,
                    metadata={
                        "user_id": resume.owner_id,
                        "resume_id": resume.id,
                        "application_id": application.id,
                        "candidate_name": user.name,
                        "job_id": job_id,
                        "application_status": application.status
                    }
                )
                print(parsed_resume)

        # search top-n resume based on jobs
        job_text = f"{job_title}\n{job_description}\n{job_requirements}"
        resumes = chroma_db_service.search_resumes_for_job(job_text, k=min(5, len(resumes_with_applications)))
        # print(resumes)
        sorted_resumes = sorted(resumes, key = lambda x: x['distance'])
        # print(sorted_resumes)
        # resume_texts = list(sorted_resumes[0]['id']+sorted_resumes[0][res] for res in sorted_resumes[0] if res == 'text')
        # for resume_text in resume_texts:
        # print(resume_text)
        prompt = PromptManager.resume_shortlisting_prompt(sorted_resumes[0], job_title, job_description, job_requirements)
        llm = LLMModelFactory.get_model_provider(self.model_name).get_model()
        attempt = 0
        max_attempts = 3
        while True:
            try:
                response = llm.generate_content(prompt)
                result = TextUtility.remove_json_marker(response.text)
                break
            except Exception as e:
                attempt += 1
                msg = str(e).lower()
                if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                    import time
                    time.sleep(1 * (2 ** (attempt - 1)))
                    continue
                raise
        print(result)
        # res={"resume_id":resume_text[0], **result}
        return result

        
        # example output = [{resume_id: 1, score: 0.9, key_metrics: [skill1, skill2]}, {}, {}]


class ParseResume:


    @staticmethod
    def parse_resume_text(resume_id):
        resume=Resume.query.get_or_404(resume_id)
        if resume.file_url is not None and resume.file_url.endswith('.pdf'):
            parsed_resume = TextUtility.extract_text_from_pdf(resume.file_url)
        elif resume.file_url is not None and resume.file_url.endswith('.docx'):
            parsed_resume = TextUtility.extract_text_from_docx(resume.file_url)
        try:
            parsed_resume = TextUtility.remove_pii(parsed_resume)
            prompt = PromptManager.get_structure_json_resume(parsed_resume)
            llm = LLMModelFactory.get_model_provider('gemini').get_model()
            attempt = 0
            max_attempts = 3
            while True:
                try:
                    response = llm.generate_content(prompt)
                    parsed_resume = TextUtility.remove_json_marker(response.text)
                    parsed_resume = TextUtility.format_resume_text(parsed_resume)
                    return parsed_resume
                except Exception as e:
                    attempt += 1
                    msg = str(e).lower()
                    if ("429" in msg or "resource exhausted" in msg or "rate limit" in msg) and attempt < max_attempts:
                        import time
                        time.sleep(1 * (2 ** (attempt - 1)))
                        continue
                    raise
        except Exception as e:
            raise RuntimeError(f"Error parsing resume: {e}")
            