import os
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz  # Fallback for newer versions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv


def read_pdfs_from_directory(directory: str = "./data") -> dict:
    """
    Read all PDF files from the specified directory and extract text per PDF.
    
    Args:
        directory: Path to the directory containing PDF files
        
    Returns:
        Dictionary with {filename: text} mapping
    """
    pdf_texts = {}
    data_path = Path(directory)
    
    if not data_path.exists():
        print(f"Warning: Directory '{directory}' does not exist.")
        return pdf_texts
    
    pdf_files = list(data_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{directory}'")
        return pdf_texts
    
    for pdf_file in pdf_files:
        try:
            print(f"Reading: {pdf_file.name}")
            doc = fitz.open(pdf_file)
            file_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                file_text += text + "\n"
            pdf_texts[pdf_file.name] = file_text
            doc.close()
        except Exception as e:
            print(f"Error reading {pdf_file.name}: {e}")
    
    return pdf_texts


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


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list:
    """
    Split text into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks


def embed_and_store_chunks(chunks: list, metadatas: list = None, persist_directory: str = "./chroma_db") -> Chroma:
    """
    Embed chunks using HuggingFace embeddings and store in ChromaDB.
    
    Args:
        chunks: List of text chunks to embed
        metadatas: List of metadata dictionaries corresponding to chunks
        persist_directory: Directory to persist ChromaDB
        
    Returns:
        Chroma vector store instance
    """
    print(f"Embedding {len(chunks)} chunks using HuggingFace 'all-MiniLM-L6-v2'...\n")
    
    # Initialize HuggingFace embeddings (runs locally, no API key needed)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create ChromaDB vector store with embeddings and metadata
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_directory,
        collection_name="pdf_documents"
    )
    
    # Persist to disk
    vectorstore.persist()
    
    print(f"✓ Embeddings stored in ChromaDB at '{persist_directory}'")
    print(f"✓ Collection: 'pdf_documents' with {len(chunks)} vectors\n")
    
    return vectorstore


def ingest_pdfs(directory: str = "./data", persist_directory: str = "./chroma_db") -> Chroma:
    """
    Main ingestion pipeline: read PDFs, clean text, chunk, embed, and store.
    
    Args:
        directory: Path to directory containing PDFs
        persist_directory: Directory to persist ChromaDB
        
    Returns:
        Chroma vector store instance
    """
    load_dotenv()  # Load API keys from .env
    
    print(f"Starting PDF ingestion from '{directory}'...\n")
    
    # Step 1: Read all PDFs as separate documents
    pdf_texts = read_pdfs_from_directory(directory)
    
    if not pdf_texts:
        print("No PDFs found to ingest.")
        return None
    
    # Step 2: Process each PDF separately to track sources
    all_chunks = []
    all_metadatas = []
    
    for filename, raw_text in pdf_texts.items():
        if not raw_text.strip():
            print(f"Warning: No text extracted from {filename}")
            continue
        
        print(f"Processing: {filename} ({len(raw_text)} characters)")
        
        # Clean text
        cleaned_text = clean_text(raw_text)
        
        # Chunk text
        chunks = chunk_text(cleaned_text)
        
        # Add chunks with source metadata
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": filename})
        
        print(f"  Created {len(chunks)} chunks from {filename}\n")
    
    if not all_chunks:
        print("No chunks created from PDFs.")
        return None
    
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Average chunk size: {sum(len(c) for c in all_chunks) / len(all_chunks):.0f} characters\n")
    
    # Step 3: Embed and store in ChromaDB with metadata
    vectorstore = embed_and_store_chunks(all_chunks, all_metadatas, persist_directory)
    
    return vectorstore


if __name__ == "__main__":
    vectorstore = ingest_pdfs("./data", "./chroma_db")
