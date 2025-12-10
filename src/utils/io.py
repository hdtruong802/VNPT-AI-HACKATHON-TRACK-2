# Hàm load JSON, ghi CSV
import json, csv, os

def load_json(path):
    path = os.path.join(os.path.dirname(__file__), "..", path)
    return json.load(open(path,"r",encoding="utf-8"))

def save_csv(path, rows:list):
    path = os.path.join(os.path.dirname(__file__), "..", path)
    with open(path,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["qid","label"])
        writer.writeheader()
        writer.writerows(rows)
