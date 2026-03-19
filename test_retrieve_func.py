#!/usr/bin/env python3
"""Debug retrieve_relevant_chunks scoring."""

from retrieve import retrieve_relevant_chunks

query = "What is section 302?"
results = retrieve_relevant_chunks(query, k=10)

print(f"Retrieved {len(results)} chunks:\n")

for i, chunk in enumerate(results[:10], 1):
    source = chunk['source']
    text = chunk['text'][:80].replace('\n', ' ')
    has_302 = '302' in chunk['text'].lower() or 'qatl-i-amd' in chunk['text'].lower()
    print(f"{i}. [{source}] {text}... {'✓ HAS 302' if has_302 else ''}")

found = any('302' in c['text'].lower() or 'qatl-i-amd' in c['text'].lower() for c in results)
print(f"\nSection 302 in results: {found}")
