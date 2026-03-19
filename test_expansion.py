#!/usr/bin/env python3
"""Debug query expansion."""

from retrieve import _expand_query, load_bm25_retriever

query = "What is section 302?"
expanded = _expand_query(query)

print(f"Original query: '{query}'")
print(f"Expanded query: '{expanded}'")
print()

# Test both queries
bm25 = load_bm25_retriever(k=15)

print("Results with ORIGINAL query:")
results = bm25.invoke(query)
for i, r in enumerate(results[:5], 1):
    source = r.metadata.get('source', 'Unknown')
    has_302 = '302' in r.page_content.lower() or 'qatl-i-amd' in r.page_content.lower()
    print(f"{i}. [{source}] {r.page_content[:80]}... {'✓' if has_302 else ''}")

print("\nResults with EXPANDED query:")
results = bm25.invoke(expanded)
for i, r in enumerate(results[:5], 1):
    source = r.metadata.get('source', 'Unknown')
    has_302 = '302' in r.page_content.lower() or 'qatl-i-amd' in r.page_content.lower()
    print(f"{i}. [{source}] {r.page_content[:80]}... {'✓' if has_302 else ''}")

# Check if 302 appears in top 15 with expanded query
print("\nSearching for section 302 in top 15 results (expanded):")
results = bm25.invoke(expanded)
for i, r in enumerate(results, 1):
    if '302' in r.page_content.lower() or 'qatl-i-amd' in r.page_content.lower():
        print(f"  ✓ Found at rank {i}")
        break
else:
    print(f"  ✗ NOT found in top 15")
