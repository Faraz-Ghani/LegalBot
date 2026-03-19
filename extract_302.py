#!/usr/bin/env python3
"""Extract and search section 302 from PPC PDF."""

try:
    import fitz
except ImportError:
    import pymupdf as fitz

pdf_path = "./data/PPC.pdf"
doc = fitz.open(pdf_path)

print(f"Searching for 'section 302' in {pdf_path}\n")

section_302_found = False
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    if 'section 302' in text.lower() or 'qatl-i-amd' in text.lower():
        print(f"Found on page {page_num + 1}:")
        print("=" * 80)
        print(text)
        print("=" * 80)
        section_302_found = True
        
        if section_302_found:
            break

if not section_302_found:
    print("Section 302 not found!")

doc.close()
