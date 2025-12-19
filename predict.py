import asyncio
import json
import pandas as pd
import os
import re
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from src.agents.router_agent import RouterAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def format_choices(choices):
    """Formats a list of choices into A. ... B. ... format."""
    formatted = ""
    for i, choice in enumerate(choices):
        letter = chr(65 + i)  # 65 is ASCII for 'A'
        formatted += f"{letter}. {choice}\n"
    return formatted

def extract_answer(text):
    """Extracts the selected answer letter (A, B, C, D...) from the text."""
    # Priority 2: Look for "X. " at the start of the text
    match = re.search(r"^([A-J])[\.\)\:]\s", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

async def get_agent_response(agent, question, session_id, user_id="user"):
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="agents")
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name="agents")
    
    content = Content(parts=[Part(text=question)], role="user")
    response_text = ""
    
    try:
        # We use synchronous iteration as per previous finding
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=content):
            if hasattr(event, "content") and event.content:
                 if isinstance(event.content, str):
                     response_text += event.content
                 elif hasattr(event.content, "parts"):
                     for part in event.content.parts:
                         if hasattr(part, "text") and part.text:
                             response_text += part.text
    except Exception as e:
        logger.error(f"Error in agent execution: {e}")
        return "Error processing request."

    return response_text

async def main():
    # Define input/output paths
    # /code/private_test.json is the standard path for submission
    # Fallback to data/test.json for local testing
    input_file = "/code/private_test.json"
    if not os.path.exists(input_file):
        input_file = "data/test.json"
        logger.info(f"private_test.json not found, using {input_file}")
    
    if not os.path.exists(input_file):
        logger.error(f"Input file {input_file} not found.")
        return

    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return
    
    # Initialize Router Agent (Coordinator)
    try:
        router_agent = RouterAgent()
    except Exception as e:
        logger.error(f"Error initializing RouterAgent: {e}")
        return
    
    results = []
    
    logger.info(f"Processing {len(data)} questions...")
    
    for item in data:
        qid = item.get('id', item.get('qid', 'unknown')) # Handle both 'id' and 'qid'
        question = item.get('question', '')
        choices = item.get('choices', [])
        
        full_question = question
        if choices:
            formatted_choices = format_choices(choices)
            full_question += f"\n\nChoices:\n{formatted_choices}\n\nIMPORTANT: Start your answer with the selected letter (e.g., 'A.')."

        logger.info(f"Processing {qid}...")
        
        try:
            # Run Router Agent
            raw_answer = await get_agent_response(router_agent, full_question, f"session_router_{qid}")
            
            final_answer = raw_answer
            if choices:
                extracted = extract_answer(raw_answer)
                if extracted:
                    final_answer = extracted
                else:
                    logger.warning(f"  Could not extract answer from: {raw_answer[:50]}...")
                    final_answer = "C" # Default fallback

            if final_answer == "":
                final_answer = "C"

            results.append({
                "id": qid,
                "answer": final_answer
            })
        except Exception as e:
            logger.error(f"Error processing {qid}: {e}")
            results.append({
                "id": qid,
                "answer": "C"
            })
        
    # Save results to submission.csv
    try:
        df = pd.DataFrame(results)
        df.to_csv("submission.csv", index=False)
        logger.info("Results saved to submission.csv")
    except Exception as e:
        logger.error(f"Error saving results: {e}")

if __name__ == "__main__":
    asyncio.run(main())
