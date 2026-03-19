#!/usr/bin/env python3
"""Debug script to test retrieval components."""

from retrieve import load_ensemble_retriever, load_vectorstore, load_bm25_retriever

query = "What is section 302?"
print(f"Query: '{query}'\n")
print("=" * 80)

# Test ensemble
print("\nTesting Ensemble retriever (k=20):")
ensemble = load_ensemble_retriever(k=20)
ensemble_results = ensemble.invoke(query)
print(f"Found {len(ensemble_results)} results\n")

# Show first 5 results
for i, r in enumerate(ensemble_results, 1):
    text = r.page_content[:100].replace('\n', ' ')
    source = r.metadata.get('source', 'Unknown')
    print(f"{i:2}. [{source}] {text}...")

# Check if section 302 is in ANY of them
print("\n" + "=" * 80)
print("Searching for 'section 302' content in all results:")
found = []
for i, r in enumerate(ensemble_results, 1):
    if 'section 302' in r.page_content.lower() or 'qatl-i-amd' in r.page_content.lower():
        found.append((i, r.metadata.get('source', 'Unknown')))

if found:
    print(f"✓ Found 'section 302' in {len(found)} results:")
    for rank, source in found:
        print(f"  Rank {rank}: {source}")
else:
    print(f"✗ 'section 302' NOT found in any of the {len(ensemble_results)} results!")
