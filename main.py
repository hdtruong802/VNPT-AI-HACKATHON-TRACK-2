import asyncio
import json
import pandas as pd
import os
import re
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from src.agents.router_agent import RouterAgent

def format_choices(choices):
    """Formats a list of choices into A. ... B. ... format."""
    formatted = ""
    for i, choice in enumerate(choices):
        letter = chr(65 + i)  # 65 is ASCII for 'A'
        formatted += f"{letter}. {choice}\n"
    return formatted

def extract_answer(text):
    """Extracts the selected answer letter (A, B, C, D...) from the text."""
    # Priority 1: Look for "Answer: X" or "Đáp án: X"
    # match = re.search(r"(?:Answer|Đáp án)[:\s\-\*]+([A-J])", text, re.IGNORECASE)
    # if match:
    #     return match.group(1).upper()
        
    # Priority 2: Look for "X. " at the start of the text
    match = re.search(r"^([A-J])[\.\)\:]\s", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
        
    # # Priority 3: Look for "**X**" or similar isolated patterns if strictly asked
    # match = re.search(r"(?:^|\s)\*\*([A-J])\*\*(?:$|\s|\.)", text, re.IGNORECASE)
    # if match:
    #     return match.group(1).upper()

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
        print(f"Error in agent execution: {e}")
        return "Error processing request."

    return response_text

async def main():
    # Load data
    input_file = "data/4sample.json"
    if not os.path.exists(input_file):
        print(f"File {input_file} not found. Creating dummy data for testing.")
        # Create dummy data if not exists (or use sample.json if user prefers)
        dummy_data = [
            {"qid": "test_001", "question": "Thủ đô của Việt Nam là gì?", "choices": ["Hà Nội", "HCM", "Đà Nẵng", "Huế"]},
            {"qid": "test_002", "question": "Tính tổng 1 + 1", "choices": ["1", "2", "3", "4"]}
        ]
        with open(input_file, "w") as f:
            json.dump(dummy_data, f, ensure_ascii=False, indent=2)
        data = dummy_data
    else:
        with open(input_file, "r") as f:
            data = json.load(f)
    
    # Initialize Router Agent (Coordinator)
    router_agent = RouterAgent()
    
    results = []
    
    print(f"Processing {len(data)} questions...")
    
    for item in data:
        qid = item.get('qid', 'unknown')
        question = item.get('question', '')
        choices = item.get('choices', [])
        
        full_question = question
        if choices:
            formatted_choices = format_choices(choices)
            full_question += f"\n\nChoices:\n{formatted_choices}\n\nIMPORTANT: Start your answer with the selected letter (e.g., 'A.')."

        print(f"Processing {qid}...")
        
        try:
            # Run Router Agent
            raw_answer = await get_agent_response(router_agent, full_question, f"session_router_{qid}")
            
            print(f"  Raw Answer: {raw_answer[:100]}...")
            
            final_answer = raw_answer
            if choices:
                extracted = extract_answer(raw_answer)
                if extracted:
                    final_answer = extracted
                    print(f"  Extracted Answer: {final_answer}")
                else:
                    print(f"  Could not extract answer from: {raw_answer[:50]}...")
            
            results.append({
                "qid": qid,
                "answer": final_answer
            })
        except Exception as e:
            print(f"Error processing {qid}: {e}")
            results.append({
                "qid": qid,
                "answer": "C" # Default to C if extraction fails
            })
        
    # Save results
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv("output/pred.csv", index=False)
    print("Results saved to output/pred.csv")

if __name__ == "__main__":
    asyncio.run(main())
