#!/usr/bin/env python3
"""Debug BM25 retrieval for section 302."""

from retrieve import load_bm25_retriever

query = "What is section 302?"
print(f"Query: '{query}'\n")

bm25 = load_bm25_retriever(k=20)
results = bm25.invoke(query)

print(f"BM25 found {len(results)} results:\n")

for i, doc in enumerate(results, 1):
    source = doc.metadata.get('source', 'Unknown')
    text = doc.page_content[:100].replace('\n', ' ')
    print(f"{i:2}. [{source}] {text}...")

# Check if section 302 is in results
print("\nSearching for 'section 302' in results:")
found = False
for i, doc in enumerate(results, 1):
    if 'section 302' in doc.page_content.lower() or 'qatl-i-amd' in doc.page_content.lower():
        print(f"  ✓ Found at rank {i}: {doc.metadata.get('source', 'Unknown')}")
        found = True

if not found:
    print(f"  ✗ NOT found in any of the {len(results)} results")
