#!/usr/bin/env python3
from retrieve import retrieve_relevant_chunks

# Test multiple search queries
queries = [
    "What is section 302?",
    "section 302",
    "punishment of qatl-i-amd",
    "qatl-i-amd death punishment",
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")
    
    chunks = retrieve_relevant_chunks(query, k=5)
    
    found_302 = False
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get('source')
        text_preview = chunk['text'][:200]
        
        if 'section 302' in chunk['text'].lower() or 'punishment of qatl-i-amd' in chunk['text'].lower():
            found_302 = True
            print(f"✓ Chunk {i}: {source} - CONTAINS SECTION 302")
            print(f"   {chunk['text'][:150]}...")
        else:
            print(f"✗ Chunk {i}: {source}")
    
    if not found_302:
        print("\n⚠️  WARNING: Section 302 NOT found in any retrieved chunks!")
    else:
        print("\n✓ Section 302 found in retrieved chunks")
