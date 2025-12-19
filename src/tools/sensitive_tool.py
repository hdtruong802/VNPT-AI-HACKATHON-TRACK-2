from google.adk.tools.function_tool import FunctionTool
from src.agents.sensitive_agent import SensitiveAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import asyncio

class SensitiveTool(FunctionTool):
    def __init__(self):
        self.agent = SensitiveAgent()
        self.session_service = InMemorySessionService()
        self.runner = Runner(agent=self.agent, session_service=self.session_service, app_name="sensitive_tool")
        
        super().__init__(func=self.handle_sensitive_question)

    def handle_sensitive_question(self, question: str) -> str:
        """
        Handles a potentially sensitive or harmful question using the Sensitive Agent.
        
        Args:
            question: The question to handle.
            
        Returns:
            The response provided by the Sensitive Agent (usually a refusal or safe answer).
        """
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(self._run_agent(question))

    async def _run_agent(self, question: str) -> str:
        session_id = "sensitive_tool_session"
        await self.session_service.create_session(session_id=session_id, user_id="tool_user", app_name="sensitive_tool")
        
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
                            
        print(f"[SensitiveTool]: {response_text}")
        return response_text
