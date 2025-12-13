import csv
import json
import os

# Lấy root folder của project để chạy ở mọi vị trí
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# ===== PATH =====
PATH_CLASS = os.path.join(ROOT, "output/class_test.csv")
PATH_TEST = os.path.join(ROOT, "data/test.json")
PATH_PRED = os.path.join(ROOT, "output/pred.csv")

def run_sensitive_filter():

    # ===== Bước 1: Đọc file class_test.csv =====
    label_map = {}  # qid -> label
    with open(PATH_CLASS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label_map[row["qid"]] = row["label"]

    # ===== Bước 2: Đọc file test.json =====
    with open(PATH_TEST, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    # ===== Bước 3: Chọn câu sensitive và tìm đáp án =====
    results = []
    TARGET = "tôi không thể"

    choice_labels = ["A", "B", "C", "D"]

    for item in test_data:
        qid = item["qid"]

        # Chỉ xử lý sensitive
        if label_map.get(qid) != "sensitive":
            continue

        choices = item["choices"]
        answer_letter = None

        for i, text in enumerate(choices):
            if TARGET in text.lower():
                answer_letter = choice_labels[i]
                break

        results.append({"qid": qid, "answer": answer_letter})

    # ===== Bước 4: Ghi file pred.csv =====
    with open(PATH_PRED, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "answer"])
        writer.writeheader()
        writer.writerows(results)

    print(f"✔ Sensitive xử lý xong → ghi vào: {PATH_PRED}")


if __name__ == "__main__":
    run_sensitive_filter()
