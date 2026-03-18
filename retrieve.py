from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from typing import List, Dict, Tuple


def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    """
    Load the existing ChromaDB vector store.
    
    Args:
        persist_directory: Path to the persisted ChromaDB
        
    Returns:
        Chroma vector store instance
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="pdf_documents"
    )
    return vectorstore


def retrieve_relevant_chunks(
    query: str,
    k: int = 5,
    persist_directory: str = "./chroma_db"
) -> List[Dict[str, any]]:
    """
    Retrieve the top-k most relevant document chunks for a given query.
    
    Args:
        query: User's search query
        k: Number of top results to return (default: 5)
        persist_directory: Path to the persisted ChromaDB
        
    Returns:
        List of dictionaries containing chunk text and metadata
    """
    print(f"Loading ChromaDB from '{persist_directory}'...\n")
    vectorstore = load_vectorstore(persist_directory)
    
    print(f"Searching for: '{query}'\n")
    
    # Perform similarity search with metadata
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    retrieved_chunks = []
    for i, (doc, score) in enumerate(results, 1):
        chunk_data = {
            "rank": i,
            "text": doc.page_content,
            "similarity_score": round(score, 4),
            "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
        }
        retrieved_chunks.append(chunk_data)
    
    return retrieved_chunks


def format_retrieval_results(retrieved_chunks: List[Dict[str, any]]) -> str:
    """
    Format retrieved chunks for display.
    
    Args:
        retrieved_chunks: List of retrieved chunk dictionaries
        
    Returns:
        Formatted string for display
    """
    if not retrieved_chunks:
        return "No results found."
    
    output = f"Retrieved {len(retrieved_chunks)} relevant chunks:\n"
    output += "=" * 80 + "\n\n"
    
    for chunk in retrieved_chunks:
        output += f"[Result {chunk['rank']}] (Similarity Score: {chunk['similarity_score']})\n"
        output += "-" * 80 + "\n"
        output += f"{chunk['text']}\n"
        if chunk['metadata']:
            output += f"\nMetadata: {chunk['metadata']}\n"
        output += "\n"
    
    return output


if __name__ == "__main__":
    # Test query
    test_query = "What are the provisions related to terrorism and prevention of terrorist activities?"
    
    # Retrieve chunks
    results = retrieve_relevant_chunks(test_query, k=5)
    
    # Format and print results
    formatted_output = format_retrieval_results(results)
    print(formatted_output)
