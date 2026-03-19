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
SYSTEM_PROMPT = """You are a legal expert assistant. Answer the user's question using ONLY the provided context from official Pakistani legal documents. If you find the answer in the context, cite the source and provide all relevant details. If the answer is not in the context, reply: "The provided documents do not contain this information." Be thorough and quote relevant sections."""


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


def build_context_from_chunks(chunks: list, max_length: int = 3000) -> str:
    """
    Format retrieved chunks into a context string.
    
    Args:
        chunks: List of retrieved chunk dictionaries
        max_length: Maximum length of context in characters (default: 3000)
        
    Returns:
        Formatted context string
    """
    if not chunks:
        return "No relevant context found in the documents."
    
    context = "RELEVANT CONTEXT FROM DOCUMENTS:\n"
    context += "=" * 80 + "\n\n"
    
    current_length = len(context)
    
    for chunk in chunks:
        source = chunk.get('source', 'Unknown Source')
        chunk_text = f"[{source}]\n"
        chunk_text += "-" * 80 + "\n"
        chunk_text += f"{chunk['text']}\n\n"
        
        # Stop adding chunks if we exceed max length
        if current_length + len(chunk_text) > max_length:
            context += f"\n[...additional relevant context truncated to fit token limit...]\n"
            break
        
        context += chunk_text
        current_length += len(chunk_text)
    
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
    # Step 1: Retrieve relevant chunks (retrieve more to ensure coverage)
    print(f"\n[Retrieving context...]")
    retrieved_chunks = retrieve_relevant_chunks(user_query, k=20)
    
    # Step 2: Build context from chunks (use all retrieved chunks, context limiting will handle size)
    context = build_context_from_chunks(retrieved_chunks, max_length=3000)
    
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
