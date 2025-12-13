from google.adk import Agent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from src.core.vnpt_adk_model import VNPTADKModel

class LogicAgent(Agent):
    def __init__(self):
        model = VNPTADKModel()
        # Use UnsafeLocalCodeExecutor for local execution
        code_executor = UnsafeLocalCodeExecutor()
        
        instruction = """You are a Logic Agent. Your task is to solve logic puzzles, math problems, and computational tasks.
You should write Python code to solve the problem.
Wrap your code in a code block like this:
```python
print("Hello")
```
The code will be executed and the output will be returned to you.
Use the code output to formulate your final answer.
Always answer in Vietnamese."""
        
        super().__init__(
            name="LogicAgent",
            model=model,
            instruction=instruction,
            code_executor=code_executor
        )
