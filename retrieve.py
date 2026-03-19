from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List, Dict, Optional
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz  # Fallback for newer versions

# Global cache for expensive model/retriever loading
_embeddings_cache: Optional[HuggingFaceEmbeddings] = None
_bm25_retriever_cache: Optional[BM25Retriever] = None

# Section number to keyword mappings for query expansion
# Maps section numbers to common keywords and related terms across documents
SECTION_KEYWORDS = {
    '302': ['qatl-i-amd', 'punishment', 'death', 'ta\'zir', 'qisas'],
    '299': ['definitions', 'qatl'],
    '300': ['qatl-i-amd', 'definition'],
    '303': ['ikrah-i-tam', 'ikrah-i-naqis'],
    '304': ['proof', 'qatl', 'qisas'],
    '310': ['compounding', 'qisas', 'sulh'],
}

# General legal term expansions
LEGAL_EXPANSIONS = {
    'terrorism': ['terrorist', 'terrorism act', 'sectarian', 'hate'],
    'qisas': ['retaliation', 'qisas enforcement', 'death penalty'],
    'ta\'zir': ['ta\'zir punishment', 'discretionary punishment'],
    'offence': ['offence definition', 'punishment', 'liability'],
}


def load_documents_from_data_dir(data_dir: str = "./data") -> List[Document]:
    """
    Load and chunk all PDF documents from the data directory.
    Returns LangChain Document objects with source metadata.
    
    Args:
        data_dir: Path to directory containing PDF files
        
    Returns:
        List of LangChain Document objects with chunked text and metadata
    """
    documents = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Warning: Directory '{data_dir}' does not exist.")
        return documents
    
    pdf_files = list(data_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{data_dir}'")
        return documents
    
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    
    for pdf_file in pdf_files:
        try:
            doc = fitz.open(pdf_file)
            file_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                file_text += text + "\n"
            
            # Clean and chunk the text
            if file_text.strip():
                cleaned_text = clean_text(file_text)
                chunks = splitter.split_text(cleaned_text)
                
                # Create LangChain Document for each chunk
                for chunk_text in chunks:
                    doc_obj = Document(
                        page_content=chunk_text,
                        metadata={"source": pdf_file.name}
                    )
                    documents.append(doc_obj)
            
            doc.close()
        except Exception as e:
            print(f"Error reading {pdf_file.name}: {e}")
    
    return documents


def clean_text(text: str) -> str:
    """
    Clean extracted text to remove excessive whitespace.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text with normalized whitespace
    """
    # Replace multiple newlines with single newline
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    
    # Remove multiple spaces within lines
    lines = []
    for line in text.split("\n"):
        cleaned_line = " ".join(line.split())
        if cleaned_line:  # Skip empty lines
            lines.append(cleaned_line)
    
    # Join with single newlines
    cleaned_text = "\n".join(lines)
    
    return cleaned_text


def load_bm25_retriever(k: int = 5, data_dir: str = "./data") -> BM25Retriever:
    """
    Load or retrieve cached BM25 retriever.
    Documents are cached to avoid reloading PDFs on every query.
    
    Args:
        k: Number of top results to return
        data_dir: Path to directory containing PDF files
        
    Returns:
        BM25Retriever instance
    """
    global _bm25_retriever_cache
    
    # Return cached retriever if available
    if _bm25_retriever_cache is not None:
        _bm25_retriever_cache.k = k
        return _bm25_retriever_cache
    
    # Otherwise, load documents and create retriever
    print(f"Loading documents from '{data_dir}' for BM25 retriever...\n")
    documents = load_documents_from_data_dir(data_dir)
    
    if not documents:
        raise ValueError("No documents loaded for BM25 retriever")
    
    # Create BM25 retriever
    _bm25_retriever_cache = BM25Retriever.from_documents(documents)
    _bm25_retriever_cache.k = k
    
    print(f"✓ BM25 retriever created with {len(documents)} documents\n")
    
    return _bm25_retriever_cache


def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    """
    Load the existing ChromaDB vector store with cached embeddings.
    
    Args:
        persist_directory: Path to the persisted ChromaDB
        
    Returns:
        Chroma vector store instance
    """
    global _embeddings_cache
    
    # Reuse cached embeddings if available
    if _embeddings_cache is None:
        print("Loading HuggingFace embeddings model (this may take a moment)...")
        _embeddings_cache = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("✓ Embeddings model loaded\n")
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=_embeddings_cache,
        collection_name="pdf_documents"
    )
    return vectorstore


