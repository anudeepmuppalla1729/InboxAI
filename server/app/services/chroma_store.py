from typing import List
import os
import time
from loguru import logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.models.domain import EmailDocument
from app.core.config import settings

class ChromaStore:
    def __init__(self):
        # Explicitly use Google's embedding model
        self.embedding = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GEMINI_API_KEY,
        )
        
        # Construct path relative to this file: server/app/services/chroma_store.py
        # We want: server/storage/chroma_db
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        persist_dir = os.path.join(base_dir, "storage", "chroma_db")
        
        self.vector_db = Chroma(
            embedding_function=self.embedding,
            persist_directory=persist_dir,
            collection_name="inbox_ai_emails",
        )
    
    def upsert_emails(self, emails: List[EmailDocument], batch_size: int = 2, delay: float = 10.0):
        """
        Upserts a list of EmailDocument objects into the Chroma vector store.
        Converts EmailDocument to LangChain Document format.
        Handles rate limits by processing in batches with delays and retries.
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
            total_docs = len(documents)
            logger.info(f"Processing {total_docs} documents in batches of {batch_size}...")
            
            for i in range(0, total_docs, batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        logger.info(f"Upserting batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size} (Attempt {attempt+1})...")
                        self.vector_db.add_documents(documents=batch_docs, ids=batch_ids)
                        break # Success, exit retry loop
                    except Exception as e:
                        if "429" in str(e) and attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 10 # Backoff: 10s, 20s
                            logger.warning(f"Rate limit hit. Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"Failed to upsert batch starting at index {i}: {e}")
                            break # Fail or max retries reached
                
                # Standard delay between successful batches
                if i + batch_size < total_docs:
                    time.sleep(delay)

    def query_similar_emails(self, query: str, n_results: int = 5) -> List[Document]:
        """
        Search for emails similar to the query.
        """
        if not query:
            return []
            
        return self.vector_db.similarity_search(query, k=n_results)