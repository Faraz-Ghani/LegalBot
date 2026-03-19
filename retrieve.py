from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from typing import List, Dict
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz  # Fallback for newer versions


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
    Load BM25 retriever from documents in the data directory.
    
    Args:
        k: Number of results to return
        data_dir: Path to directory containing PDF files
        
    Returns:
        BM25Retriever instance
    """
    print(f"Loading documents from '{data_dir}' for BM25 retriever...\n")
    documents = load_documents_from_data_dir(data_dir)
    
    if not documents:
        raise ValueError("No documents loaded for BM25 retriever")
    
    # Create BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = k
    
    print(f"✓ BM25 retriever created with {len(documents)} documents\n")
    
    return bm25_retriever


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


def load_ensemble_retriever(k: int = 5, persist_directory: str = "./chroma_db", data_dir: str = "./data"):
    """
    Load an EnsembleRetriever combining BM25 (keyword-based) and Chroma (semantic).
    
    Args:
        k: Number of top results to return from ensemble
        persist_directory: Path to the persisted ChromaDB
        data_dir: Path to directory containing PDF files
        
    Returns:
        EnsembleRetriever instance combining BM25 and Chroma
    """
    print("Loading ensemble retriever components...\n")
    
    # Load BM25 retriever
    bm25_retriever = load_bm25_retriever(k=k, data_dir=data_dir)
    
    # Load Chroma vector store
    print(f"Loading ChromaDB from '{persist_directory}'...\n")
    vectorstore = load_vectorstore(persist_directory)
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    
    # Create ensemble retriever with equal weights
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.5, 0.5]
    )
    
    print("✓ Ensemble retriever created with BM25 (0.5) + Chroma (0.5)\n")
    
    return ensemble_retriever


def retrieve_relevant_chunks(
    query: str,
    k: int = 5,
    persist_directory: str = "./chroma_db",
    data_dir: str = "./data"
) -> List[Dict[str, any]]:
    """
    Retrieve the top-k most relevant document chunks using ensemble retrieval.
    Combines BM25 (keyword-based) and semantic (vector) search.
    
    Args:
        query: User's search query
        k: Number of top results to return (default: 5)
        persist_directory: Path to the persisted ChromaDB
        data_dir: Path to directory containing PDF files
        
    Returns:
        List of dictionaries containing chunk text and metadata
    """
    print(f"Searching for: '{query}'\n")
    
    # Load ensemble retriever
    ensemble_retriever = load_ensemble_retriever(k=k, persist_directory=persist_directory, data_dir=data_dir)
    
    # Perform ensemble retrieval
    results = ensemble_retriever.invoke(query)
    
    retrieved_chunks = []
    for i, doc in enumerate(results, 1):
        # Extract source filename from metadata
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        source = metadata.get('source', 'Unknown Source')
        
        # Extract just the filename from the path if it's a full path
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
