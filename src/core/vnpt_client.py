import requests
import json
import time
from typing import List, Dict, Any, Optional
from src.core.config import Config

class VNPTClient:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {Config.VNPT_API_KEY}',
            'Token-id': Config.VNPT_TOKEN_ID,
            'Token-key': Config.VNPT_TOKEN_KEY,
            'Content-Type': 'application/json',
        }

    def chat_completion(self, messages: List[Dict[str, str]], model: str = Config.MODEL_SMALL, 
                        temperature: float = 1.0, top_p: float = 1.0, top_k: int = 20, 
                        max_tokens: int = 512) -> Optional[str]:
        
        # URL uses hyphens, Payload uses underscores
        url = f"{Config.API_BASE_URL}/{model.replace('_', '-')}"
        # url = f"{Config.API_BASE_URL}/{model}"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "n": 1,
            "max_completion_tokens": max_tokens
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)

            # In method và URL
            print("=== REQUEST ===")
            print(response.request.method, response.request.url)

            # In headers
            print("\n--- Headers ---")
            for k, v in response.request.headers.items():
                print(f"{k}: {v}")

            # In body
            print("\n--- Body ---")
            print(response.request.body)


            response.raise_for_status()
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            return None
        except Exception as e:
            print(f"Error calling VNPT Chat API: {e}")
            if response:
                print(f"Response content: {response.text}")
            return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        url = Config.EMBEDDING_URL
        
        payload = {
            "model": Config.MODEL_EMBEDDING,
            "input": text,
            "encoding_format": "float"
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0]['embedding']
            return None
        except Exception as e:
            print(f"Error calling VNPT Embedding API: {e}")
            if response:
                print(f"Response content: {response.text}")
            return None
