from google.adk.tools.function_tool import FunctionTool
from src.agents.logic_agent import LogicAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import asyncio

class LogicTool(FunctionTool):
    def __init__(self):
        self.agent = LogicAgent()
        self.session_service = InMemorySessionService()
        self.runner = Runner(agent=self.agent, session_service=self.session_service, app_name="logic_tool")
        
        super().__init__(func=self.solve_logic_problem)

    def solve_logic_problem(self, question: str) -> str:
        """
        Solves a logic or math problem using the Logic Agent.
        
        Args:
            question: The logic or math question to solve.
            
        Returns:
            The answer provided by the Logic Agent.
        """
        # Since tools are synchronous in this framework (based on RetrievalTool), 
        # but Runner is async, we might need to run it in a new event loop or use existing one.
        # However, calling async from sync is tricky.
        # Let's check how RetrievalTool works - it calls sync APIs (requests).
        # LogicAgent uses VNPTADKModel which uses async generate.
        
        # If we are already in an async loop (which we are), we can't use asyncio.run().
        # We should try to find a way to run it.
        
        # OPTION 1: Use a helper to run async in sync
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We are in a loop. We can't block it.
            # But FunctionTool expects a sync return?
            # If ADK supports async tools, we should use async def.
            # Let's try defining it as async first.
            return "Error: Async tool execution not fully supported in this context yet."
        else:
             return asyncio.run(self._run_agent(question))

    # Let's try to make the tool function async if ADK supports it.
    # Looking at base_llm.py or similar might reveal if async tools are supported.
    # For now, I will implement a sync wrapper that assumes it can run async code 
    # or I'll implement it as async and hope ADK handles it.
    
    # Actually, let's look at how I can reuse the LogicAgent logic without the full Runner overhead if possible,
    # OR just implement it as an async method.
    
    async def solve_logic_problem_async(self, question: str) -> str:
        session_id = "logic_tool_session"
        await self.session_service.create_session(session_id=session_id, user_id="tool_user", app_name="logic_tool")
        
        content = Content(parts=[Part(text=question)], role="user")
        response_text = ""
        
        async for event in self.runner.run_async(user_id="tool_user", session_id=session_id, new_message=content):
            if hasattr(event, "content") and event.content:
                if isinstance(event.content, str):
                    response_text += event.content
                elif hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text
        # print(f"[LogicTool]: {response_text}")                   
        return response_text

    def solve_logic_problem(self, question: str) -> str:
        """
        Solves a logic or math problem using the Logic Agent.
        
        Args:
            question: The logic or math question to solve.
            
        Returns:
            The answer provided by the Logic Agent.
        """
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(self.solve_logic_problem_async(question))

