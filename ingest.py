import os
from pathlib import Path
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv


def read_pdfs_from_directory(directory: str = "./data") -> str:
    """
    Read all PDF files from the specified directory and extract text.
    
    Args:
        directory: Path to the directory containing PDF files
        
    Returns:
        Combined text from all PDFs
    """
    all_text = ""
    data_path = Path(directory)
    
    if not data_path.exists():
        print(f"Warning: Directory '{directory}' does not exist.")
        return all_text
    
    pdf_files = list(data_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{directory}'")
        return all_text
    
    for pdf_file in pdf_files:
        try:
            print(f"Reading: {pdf_file.name}")
            doc = fitz.open(pdf_file)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                all_text += text + "\n"
            doc.close()
        except Exception as e:
            print(f"Error reading {pdf_file.name}: {e}")
    
    return all_text


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


def embed_and_store_chunks(chunks: list, persist_directory: str = "./chroma_db") -> Chroma:
    """
    Embed chunks using HuggingFace embeddings and store in ChromaDB.
    
    Args:
        chunks: List of text chunks to embed
        persist_directory: Directory to persist ChromaDB
        
    Returns:
        Chroma vector store instance
    """
    print(f"Embedding {len(chunks)} chunks using HuggingFace 'all-MiniLM-L6-v2'...\n")
    
    # Initialize HuggingFace embeddings (runs locally, no API key needed)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create ChromaDB vector store with embeddings
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
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
    
    # Step 1: Read PDFs
    raw_text = read_pdfs_from_directory(directory)
    
    if not raw_text.strip():
        print("No text extracted from PDFs.")
        return None
    
    print(f"Raw text extracted: {len(raw_text)} characters\n")
    
    # Step 2: Clean text
    cleaned_text = clean_text(raw_text)
    print(f"Cleaned text: {len(cleaned_text)} characters\n")
    
    # Step 3: Chunk text
    chunks = chunk_text(cleaned_text)
    print(f"Total chunks created: {len(chunks)}")
    print(f"Average chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} characters\n")
    
    # Step 4: Embed and store in ChromaDB
    vectorstore = embed_and_store_chunks(chunks, persist_directory)
    
    return vectorstore


if __name__ == "__main__":
    vectorstore = ingest_pdfs("./data", "./chroma_db")
