# Load test.json -> run pipeline -> ghi pred.csv

from src.utils.io import load_questions, write_csv
from src.router_agent import RouterAgent
from src.answer_selector_agent import AnswerSelectorAgent

def run():
    questions = load_questions("data/val.json")
    router = RouterAgent()
    selector = AnswerSelectorAgent()
    results = []

    for q in questions:
        agent = router.route(q["question"])   # → KNOWLEDGE / MATH / READING / SENSITIVE
        answer = agent.solve(q)               # agent reasoning và trả lại index hoặc None
        final_ans = selector.select(answer)   # Convert 0→A,1→B,2→C,3→D

        results.append({
            "qid": q["qid"],
            "answer": final_ans                # Nếu sensitive → final_ans = ""
        })

    write_csv("output/pred.csv", results)

if __name__ == "__main__":
    run()
