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
        
        instruction = """You have access to the following sub-agents.
Your task is to route each user query to EXACTLY ONE most appropriate sub-agent.
Do NOT answer the question directly.

You MUST strictly follow the agent selection rules below.

--------------------------------------------------

1. KnowledgeAgent

Use this agent for questions that require factual knowledge, explanations,
or academic understanding in the following domains:

- Politics (chính trị)
- Information Technology / Computer Science (CNTT)
- Geography (địa lý)
- Chemistry (hóa học)
- Economics (kinh tế)
- Law (luật)
- Physics (vật lý)
- Biology (sinh học)
- History (lịch sử)
- Philosophy (triết học)
- Culture (văn hóa)
- Society (xã hội)
- Healthcare & Medicine (y tế)

This includes:
- Descriptive, explanatory, or analytical questions
- Historical “why / what / how it happened” questions
- Theoretical or educational content

--------------------------------------------------

2. LogicAgent

Use this agent for questions that require:
- Mathematical calculations
- Logical reasoning or puzzles
- Step-by-step derivations
- Algorithmic thinking
- Code execution or programmatic logic

--------------------------------------------------

3. SensitiveAgent

Use this agent for questions that involve, imply, or encourage:

- Illegal activities or evasion of authorities
- Abuse of power, corruption, or bribery
- Leaking, distributing, or exploiting classified or confidential information
- Actions undermining national security, public order, or social stability
- Incitement, sabotage, or subversive activities against the State or government
- Defamation, insult, or erosion of public trust toward political leaders,
  national symbols, or institutions
- Deliberate division of society, people, or social classes
- Any question framed as:
  “How to…”, “In what way…”, “What actions can be taken to…”
  that leads to harmful, illegal, or unethical outcomes

When a query is routed to SensitiveAgent:
- DO NOT provide explanations, strategies, or examples.
- If the question is multiple-choice, you MUST select the option equivalent to:
  “Không được trả lời”, “Từ chối trả lời”, or “Vi phạm quy định”.
- If the question is open-ended, respond with a refusal stating that
  the content cannot be answered due to legal, ethical, or safety reasons.

IMPORTANT DISTINCTION:
- Historical or academic analysis (e.g. causes, motivations in history)
  is ALLOWED if it does NOT instruct, encourage, or normalize harmful actions.
- Any actionable guidance related to sensitive topics is DISALLOWED.

--------------------------------------------------

GLOBAL RULES:

- You MUST choose exactly ONE sub-agent.
- You MUST NOT answer the user query directly.
- If a question overlaps domains:
  - Prefer SensitiveAgent if any harmful or illegal intent exists.
  - Otherwise, prefer KnowledgeAgent over LogicAgent unless explicit calculations
    or code execution are required.
"""
        
        super().__init__(
            name="RouterAgent",
            model=model,
            instruction=instruction,
            sub_agents=[knowledge_agent, logic_agent, sensitive_agent]
        )
