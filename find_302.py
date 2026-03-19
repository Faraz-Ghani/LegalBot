#!/usr/bin/env python3
"""Find actual section 302 content."""

import fitz

doc = fitz.open("./data/PPC.pdf")

# Search all pages
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    if '302' in text and 'qatl-i-amd' in text.lower():
        print(f"PAGE {page_num + 1}:")
        print("=" * 80)
        print(text)
        print("=" * 80)

doc.close()
