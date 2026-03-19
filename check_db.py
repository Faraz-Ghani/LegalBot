#!/usr/bin/env python3
"""Check if section 302 content exists in the database."""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load the vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="pdf_documents"
)

# Get all collections and count
collection = vectorstore._collection
total_count = collection.count()
print(f"Total chunks in database: {total_count}")

# Search for section 302 directly in the vector store
results = vectorstore.similarity_search("section 302", k=50)

print(f"\nFound {len(results)} results for 'section 302'")
print("\nLooking for section 302 content in first 50 semantic matches:\n")

section_302_found = False
for i, doc in enumerate(results, 1):
    if 'section 302' in doc.page_content.lower() or 'qatl-i-amd' in doc.page_content.lower():
        source = doc.metadata.get('source', 'Unknown')
        text_preview = doc.page_content[:150].replace('\n', ' ')
        print(f"✓ RANK {i}: [{source}] {text_preview}...")
        section_302_found = True

if not section_302_found:
    print("✗ Section 302 content NOT found in top 50 semantic matches!")
    print("\nFirst 3 results (to see what IS being returned):")
    for i, doc in enumerate(results[:3], 1):
        source = doc.metadata.get('source', 'Unknown')
        text_preview = doc.page_content[:150].replace('\n', ' ')
        print(f"{i}. [{source}] {text_preview}...")
