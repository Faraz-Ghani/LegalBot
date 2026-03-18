import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from retrieve import retrieve_relevant_chunks

# Try to load environment variables from .env file (for local development)
try:
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except Exception:
    pass  # .env may not exist in production (Streamlit Cloud uses secrets)

# System prompt - strict context-only answering
SYSTEM_PROMPT = """You are an expert assistant. You will be provided with context extracted from official documents. Your ONLY job is to answer the user's question using STRICTLY the provided context. If the answer is not explicitly stated in the context, you must reply exactly with: "The provided documents do not contain this information." Do not use outside knowledge. Do not guess. Always cite the source filename and page number for your answer."""


def initialize_llm(api_key: str, model: str = "llama-3.3-70b-versatile", temperature: float = 0.0) -> ChatGroq:
    """
    Initialize the Groq LLM.
    
    Args:
        api_key: Groq API key
        model: Model name (default: llama3-8b-8192)
        temperature: Temperature for generation (default: 0.0 for deterministic)
        
    Returns:
        ChatGroq instance
    """
    llm = ChatGroq(
        api_key=api_key,
        model_name=model,
        temperature=temperature
    )
    return llm


def build_context_from_chunks(chunks: list) -> str:
    """
    Format retrieved chunks into a context string.
    
    Args:
        chunks: List of retrieved chunk dictionaries
        
    Returns:
        Formatted context string
    """
    if not chunks:
        return "No relevant context found in the documents."
    
    context = "RELEVANT CONTEXT FROM DOCUMENTS:\n"
    context += "=" * 80 + "\n\n"
    
    for i, chunk in enumerate(chunks, 1):
        context += f"[Source {i}] {chunk.get('metadata', {})}\n"
        context += "-" * 80 + "\n"
        context += f"{chunk['text']}\n\n"
    
    return context


def query_rag_pipeline(user_query: str, api_key: str) -> str:
    """
    Process a user query through the RAG pipeline.
    
    Args:
        user_query: User's question
        api_key: Groq API key
        
    Returns:
        LLM response
    """
    # Step 1: Retrieve relevant chunks
    print(f"\n[Retrieving context...]")
    retrieved_chunks = retrieve_relevant_chunks(user_query, k=5)
    
    # Step 2: Build context from chunks
    context = build_context_from_chunks(retrieved_chunks)
    
    # Step 3: Initialize LLM
    llm = initialize_llm(api_key)
    
    # Step 4: Create prompt with context and query
    full_prompt = f"{context}\n\nUSER QUERY:\n{user_query}"
    
    # Step 5: Generate response
    print(f"[Generating response...]\n")
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=full_prompt)
    ]
    
    response = llm.invoke(messages)
    return response.content


def main():
    """Main chat loop for interactive testing."""
    print("\n" + "=" * 80)
    print("RAG Pipeline Chat - Legal Documents")
    print("=" * 80)
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break
            
            # Query the RAG pipeline
            response = query_rag_pipeline(user_input, groq_api_key)
            
            print(f"\nAssistant: {response}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
