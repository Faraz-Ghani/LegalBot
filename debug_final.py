#!/usr/bin/env python3
"""Debug retrieval with PPC boosting."""

from retrieve import retrieve_relevant_chunks

query = "What is section 302?"
results = retrieve_relevant_chunks(query, k=10)

print(f"Query: '{query}'\n")
print(f"Retrieved {len(results)} chunks:\n")

for i, chunk in enumerate(results, 1):
    source = chunk['source']
    text = chunk['text'][:100].replace('\n', ' ')
    has_302 = 'section 302' in text.lower() or 'qatl-i-amd' in text.lower()
    print(f"{i:2}. [{source}] {text}... {'✓' if has_302 else ''}")

# Check if section 302 is in results
found = any('section 302' in c['text'].lower() or 'qatl-i-amd' in c['text'].lower() for c in results)
print(f"\nSection 302 found in results: {found}")
