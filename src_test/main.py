# Load test.json -> xử lý batch -> ghi kết quả realtime CSV
from utils.io import load_json
from router_agent import Router
import csv, os

OUTPUT = "../output/class_1.csv"

def run():
    data = load_json("../data/val.json")
    router = Router()

    if not os.path.exists(OUTPUT):
        with open(OUTPUT, "w", encoding="utf-8") as f:
            f.write("qid,label\n")

    # mở file append mode
    with open(OUTPUT, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        total = len(data)
        for idx, item in enumerate(data, 1):
            label = router.classify_single(item)
            writer.writerow([item["qid"], label])
            print(f"✔ {idx}/{total} → qid: {item['qid']} | label: {label}")

    print("FINISHED → file:", OUTPUT)

if __name__=="__main__":
    run()
