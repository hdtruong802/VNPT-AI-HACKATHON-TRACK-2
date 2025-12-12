from typing import AsyncGenerator, Any
from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.genai.types import Content, Part
from src.core.vnpt_client import VNPTClient
from src.core.config import Config
from pydantic import PrivateAttr
import asyncio

class VNPTADKModel(BaseLlm):
    model: str = Config.MODEL_SMALL
    _client: VNPTClient = PrivateAttr(default_factory=VNPTClient)
    print("VNPTADKModel(BaseLlm):", VNPTClient)
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        print("VNPTADKModel.generate_content_async called")
        
        # Convert ADK contents to VNPT messages format
        # Assuming llm_request.contents is a list of objects with role and parts
        messages = []
        if llm_request.contents:
            for content in llm_request.contents:
                # This part depends on ADK's Content structure. 
                # We'll try to extract text.
                role = "user"
                if hasattr(content, "role") and content.role:
                    role = content.role
                
                text = ""
                if hasattr(content, "parts"):
                    for part in content.parts:
                        if hasattr(part, "text"):
                            text += part.text
                
                # Adjust role mapping if necessary
                if role == "model":
                    role = "assistant"
                
                messages.append({"role": role, "content": text})
        
        # Call VNPT API
        # We run the synchronous client in a thread
        response_text = await asyncio.to_thread(
            self._client.chat_completion,
            messages=messages,
            model=self.model
        )
        
        if response_text:
            yield LlmResponse(content=Content(parts=[Part(text=response_text)], role="model"))
        else:
            yield LlmResponse(content=Content(parts=[Part(text="Error: No response from VNPT AI")], role="model"))

