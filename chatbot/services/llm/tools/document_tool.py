from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import Optional, Any

from chatbot.services.llm.vector_store import PGVectorStore

class DocumentSearchInput(BaseModel):
    query: str = Field(..., description="Search query for documents")
    k: Optional[int] = Field(3, description="Number of results to return")

@tool(args_schema=DocumentSearchInput)
def document_search_tool(
    query: str,
    vector_store:Optional[PGVectorStore] = None,
    k: int = 3
) -> str:
    """Search through business documents using semantic search."""
    if not vector_store:
        return "Document search not configured"
    
    try:
        results = vector_store.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Document search failed: {e}"