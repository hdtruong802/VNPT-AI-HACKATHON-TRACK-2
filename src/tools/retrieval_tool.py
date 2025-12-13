from google.adk.tools.function_tool import FunctionTool
from qdrant_client import QdrantClient
from src.core.config import Config
from src.core.vnpt_client import VNPTClient

class RetrievalTool(FunctionTool):
    def __init__(self):
        self.qdrant_client = QdrantClient(url=Config.QDRANT_URL)
        self.vnpt_client = VNPTClient()
        self.collection_name = "vnpt_hackathon_knowledge"
        # self.collection_name = "vnpt_hackathon_knowledge2"
        
        super().__init__(func=self.retrieve_context)

    def retrieve_context(self, query: str) -> str:
        """
        Retrieve relevant context from the knowledge base for a given query.
        Args:
            query: The query string to search for.
        Returns:
            A string containing the retrieved context.
        """
        print(f"[RetrievalTool] Searching for: {query}")
        embedding = self.vnpt_client.get_embedding(query)
        if not embedding:
            return "Error: Could not generate embedding."
            
        try:
            search_result = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=3
            )
            
            context_parts = []
            print("SEARCH RESULT:", search_result)

            for hit in search_result.points:
                if hit.payload and "text" in hit.payload:
                    context_parts.append(hit.payload["text"])

            if not context_parts:
                return "No relevant context found."

            return "\n\n".join(context_parts)
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return f"Error searching knowledge base: {e}"
