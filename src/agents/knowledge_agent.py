from google.adk import Agent
from src.core.vnpt_adk_model import VNPTADKModel
from src.tools.retrieval_tool import RetrievalTool

class KnowledgeAgent(Agent):
    def __init__(self):
        model = VNPTADKModel()
        retrieval_tool = RetrievalTool()
        
        instruction = """You are a Knowledge Agent. Your task is to answer questions based on context retrieved from the knowledge base.
You MUST use the 'retrieve_tool' tool to search for information before answering.
Do not answer from your own knowledge unless the tool returns no relevant information.
Always answer in Vietnamese.

Process:
1. Receive question.
2. Call 'retrieve_tool' with a relevant query.
3. Wait for the tool output.
4. Answer the question based on the tool output."""
        
        super().__init__(
            name="KnowledgeAgent",
            model=model,
            instruction=instruction,
            tools=[retrieval_tool]
        )
