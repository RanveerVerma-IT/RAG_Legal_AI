"""
RAG System for Legal Document Retrieval
Simple implementation using ChromaDB and Sentence Transformers
"""
import logging
from typing import List, Dict, Optional
import os

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available - RAG features disabled")

from config import Config

logger = logging.getLogger(__name__)


class SimpleRAGSystem:
    """Simple RAG system using ChromaDB"""
    
    def __init__(self):
        if not CHROMADB_AVAILABLE:
            logger.error("ChromaDB not available")
            self.collection = None
            return
            
        try:
            self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
            self.client = chromadb.Client()
            self.collection = self.client.create_collection("legal_documents")
            self._init_sample_data()
            logger.info("RAG system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            self.collection = None
    
    def _init_sample_data(self):
        """Load sample legal documents"""
        sample_docs = [
            {
                "id": "1",
                "content": "The Indian Contract Act, 1872 governs contractual relationships. Essential elements include offer, acceptance, consideration, and intention to create legal relations.",
                "metadata": {"type": "statute", "topic": "contracts"}
            },
            {
                "id": "2",
                "content": "Consumer Protection Act, 2019 provides for protection of consumer rights and establishes authorities for timely settlement of consumer disputes.",
                "metadata": {"type": "statute", "topic": "consumer rights"}
            },
            {
                "id": "3",
                "content": "An affidavit is a written statement confirmed by oath or affirmation for use as evidence in court. Must contain specific details and be signed before a notary.",
                "metadata": {"type": "procedure", "topic": "affidavits"}
            }
        ]
        
        try:
            self.collection.add(
                documents=[d["content"] for d in sample_docs],
                metadatas=[d["metadata"] for d in sample_docs],
                ids=[d["id"] for d in sample_docs]
            )
            logger.info(f"Loaded {len(sample_docs)} sample documents")
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")
    
    def query(self, question: str, n_results: int = 3) -> List[Dict]:
        """Query documents"""
        if not self.collection:
            logger.warning("RAG system not available")
            return []
        
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=min(n_results, Config.MAX_RESULTS)
            )
            
            if not results or not results.get("documents"):
                return []
            
            return [
                {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                }
                for i in range(len(results["documents"][0]))
            ]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []


# Voice processing - disabled by default (requires additional deps)
# TODO: Make voice input optional based on config
# class VoiceProcessor:
#     pass