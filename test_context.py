#!/usr/bin/env python3
"""Debug what context is sent to LLM."""

from retrieve import retrieve_relevant_chunks
from chat import build_context_from_chunks

query = "What is section 302?"
chunks = retrieve_relevant_chunks(query, k=10)

print(f"Retrieved {len(chunks)} chunks")
print()

context = build_context_from_chunks(chunks, max_length=3000)

print("CONTEXT SENT TO LLM:")
print("=" * 80)
print(context)
print("=" * 80)
print(f"\nContext length: {len(context)} characters")
