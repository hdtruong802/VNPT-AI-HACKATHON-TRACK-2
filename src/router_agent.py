# Agent phân loại câu hỏi → routing sang module xử lý phù hợp
import requests, yaml, time, re

class Router:
    def __init__(self, config_path="config/config.yaml"):
        self.config = yaml.safe_load(open(config_path,"r",encoding="utf-8"))
        self.cfg = self.config["models"]["llm_small"]

        # keyword reading
        self.reading_keywords = ["Đoạn thông tin:", "Tiêu đề:", "Nội dung:", "Câu hỏi:"]
        # keyword sensitive
        self.sensitive_keywords = [
            "tránh tuân thủ", "cấm", "bạo lực", "vũ khí", 
            "hướng dẫn phạm pháp", "tự sát", "tấn công", "thông tin nhạy cảm"
        ]

        # regex math context-aware: keyword + số / phép toán / ký hiệu
        self.math_pattern = re.compile(
            r"(tính|tìm|đổi|tổng|hiệu|tương đương|phần trăm|lấy|tính toán).*(\d+|[\+\-\*/=]|R\d+|%|\$)"
        )

        # regex công thức nhưng không yêu cầu tính toán → knowledge fallback
        self.formula_pattern = re.compile(r"\$|\d+[\+\-\*/=]|\w+\(\d+\)")

    def build_prompt(self, question, qid):
        text = f"""Phân loại câu hỏi sau theo 3 nhãn (knowledge, math, sensitive):
- knowledge : kiến thức, lịch sử, địa lý, văn hóa, chính trị/tôn giáo không nhạy cảm
- math      : các câu thực sự yêu cầu tính toán
- sensitive : nội dung nhạy cảm, cấm

Câu hỏi: {question}

Trả về theo format: label
"""
        return text

    def classify_single(self, item):
        question_lower = item["question"].strip().lower()

        # 1. Reading
        if any(k.lower() in question_lower for k in self.reading_keywords):
            return "reading"

        # 2. Sensitive
        if any(k in question_lower for k in self.sensitive_keywords):
            return "sensitive"

        # 3. Math → chỉ khi match regex context-aware
        if self.math_pattern.search(question_lower):
            return "math"

        # 4. Công thức nhưng không tính toán → knowledge
        if self.formula_pattern.search(question_lower):
            return "knowledge"

        # 5. Gọi LLM để phân loại knowledge/math/sensitive
        payload = {
            "model": self.cfg["model"],
            "messages":[{"role":"user","content": self.build_prompt(item["question"], item["qid"])}],
            "temperature": 0,
            "max_tokens": 50
        }

        headers = {
            "Authorization": self.cfg["authorization"],
            "token-id": self.cfg["token_id"],
            "token-key": self.cfg["token_key"],
            "Content-Type": "application/json"
        }

        for retry in range(1,6):
            r = requests.post(self.cfg["endpoint"], json=payload, headers=headers)

            try:
                data = r.json()
            except:
                time.sleep(3*retry)
                continue

            if "error" in data and "limit" in data["error"]:
                wait = 8 + retry*6
                print(f"⏳ RATE LIMIT — nghỉ {wait}s rồi retry {retry}/5 ...")
                time.sleep(wait)
                continue

            if "choices" in data:
                text = data["choices"][0]["message"]["content"].strip().lower()
                if text not in ["knowledge","math","sensitive"]:
                    text = "knowledge"
                return text

            time.sleep(3*retry)

        # fallback
        return "knowledge"

    def classify_batch(self, items, batch_id=0):
        out = {}
        for it in items:
            out[it["qid"]] = self.classify_single(it)
        return out
