from typing import List
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.models.domain import EmailDocument

class ChromaStore:
    def __init__(self):
        # Explicitly use Google's embedding model
        self.embedding = GoogleGenerativeAIEmbeddings(
            model_name="models/gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
        self.vector_db = Chroma(
            embedding_function=self.embedding,
            persist_directory="/app/storage/chroma_db",
            collection_name="inbox_ai_emails",
        )
    
    def upsert_emails(self, emails: List[EmailDocument]):
        """
        Upserts a list of EmailDocument objects into the Chroma vector store.
        Converts EmailDocument to LangChain Document format.
        """
        documents = []
        ids = []
        
        for email in emails:
            # Construct the text content for embedding
            # We prioritize subject and body_text
            page_content = f"Subject: {email.subject}\n\n{email.body_text or ''}"
            
            # Prepare metadata (ensure types are compatible with Chroma)
            metadata = {
                "gmail_id": email.gmail_id,
                "thread_id": email.thread_id,
                "sender": email.sender,
                "recipients": ", ".join(email.recipients),  # Convert list to string
                "subject": email.subject,
                "timestamp": email.timestamps.isoformat() if email.timestamps else None,
                "labels": ", ".join(email.labels)  # Convert list to string
            }
            
            # Create LangChain Document
            doc = Document(
                page_content=page_content,
                metadata={k: v for k, v in metadata.items() if v is not None} # Filter None values
            )
            
            documents.append(doc)
            ids.append(email.gmail_id)
        
        if documents:
            # add_documents with ids argument handles upsert logic in Chroma
            self.vector_db.add_documents(documents=documents, ids=ids)