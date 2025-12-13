from google.adk import Agent
from src.core.vnpt_adk_model import VNPTADKModel
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.logic_agent import LogicAgent
from src.agents.sensitive_agent import SensitiveAgent

class RouterAgent(Agent):
    def __init__(self):
        model = VNPTADKModel()
        
        # Initialize sub-agents
        knowledge_agent = KnowledgeAgent()
        logic_agent = LogicAgent()
        sensitive_agent = SensitiveAgent()
        
        instruction = """You are a Router Agent. Your goal is to help the user by delegating their request to the most appropriate specialist agent.

You have access to the following sub-agents:
- KnowledgeAgent: For questions about general knowledge, history, culture, geography, politics, etc.
- LogicAgent: For questions involving math, logic puzzles, calculations, or code execution.
- SensitiveAgent: For questions that might be sensitive, harmful, or asking for personal info.

Rules:
1. Analyze the user's request carefully.
2. Delegate the task to the most suitable sub-agent.
3. If the request is ambiguous, default to KnowledgeAgent.
4. Do not try to answer the question yourself if a sub-agent is better suited."""
        
        super().__init__(
            name="RouterAgent",
            model=model,
            instruction=instruction,
            sub_agents=[knowledge_agent, logic_agent, sensitive_agent]
        )
