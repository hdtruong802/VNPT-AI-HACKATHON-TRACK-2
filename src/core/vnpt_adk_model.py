from typing import AsyncGenerator, Any, Dict
from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.genai.types import Content, Part, FunctionCall
from src.core.vnpt_client import VNPTClient
from src.core.config import Config
from pydantic import PrivateAttr
import asyncio
import json
import re

class VNPTADKModel(BaseLlm):
    _client: VNPTClient = PrivateAttr(default_factory=VNPTClient)
    model: str = Config.MODEL_SMALL

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        # print("VNPTADKModel.generate_content_async called")
        
        messages = []
        tools_instruction = ""
        
        # Handle Tools
        if llm_request.tools_dict:
            tools_instruction = "\nYou have access to the following tools:\n"
            for name, tool in llm_request.tools_dict.items():
                # Assuming tool has a description or we can inspect it
                # For FunctionTool, it wraps a function.
                # We'll try to get docstring or signature.
                sig = "unknown"
                doc = "No description"
                if hasattr(tool, "func"):
                    sig = tool.func.__name__
                    if tool.func.__doc__:
                        doc = tool.func.__doc__.strip()
                
                tools_instruction += f"- {name}: {doc}\n"
            
            tools_instruction += "\nTo use a tool, please respond with ONLY the following format:\n"
            tools_instruction += "ToolCall: <tool_name>(<arguments_json>)\n"
            tools_instruction += "Example: ToolCall: retrieve_context({\"query\": \"hello\"})\n"
        
        # Convert ADK contents to VNPT messages format
        if llm_request.contents:
            for i, content in enumerate(llm_request.contents):
                role = "user"
                if hasattr(content, "role") and content.role:
                    role = content.role
                
                text = ""
                if hasattr(content, "parts"):
                    for part in content.parts:
                        if hasattr(part, "text") and part.text:
                            text += part.text
                        # Handle FunctionCall in history (if any)
                        if hasattr(part, "function_call") and part.function_call:
                            # We represent function call as assistant message for history
                            text += f"ToolCall: {part.function_call.name}({json.dumps(part.function_call.args)})"
                        # Handle FunctionResponse in history
                        if hasattr(part, "function_response") and part.function_response:
                             role = "function" # VNPT might not support 'function' role, map to user or system?
                             # Let's map to user for now with a prefix
                             text += f"Tool Output: {json.dumps(part.function_response.response)}"

                # Adjust role mapping
                if role == "model":
                    role = "assistant"
                elif role == "function":
                    role = "user" # Fake function role as user
                
                # Inject tools instruction into the last user message or system message
                if i == len(llm_request.contents) - 1 and role == "user" and tools_instruction:
                    text += tools_instruction

                messages.append({"role": role, "content": text})
        
        # Call VNPT API
        response_text = await asyncio.to_thread(
            self._client.chat_completion,
            messages=messages,
            model=self.model
        )
        
        if response_text:
            # Check for ToolCall
            tool_call_match = re.search(r"ToolCall:\s*(\w+)\((.*)\)", response_text, re.DOTALL)
            if tool_call_match:
                tool_name = tool_call_match.group(1)
                args_str = tool_call_match.group(2)
                try:
                    args = json.loads(args_str)
                    # Return FunctionCall
                    fc = FunctionCall(name=tool_name, args=args)
                    yield LlmResponse(content=Content(parts=[Part(function_call=fc)], role="model"))
                    return
                except json.JSONDecodeError:
                    print(f"Failed to parse tool args: {args_str}")
            
            yield LlmResponse(content=Content(parts=[Part(text=response_text)], role="model"))
        else:
            yield LlmResponse(content=Content(parts=[Part(text="Error: No response from VNPT AI")], role="model"))
