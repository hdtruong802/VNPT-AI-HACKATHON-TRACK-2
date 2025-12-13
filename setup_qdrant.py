from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.core.config import Config

def setup_qdrant():
    client = QdrantClient(url=Config.QDRANT_URL)
    collection_name = "vnpt_hackathon_knowledge"
    
    # Check if collection exists
    collections = client.get_collections()
    exists = any(c.name == collection_name for c in collections.collections)
    
    if exists:
        print(f"Collection '{collection_name}' already exists. Recreating...")
        client.delete_collection(collection_name=collection_name)
    
    print(f"Creating collection '{collection_name}' with dim=1024...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
    )
    print("Collection created successfully.")

    # Add some dummy data for testing
    print("Adding dummy data...")
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=1,
                vector=[0.1] * 1024,
                payload={"text": "Account discord của Nam tên là Quỳnh Sơn Ca"}
            ),
            models.PointStruct(
                id=2,
                vector=[0.2] * 1024,
                payload={"text": "Công nghiệp văn hóa đóng góp quan trọng vào kinh tế."}
            )
        ]
    )
    print("Dummy data added.")

if __name__ == "__main__":
    setup_qdrant()
