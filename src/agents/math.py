import json
import csv
import re
import sys
import os
from pathlib import Path

# Add parent directory to path to allow imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.llm import LLM
from utils.config_loader import load_config


# -----------------------
# Load config + LLM Large
# -----------------------
CONFIG = load_config(os.path.join(SRC_DIR, "config", "config.yaml"))
LLM_LARGE = LLM(CONFIG["models"]["llm_large"])

# -----------------------
# File paths
# -----------------------
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TEST_JSON = PROJECT_ROOT / "data" / "test.json"
CLASS_CSV = PROJECT_ROOT / "output" / "class_test.csv"
PRED_CSV = PROJECT_ROOT / "output" / "pred.csv"


# -----------------------
# Regex nhận diện toán phức tạp
# -----------------------
COMPLEX_PATTERN = re.compile(
    r"[\+\-\*/\^]{2,}|sqrt|log|sin|cos|tan|\(|\)|\d+\/\d+|\d+\s*\*\s*\d+",
    re.IGNORECASE
)

def is_complex_math(question: str) -> bool:
    return bool(COMPLEX_PATTERN.search(question))


# -----------------------
# Extract A/B/C/D robustly
# -----------------------
def extract_option(text: str) -> str:
    """
    Bắt chữ A/B/C/D xuất hiện ở bất kỳ chỗ nào.
    Tránh lỗi model trả 'Đáp án là C', 'C.', 'C )', v.v.
    """
    match = re.search(r"\b([A-D])\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "A"   # Fallback an toàn


# -----------------------
# Helper: call LLM Large
# -----------------------
def llm_call(messages):
    return LLM_LARGE(messages)


# -----------------------
# Solve math with CoT + Python Hybrid
# -----------------------
def solve_math_question(question: str, choices: list[str]) -> str:
    choices = choices[:4]

    if is_complex_math(question):
        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý giải toán dùng Python. "
                    "Nếu cần hãy viết mã Python để tính toán. "
                    "YÊU CẦU BẮT BUỘC: Cuối cùng chỉ trả về duy nhất một chữ cái "
                    "A/B/C/D, không thêm chữ nào khác."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Câu hỏi: {question}\n"
                    f"Các lựa chọn: {choices}\n"
                    "Hãy giải và cuối cùng chỉ trả về A/B/C/D, KHÔNG giải thích thêm."
                )
            },
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý giải toán tiếng Việt. "
                    "Hãy suy luận nếu cần, nhưng cuối cùng bắt buộc chỉ trả về "
                    "một chữ cái A/B/C/D duy nhất."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Câu hỏi: {question}\n"
                    f"Các lựa chọn: {choices}\n"
                    "Hãy đưa ra đáp án đúng và cuối cùng chỉ trả về A/B/C/D."
                )
            },
        ]

    output = llm_call(messages)
    ans = output.strip()
    return extract_option(ans)


# -----------------------
# Save preds immediately after each question
# -----------------------
def save_preds(preds: dict):
    sorted_qids = sorted(preds.keys())

    with open(PRED_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["qid", "answer"])
        for qid in sorted_qids:
            writer.writerow([qid, preds[qid]])


# -----------------------
# Main pipeline
# -----------------------
def main():

    # load label map
    label_map = {}
    with open(CLASS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label_map[row["qid"]] = row["label"]

    # load test set
    with open(TEST_JSON, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    # load existing predictions
    preds = {}
    if PRED_CSV.exists():
        with open(PRED_CSV, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                preds[row["qid"]] = row["answer"]

    # process math questions
    for item in test_data:
        qid = item["qid"]

        if label_map.get(qid) != "math":
            continue

        # resume-safe: skip if already predicted
        if qid in preds:
            print(f"[Skip] {qid} đã có trong pred.csv, bỏ qua.")
            continue

        print(f"[Math] Đang xử lý {qid} ...")

        ans = solve_math_question(item["question"], item["choices"])
        preds[qid] = ans

        # save immediately
        save_preds(preds)

    print("✔ Hoàn thành. Từng câu đã được lưu ngay vào Dev/output/pred.csv")


if __name__ == "__main__":
    main()
