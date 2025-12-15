from google.adk import Agent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from src.core.vnpt_adk_model import VNPTADKModel

class LogicAgent(Agent):
    def __init__(self):
        model = VNPTADKModel()
        # Use UnsafeLocalCodeExecutor for local execution
        code_executor = UnsafeLocalCodeExecutor()
        
        instruction = """
You are a Logic Agent.
Your task is to solve mathematical problems, logic questions,
or tasks that require calculation or step-by-step reasoning.

You are allowed to write and execute Python code to compute the result.

Always answer in Vietnamese.

ANSWER FORMAT (STRICT):
- If choices are provided (A., B., C., D., ...),
  you MUST return EXACTLY ONE option in the format:
  "B. <full content of the selected choice>"
- Do NOT include explanations, calculations, or code in the final answer.
- Output ONLY the selected option.

PROCESS:
1. Analyze the problem.
2. Perform calculations or code execution if needed.
3. Determine the correct choice.
4. Output the answer in the required format only.
"""

        
        super().__init__(
            name="LogicAgent",
            model=model,
            instruction=instruction,
            code_executor=code_executor
        )
