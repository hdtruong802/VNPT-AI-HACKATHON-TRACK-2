import asyncio
import json
import pandas as pd
import os
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from src.agents.router_agent import RouterAgent

async def get_agent_response(agent, question, session_id, user_id="user"):
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="pipeline")
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name="pipeline")
    
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
            {"qid": "test_001", "question": "Thủ đô của Việt Nam là gì?", "choices": []},
            {"qid": "test_002", "question": "Tính tổng 1 + 1", "choices": []}
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
        
        if choices:
            question += f"\nChoices: {choices}"

        print(f"Processing {qid}...")
        
        try:
            # Run Router Agent
            answer = await get_agent_response(router_agent, question, f"session_router_{qid}")
            
            print(f"  Answer: {answer[:100]}...")
            
            results.append({
                "qid": qid,
                "answer": answer
            })
        except Exception as e:
            print(f"Error processing {qid}: {e}")
            results.append({
                "qid": qid,
                "answer": "Error"
            })
        
    # Save results
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv("output/pred.csv", index=False)
    print("Results saved to output/pred.csv")

if __name__ == "__main__":
    asyncio.run(main())
