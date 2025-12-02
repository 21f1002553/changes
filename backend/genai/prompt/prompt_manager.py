


class PromptManager:

    @staticmethod
    def get_structure_json_resume(resume_text):
        prompt = f"""
        You are an expert HR data extraction assistant.
        You will be provided with a resume and a job description.
        Your task is to extract the relevant information from the resume that is most relevant to the job description.
        The output should be a JSON object with the following structure:
        {{
            "location": "",
            "skills": [],
            "total_experience": "",
            "work_experience": [
                {{
                    "title": "",
                    "company": "",
                    "position": "",
                    "start_date": "",
                    "end_date": "",
                    "description": ""        
                }}
            ],
            "education": [
                {{
                    "degree": "",
                    "institute": "",
                    "field_of_study": "",
                    "start_date": "",
                    "end_date": "",
                }}
            ],
            "certifications": [],
            "projects": [],
            "interests": [],
        }}
        Rules:
        - The output should be a valid JSON object.
        - Calculate total_experience from start_date to end_date in work_experience.
        - If any fields are missing, leave it as empty.
        - Do not include extra text or summary.
        - Do not include any other information.

        Resume text: 
        ---
        {resume_text}
        ---
    """
        return prompt
    

    @staticmethod
    def performance_review_prompt(self_review, manager_review):
        prompt = f"""
        You are an expert performance review summarizer assistant.
        You will be provided with an employee self-assessment and a manager review.
        Your task is to summarize the employee's performance based on the self-assessment and manager review.
        Respond only in valid JSON and nothing else.
        If you cannot answer, return the JSON with empty fields or null.
        Return a JSON object exactly matching the schema below:

        Schema: 
        {{
            "Strengths": "",
            "Weaknesses": "",
            "Improvements": "",
            "Actionable_step: "",
            "Comments": ""
        }}

        Inputs:
        - Employee Self Review type: {self_review}
        - Manager Review: {manager_review}

        Rules:
        = Provide a summary of the employee's performance based on the self-assessment and manager review.
        - Provide a concise summary of strengths, weaknesses, and areas for improvement each in less than 20 words.
        - Actionable Steps should be specific and prioritized (e.g. "Take X Courses").
        - Comments should be a single sentence summary.
        - Output only in valid JSON
        
    """
        return prompt
    

    @staticmethod
    def mock_interview_prompt(job_title,job_description,job_requirements,n_easy_questions,n_medium_questions,n_hard_questions):
        prompt = f"""
        You are an expert AI assistant for interview tasks.
        Your Job is to provide tailored mock interviews for candidates based on the job description and requirements.
        Generate a structured mock interview for the role.
        Respond only in Valid JSON and nothing else.
        Each key maps to a list of questions with the following structure:

        {{
            "question": ""
        }}

        Inputs:
        - Job Title: {job_title}
        - Job Description: {job_description}
        - Job Requirements: {job_requirements}
        - Number of easy questions: {n_easy_questions}
        - Number of medium questions: {n_medium_questions}
        - Number of hard questions: {n_hard_questions}
        - Tone: Professional and Concise

        Rules:
        - Provide exactly the requested number of questions for each category.
        - Each question should be action-result formatted and containes keywords relevant to the job.
        - Keep each question and answer concise (questions <= 30 words).
        - Output only in valid JSON.
        
        """
        return prompt


    @staticmethod
    def course_recommendation_prompt(resume_text, job_title, courses):
        prompt = f"""
        You are an expert AI assistant for course recommendation tasks.
        You will be given a candidates resume and a job title and a list of courses with the id, title and duration minutes.
        Your Job is to identifying the skills gaps from the resume and job title and provide course recommendations to fill those gaps.
        You should explicity provide the reason behind taking that course.
        Return a JSON Object of course recommendations with the following structure:

        {{
            "Course_title":"",
            "reason":""
        }}

        Inputs:
        - Resume text: {resume_text}
        - Job Title: {job_title}
        - Courses: {courses}
        - Tone: Professional and Concise

        Rules:
        - Provide course recommendations based on the resume and job title.
        - Provide up to 1-2 course recommendations.
        - Each course recommendation should be action-result formatted and containes keywords relevant to the job.
        - Return only in valid JSON
        
        """
        return prompt
    

    @staticmethod
    def skill_gap_suggest_upskill_prompt(resume_text, job_description, job_title, courses):
        prompt = f"""
        You are an expert carrer coach.
        Your Job is to compare the candidate and target Job and suggest ways to upskill the candidate to match the job.
        You will be given course details which includes the course title, course duration and course description.
        You need to specify the missing skills and upskill path by looking at job details and resume.
        You have to specify the steps and and the course id, estimated hours like how much time will a person take to complete the course and hour of the course.
        You need to specify the reason why an individual should take that course.
        Your tone should be professional and concise, no need to exagerrate the information just summarize like 1 liner reason.
        Respond only in Valid Json and Structure should match with the Schema provided below.
        If you cannot answer, return the JSON with empty fields or null.
        If you do not find any course related to missing skills, return the course_upskilling_path as empty.
        Return JSON Object should be name as Upskilling Path with the following structure:

        Schema: 
        {{
            "missing_skill":[],
            "course_upskilling_path": [
                {{  
                    "course_id": "",
                    "step": "",
                    "course_title": "",
                    "estimated_time": "",
                    "reason:""
                }}            
            ]
        }}
        
        Inputs:
        - Resume: {resume_text}
        - Job Title: {job_title}
        = Job Description: {job_description}
        - Courses: {courses}
        

        Rules:
        - missing_skills: list the key skills absent for the role.
        - upskilling_path: provide up to 3-4 steps to upskill, each with estimated hours and one line reason.
        - Output only in valid JSON.
        - Keep the entries concise.
        """
        return prompt


    @staticmethod
    def tailor_resume_prompt(resume_text, target_jobs):
        prompt = f"""
        You are an expert AI assistant for resume tailoring tasks.
        You will be given a candidates resume text, and a job details and your task is to analyze the resume and suggest ways to optimize it to match the job details.
        Provide a short reason for the changes.
        Your job is to analyze the mistakes, which can be in any section of the resume whether it is work exp, education, skills, summary, etc.
        Find analyze each and every section, identify the mistakes and provide the suggested changes and give the reason for the changes.
        The output should be valid JSON and inside it each list or dict should be section wise, for example:
        Respond only in Valid JSON and nothing else.
        If you cannot answer, return the JSON with empty fields or null.
        If you do not find any mistakes, return the JSON with empty fields or null and just say that there are no mistakes, you are good to go.
        The output should be a JSON object with the following structure:

        {{
            "section": "",
            "mistakes": [],
            "suggested_change": [],
            "reasons": "" # short reasons for the changes
        }}

        Inputs:
        - Resume text: {resume_text}
        - Target Jobs: {target_jobs}
        - Tone: professional and concise

        Rules:
        - Analyze the resume text and provide the mistakes and provide the suggested changes.
        - Provide up to 5-6 suggestions; each bullet should be action-result formatted and containes keywords relevant to the target job.
        - reason: provide up to 3-4 short explanation for the changes.
        - Output only in valid JSON.

        """
        return prompt
    

    @staticmethod
    def resume_shortlisting_prompt(resume_text, job_title, job_description, job_requirements):
        prompt = f"""
        You are an expert AI assistant for resume shortlisting tasks.
        You will be given a collection of resumes with the id, text and metadata that is return from embeddings and similarity search.
        Inside resume text which contains the candidate's resume in which it has id that is resume_id, there will be text which is resume text, and inside metadata there are user_id.
        Inside that there will be a distance which means how much the resume is similar to the job description less the distance more similar.

        You will also be given job title, job description and job requirements.
        Your job is to score (0-100) the candidate's resume based on the job details that has been provided you and provide a short explanation for the score and provide the key metrics which includes some highlights such as (5+ years of experience or 5+ projects or valuable skills).
        Your job is to return in JSON object with each and every candidate given in the input, you have to return all the candidate in similar kind of JSON object.
        Return a JSON Object with the following structure and respond only in respective Schema that is provided below:

        Schema: 
        {{
            "score": "",
            "key_metrics:[],
            "reason": [],
            "resume_id:"",
            "user_id":""
        }}

        Inputs:
        - Resume text: {resume_text}
        - Job Title: {job_title}
        - Job Description: {job_description}
        - Job Requirements: {job_requirements}
        - Tone: Professional and Concise

        Rules:
        - Provide a short explanation for the score and provide the key metrics which includes some highlights such as (5+ years of experience or 5+ projects or valuable skills).
        - Output only in valid JSON

        
    """
        
        return prompt
    
    @staticmethod
    def job_description_generation_prompt(job_title, level, location):
        prompt = f"""
        You are an expert HR assistant specialized in creating comprehensive job descriptions.
        Your task is to generate a professional and detailed job description based on the provided information.
        
        Respond only in valid JSON format with the following structure:
        {{
            "title": "",
            "description": "",
            "key_responsibilities": [],
            "required_qualifications": [],
            "preferred_qualifications": [],
            "skills_required": [],
            "benefits": [],
            "employment_type": "",
            "experience_level": ""
        }}

        Inputs:
        - Job Title: {job_title}
        - Level: {level}
        - Location: {location}

        Rules:
        - Create a comprehensive job description that is professional and engaging
        - Include 5-7 key responsibilities that are specific and actionable
        - List 4-6 required qualifications including education and experience
        - Include 3-4 preferred qualifications that would be nice to have
        - List 6-8 relevant technical and soft skills
        - Include 4-5 standard benefits
        - Determine appropriate employment_type (full-time, part-time, contract)
        - Set experience_level based on the level provided (entry, mid, senior)
        - Keep descriptions clear, concise, and professional
        - Output only in valid JSON format
        """
        return prompt


    @staticmethod
    def make_JD_prompt(job_title):
        prompt = f"""
        You are an expert HR for making Job Descriptions based on Job title.
        Write concise, clear, and attractive job description for the job title provided.
        Follow this section order and heading exactly:
        
        - Job title
        - Company
        - Location
        - About Us
        - Job Summary
        - Responsibilities
        - Qualifications
        
        Inputs: {job_title}

        Rules:
        - Keep paragraphs tight and scannable.
        - Use bullet points where appropriate.
        - If a field is missing, infer practical defaults without hallucinating facts.
        - Keep length between 250–500 words unless instructed otherwise.
        
    """
        
        return prompt


    @staticmethod
    def example_prompt():
        example = [{
            "input": """Job Title: Robotics Instructor
                Company: SE Team 18 Company
                Location: Chennai, Tamil Nadu
                Notes: After-school programs; kits include LEGO Mindstorms, VEX, Arduino; audience 8–16 years""",
                
                "output": """### Job Title
                Robotics Instructor

                ### Company
                SE Team 18 Company

                ### Location
                Chennai, Tamil Nadu

                ### About Us
                SE Team 18 is a leading provider of STEM education, inspiring future engineers, programmers, and scientists through hands-on learning in robotics.

                ### Job Summary
                We seek a passionate, energetic instructor to lead after-school programs and workshops for students aged 8–16. You’ll deliver our curriculum, guide robot builds, and foster a collaborative, creative classroom.

                ### Key Responsibilities
                - Deliver engaging robotics lessons for ages 8–16.
                - Help students assemble, program, and troubleshoot robots using LEGO Mindstorms, VEX, or Arduino.
                - Manage classroom dynamics to ensure a safe, positive, productive environment.
                - Prepare and maintain materials, equipment, and robotics kits.
                - Offer constructive feedback to build problem-solving skills.

                ### Qualifications
                - Strong interest/basic knowledge in robotics, electronics, or programming.
                - Experience with children or educational settings preferred.
                - Excellent communication and interpersonal skills.
                - Ability to explain complex concepts simply.
                - Pursuing/completed a degree in Engineering, Computer Science, Education, or related field is a plus."""
            }]
        
        return example