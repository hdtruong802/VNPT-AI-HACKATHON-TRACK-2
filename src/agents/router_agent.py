from google.adk import Agent
from src.core.vnpt_adk_model import VNPTADKModel
from src.core.config import Config

class RouterAgent(Agent):
    def __init__(self):
        model = VNPTADKModel()
        instruction = """You are a router agent. Your task is to classify the user's question into one of the following categories:
- KNOWLEDGE: Questions about general knowledge, history, culture, geography, politics, etc.
- LOGIC: Questions involving math, logic puzzles, calculations.
- SENSITIVE: Questions that might be sensitive, asking for personal info, or illegal acts.

Return ONLY the category name (KNOWLEDGE, LOGIC, or SENSITIVE). Do not add any explanation."""
        
        super().__init__(
            name="RouterAgent",
            model=model,
            instruction=instruction
        )