def _expand_query(query: str) -> str:
    """
    Expand a query with related keywords for better retrieval across documents.
    
    For example: "What is section 302?" becomes "section 302 qatl-i-amd punishment death ta'zir qisas"
    This helps find related content across all documents.
    
    Args:
        query: Original user query
        
    Returns:
        Expanded query with related keywords
    """
    expanded = query
    
    # Check if query asks about a specific section
    import re
    section_match = re.search(r'section\s+(\d+)', query.lower())
    
    if section_match:
        section_num = section_match.group(1)
        if section_num in SECTION_KEYWORDS:
            # Add related keywords to the query
            keywords = SECTION_KEYWORDS[section_num]
            expanded = query + " " + " ".join(keywords)
    
    # Check for general legal terms and expand them
    for term, expansions in LEGAL_EXPANSIONS.items():
        if term in query.lower():
            expanded = expanded + " " + " ".join(expansions)
    
    return expanded


def retrieve_relevant_chunks(
    query: str,
    k: int = 10,
    persist_directory: str = "./chroma_db",
    data_dir: str = "./data"
) -> List[Dict[str, any]]:
    """
    Retrieve the top-k most relevant document chunks using BM25 retrieval with query expansion.
    
    Scales to 200+ PDFs by:
    1. Expanding queries with domain-specific keywords (e.g., section 302 -> qatl-i-amd, punishment, etc.)
    2. Using fast BM25 keyword search (linear complexity, no embeddings)
    3. Filtering by relevance without loading models
    
    Args:
        query: User's search query
        k: Number of top results to return (default: 10)
        persist_directory: Path to the persisted ChromaDB (unused, kept for compatibility)
        data_dir: Path to directory containing PDF files
        
    Returns:
        List of dictionaries containing chunk text and metadata
    """
    print(f"Searching for: '{query}'\n")
    
    # Expand query with related keywords
    expanded_query = _expand_query(query)
    
    # Use BM25 retriever (fast, scales to 200+ PDFs)
    # Get more results to allow filtering without missing relevant content
    bm25_retriever = load_bm25_retriever(k=k*3, data_dir=data_dir)
    results = bm25_retriever.invoke(expanded_query)
    
    # Simple relevance filtering: keep top k, prefer exact matches
    query_lower = query.lower()
    scored_results = []
    
    for doc in results:
        text_lower = doc.page_content.lower()
        
        # Score based on how well the chunk matches the original query
        score = 0
        
        # High score for exact phrase matches
        if query_lower in text_lower:
            score += 100
        
        # Medium score for individual keyword matches
        for word in query_lower.split():
            if len(word) > 3 and word in text_lower:
                score += 10
        
        # Keep documents with any relevance
        if score > 0 or 'section' in query_lower:
            scored_results.append((score, doc))
    
    # Sort by relevance score
    scored_results.sort(key=lambda x: -x[0])
    results = [doc for _, doc in scored_results[:k]]
    
    # If no results found with scoring, fall back to BM25 results
    if not results:
        results = bm25_retriever.invoke(query)[:k]
    
    # Convert to dictionary format
    retrieved_chunks = []
    for i, doc in enumerate(results, 1):
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        source = metadata.get('source', 'Unknown Source')
        
        # Extract just filename
        if '/' in source:
            source = source.split('/')[-1]
        
        chunk_data = {
            "rank": i,
            "text": doc.page_content,
            "source": source,
            "metadata": metadata
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
    
    output = f"Retrieved {len(retrieved_chunks)} relevant chunks (via ensemble retrieval):\n"
    output += "=" * 80 + "\n\n"
    
    for chunk in retrieved_chunks:
        source = chunk.get('source', 'Unknown Source')
        output += f"[{source}]\n"
        output += "-" * 80 + "\n"
        output += f"{chunk['text']}\n\n"
    
    return output


if __name__ == "__main__":
    # Test query
    test_query = "What are the provisions related to terrorism and prevention of terrorist activities?"
    
    # Retrieve chunks
    results = retrieve_relevant_chunks(test_query, k=5)
    
    # Format and print results
    formatted_output = format_retrieval_results(results)
    print(formatted_output)
