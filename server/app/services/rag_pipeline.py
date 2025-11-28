from loguru import logger
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.services.chroma_store import ChromaStore

class RagPipeline:
    def __init__(self):
        self.chroma = ChromaStore()
        # Using Gemini 1.5 Flash as requested (mapped to valid model name)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )
    
    def answer_query(self, query: str) -> str:
        """
        Retrieves relevant emails and answers the user's query.
        """
        logger.info(f"Processing RAG query: {query}")
        
        # 1. Retrieve relevant documents
        docs = self.chroma.query_similar_emails(query, n_results=5)
        
        if not docs:
            return "I couldn't find any relevant emails to answer your question."
            
        # 2. Construct context
        context_parts = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            content = doc.page_content
            source_info = f"Email {i} from {meta.get('sender')} (Subject: {meta.get('subject')}):"
            context_parts.append(f"{source_info}\n{content}\n---")
            
        context = "\n".join(context_parts)
        
        # 3. Generate answer
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an intelligent email assistant. Use the following retrieved emails to answer the user's question accurately.
If the answer is not in the emails, say "I don't have enough information in your emails to answer that."

Retrieved Emails:
{context}

User Question: {question}

Answer:"""
        )
        
        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": query})
        
        return response.content

    def get_important_emails(self) -> str:
        """
        Identifies important emails from recent history.
        """
        # For now, we'll query for generic "important" keywords
        # In a real system, this might be more sophisticated (e.g. recent unread, specific senders)
        query = "urgent important deadline meeting action required"
        docs = self.chroma.query_similar_emails(query, n_results=10)
        
        if not docs:
            return "No particularly important emails found recently."
            
        context_parts = []
        for doc in docs:
            meta = doc.metadata
            context_parts.append(f"- From: {meta.get('sender')}, Subject: {meta.get('subject')}, Date: {meta.get('timestamp')}")
            
        context = "\n".join(context_parts)
        
        prompt = PromptTemplate(
            input_variables=["context"],
            template="""Analyze the following list of emails and identify the top 3-5 most important ones that require attention.
Summarize why each is important.

Emails:
{context}

Important Emails Summary:"""
        )
        
        chain = prompt | self.llm
        response = chain.invoke({"context": context})
        
        return response.content
