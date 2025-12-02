from ..prompt import PromptManager
from ..llm_factory import LLMModelFactory
from utils import TextUtility


class AIPerformanceReview:
    def __init__(self, model_name: str = 'gemini'):
        self.model_name = model_name

    def generate_performance_review(self, employee_review, manager_view):

        if not employee_review or not manager_view:
            raise ValueError("Employee review and manager view are required")
        
        # load the prompt
        prompt=PromptManager.performance_review_prompt(employee_review, manager_view)

        # Load Model
        model=LLMModelFactory.get_model_provider(self.model_name).get_model()
        try:
            response=model.generate_content(prompt)
            if not response or not response.text:
                raise ValueError("No response from LLM")
        except Exception as e:
            raise RuntimeError(f"Failed to generate performance review: {e}")
        
        output = TextUtility.remove_json_marker(response.text)
        return output
        