from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import os

class ChromaStore:
    def __init__(self):
        # Explicitly use Google's embedding model
        self.embedding = GoogleGenerativeAIEmbeddings(
            model_name="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
        self.vector_db = Chroma(
            embedding_function=self.embedding,
            persist_directory="/app/storage/chroma_db",
            collection_name="inbox_ai_emails",
        )
    
    # def upsert_emails(self , emails: List[EmailDocument]):
        