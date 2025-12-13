import requests
import time


class LLM:
    """Wrapper class for LLM API calls."""
    
    def __init__(self, config: dict):
        """
        Initialize LLM with configuration.
        
        Args:
            config: Dictionary containing endpoint, model, authorization, token_id, token_key, etc.
        """
        self.config = config
        self.endpoint = config["endpoint"]
        self.model = config["model"]
        self.headers = {
            "Authorization": config["authorization"],
            "token-id": config["token_id"],
            "token-key": config["token_key"],
            "Content-Type": "application/json"
        }
    
    def __call__(self, messages, temperature=None, max_tokens=None):
        """
        Make API call to LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys, 
                     or a single string (which will be converted to user message)
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            Response text from the LLM
        """
        # Handle string input (backwards compatibility)
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Build payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.get("temperature", 0.2),
            "max_tokens": max_tokens if max_tokens is not None else self.config.get("max_tokens", 512)
        }
        
        # Add optional parameters if present in config
        if "top_p" in self.config:
            payload["top_p"] = self.config["top_p"]
        if "top_k" in self.config:
            payload["top_k"] = self.config["top_k"]
        
        # Retry logic
        for retry in range(1, 6):
            try:
                r = requests.post(self.endpoint, json=payload, headers=self.headers)
                data = r.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                    
            except Exception as e:
                if retry < 5:
                    time.sleep(2 * retry)
                    continue
                else:
                    raise Exception(f"LLM API call failed after 5 retries: {e}")
        
        raise Exception("LLM API call failed: No valid response received")
