#!/usr/bin/env python3
from ingest import clean_text, chunk_text
try:
    import fitz
except:
    import pymupdf as fitz

# Read PPC pages 106-107
doc = fitz.open('data/PPC.pdf')
page106 = doc[105].get_text()
page107 = doc[106].get_text()

combined = page106 + "\n" + page107

# Check if section 302 content is there
if "Punishment of qatl-i-amd" in combined and "punished with death as qisas" in combined:
    print("✓ Section 302 content IS in pages 106-107")
    print("\n" + "="*80)
    print("Checking if this content gets into chunks...")
    print("="*80)
    
    # Clean and chunk like ingest.py does
    cleaned = clean_text(combined)
    chunks = chunk_text(cleaned)
    
    print(f"\nCreated {len(chunks)} chunks from these 2 pages")
    
    # Check if any chunk contains section 302 details
    found_count = 0
    for i, chunk in enumerate(chunks):
        if "Punishment of qatl-i-amd" in chunk or "punished with death as qisas" in chunk:
            found_count += 1
            print(f"\nChunk {i} contains section 302 content:")
            print(chunk[:300])
            print("...")
    
    print(f"\n\nTotal chunks with section 302 content: {found_count}")
    
    if found_count == 0:
        print("\n⚠️  WARNING: Section 302 content is NOT in the chunks!")
        print("This is a critical issue - the content exists in the PDF but is being lost during chunking")
else:
    print("✗ Section 302 content missing from pages")
