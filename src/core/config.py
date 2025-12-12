import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    VNPT_API_KEY = os.getenv("VNPT_API_KEY")
    VNPT_TOKEN_ID = os.getenv("VNPT_TOKEN_ID")
    VNPT_TOKEN_KEY = os.getenv("VNPT_TOKEN_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Model names
    MODEL_SMALL = "vnptai_hackathon_small"
    MODEL_LARGE = "vnptai_hackathon_large"
    MODEL_EMBEDDING = "vnptai_hackathon_embedding"
    
    # API Base URL
    API_BASE_URL = "https://api.idg.vnpt.vn/data-service/v1/chat/completions"
    EMBEDDING_URL = "https://api.idg.vnpt.vn/data-service/vnptai-hackathon-embedding"
