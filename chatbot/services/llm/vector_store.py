from typing import Any, Dict, List
from django.db import connection


from chatbot.services.embedding_service import HuggingFaceEmbeddingService
from langchain_postgres import PGVector
from langchain.docstore.document import Document


import logging
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Factory for creating and managing vector stores"""
    
    @staticmethod
    def create_vector_store(connection_string: str, collection_name: str, embedding_dim: int = 1536) -> 'PGVectorStore':
        """Factory method for creating vector stores"""
        return PGVectorStore(connection_string, collection_name, embedding_dim)
    


class PGVectorStore:
    """Production-ready pgvector store implementation with error handling"""

    def __init__(self, connection_string: str, collection_name: str, embedding_dim: int = 1536):
        """
        Initialize the PGVector store.

        Args:
            connection_string: PostgreSQL connection string
            collection_name: Name of the collection/table to use
            embedding_dim: Dimension of the embeddings (default 1536 for OpenAI)
        """
        self.connection_string = connection_string
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

        self.embeddings = HuggingFaceEmbeddingService()

        try:
            self._ensure_extension()
            self.store = PGVector(
                connection=connection_string,
                embeddings=self.embeddings,
                collection_name=collection_name,
                use_jsonb=True,
            )
        except Exception as e:
            logger.critical(f"PGVectorStore initialization failed: {str(e)}")
            raise

    def _ensure_extension(self):
        """Ensure pgvector extension is enabled in the database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        except Exception as e:
            logger.error(f"Failed to enable pgvector extension: {str(e)}")
            raise

    def _get_embedding_function(self):
        """
        Get the embedding function based on configuration.
        In a real implementation, you would return the appropriate embedding function.
        """
        # This is a placeholder - you should implement based on your actual embedding service
        def dummy_embedding(text: str) -> List[float]:
            return [0.0] * self.embedding_dim

        return dummy_embedding

    def store_documents(self, documents: List[Document], **kwargs) -> List[str]:
        """
        Store documents with embeddings in the vector store.

        Args:
            documents: List of Langchain Document objects
            **kwargs: Additional arguments for the store

        Returns:
            List of document IDs
        """
        try:
            return self.store.add_documents(documents, **kwargs)
        except Exception as e:
            logger.error(f"Failed to store documents: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        """
        Perform similarity search on stored vectors.

        Args:
            query: The query string
            k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of matching Documents
        """
        try:
            return self.store.similarity_search(query, k=k, **kwargs)
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise

    def similarity_search_with_score(self, query: str, k: int = 4, **kwargs) -> List[tuple]:
        """
        Perform similarity search with scores.

        Args:
            query: The query string
            k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of tuples (Document, score)
        """
        try:
            return self.store.similarity_search_with_score(query, k=k, **kwargs)
        except Exception as e:
            logger.error(f"Similarity search with score failed: {str(e)}")
            raise

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by their IDs.

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Implementation depends on how you want to handle deletions
            # This is a placeholder implementation
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM langchain_pg_embedding WHERE collection_id = %s AND id = ANY(%s)",
                    [self.collection_name, ids]
                )
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as document_count,
                        pg_size_pretty(pg_total_relation_size('langchain_pg_embedding')) as size
                    FROM langchain_pg_embedding
                    WHERE collection_id = %s
                    """,
                    [self.collection_name]
                )
                result = cursor.fetchone()
                return {
                    'document_count': result[0],
                    'size': result[1],
                    'collection_name': self.collection_name
                }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                'error': str(e),
                'collection_name': self.collection_name
            }

    @classmethod
    def from_documents(cls, documents: List[Document], **kwargs) -> 'PGVectorStore':
        """
        Create a PGVectorStore from a list of documents.

        Args:
            documents: List of Langchain Document objects
            **kwargs: Additional arguments for initialization

        Returns:
            PGVectorStore instance
        """
        instance = cls(**kwargs)
        instance.store_documents(documents)
        return instance

