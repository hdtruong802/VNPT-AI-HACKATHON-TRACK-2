from google.adk import Agent
from src.core.vnpt_adk_model import VNPTADKModel

class SensitiveAgent(Agent):
    def __init__(self):
        model = VNPTADKModel()
        
        instruction = """You are a Sensitive Agent. Your task is to handle questions that might be sensitive, illegal, or harmful.
You must politely refuse to answer any question that violates safety guidelines, asks for personal information, or promotes illegal activities.
If the question is safe but was misclassified, answer it normally.
Always answer in Vietnamese."""
        
        super().__init__(
            name="SensitiveAgent",
            model=model,
            instruction=instruction
        )
