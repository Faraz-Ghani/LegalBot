#!/usr/bin/env python3
"""Test LLM directly with section 302 context."""

import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("No API key")
    exit(1)

llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0.0)

context = """RELEVANT CONTEXT FROM DOCUMENTS:

[PPC.pdf]
302. Punishment of qatl-i-amd
(a) punished with death as qisas;
(b) punished with death for imprisonment for life as ta'zir having regard to the facts
and circumstances of the case, if the proof in either of the forms specified in
section 304 is not available; or
(c) punished with imprisonment of either description for a term which may extend
to twenty-five years, where according to the Injunctions of Islam the
punishment of qisas is not applicable
Provided that nothing in clause (c) shall apply where the principle of fasad-fil-arz is attracted
and in such cases only clause (a) or clause (b) shall apply.
"""

query = "What is section 302?"
full_prompt = f"{context}\n\nUSER QUERY:\n{query}"

system_prompt = """You are an expert assistant. You will be provided with context extracted from official documents. Your ONLY job is to answer the user's question using STRICTLY the provided context. If the answer is not explicitly stated in the context, you must reply exactly with: "The provided documents do not contain this information." Do not use outside knowledge. Do not guess. Always cite the source filename and page number for your answer."""

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=full_prompt)
]

response = llm.invoke(messages)
print("LLM Response:")
print(response.content)
