import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core._api.deprecation")

import streamlit as st
from chat import query_rag_pipeline
from retrieve import retrieve_relevant_chunks
import os
import subprocess
from pathlib import Path

# Initialize Groq API key - works both locally (.env) and in production (Streamlit secrets)
try:
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not groq_api_key:
        groq_api_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    groq_api_key = st.secrets.get("GROQ_API_KEY", "")

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Please set it in .env (local) or Streamlit secrets (production).")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Legal Document RAG Chat",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile responsiveness and styling
st.markdown("""
    <style>
    /* Mobile responsiveness */
    @media (max-width: 640px) {
        .main {
            padding: 1rem 0.5rem;
        }
        .stChatMessage {
            padding: 0.5rem;
        }
    }
    
    /* Chat styling */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        background-color: #f5f5f5;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .source-box {
        background-color: #e8f4f8;
        border-left: 4px solid #0088cc;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    
    .source-title {
        font-weight: bold;
        color: #0088cc;
        margin-bottom: 0.5rem;
    }
    
    .source-content {
        color: #333;
        line-height: 1.5;
    }
    
    .sources-section {
        background-color: #f0f8ff;
        border: 1px solid #0088cc;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    .sources-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #0088cc;
        margin-bottom: 0.5rem;
    }
    
    .answer-section {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Vector Database Management
st.sidebar.markdown("## 🛠️ Database Management")

if st.sidebar.button("🧠 Build/Update Vector Database", use_container_width=True):
    """Run the ingest.py script to build/update the vector database."""
    with st.spinner("Reading and embedding PDFs... This may take a minute."):
        try:
            # Get the directory of the current script
            script_dir = Path(__file__).parent
            ingest_script = script_dir / "ingest.py"
            
            # Run ingest.py as a subprocess
            result = subprocess.run(
                ["python", str(ingest_script)],
                cwd=str(script_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                st.sidebar.success("✅ Vector database built successfully!")
                st.rerun()
            else:
                st.sidebar.error(f"❌ Error building database:\n{result.stderr}")
        except subprocess.TimeoutExpired:
            st.sidebar.error("❌ Database build timed out (exceeded 10 minutes)")
        except Exception as e:
            st.sidebar.error(f"❌ Error running ingest.py: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.info("ℹ️ Click the button above to build or update the vector database from PDFs in the `data/` directory.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources" not in st.session_state:
    st.session_state.sources = {}

# Check if chroma_db exists
chroma_db_path = Path("./chroma_db")
database_exists = chroma_db_path.exists()

# Header
st.markdown("# ⚖️ Legal Document RAG Assistant")
st.markdown("Ask questions about Pakistani legal documents. Get answers sourced directly from official documents.")

# Warning if database doesn't exist
if not database_exists:
    st.warning(
        "⚠️ Vector database not found. Please click the **'🧠 Build/Update Vector Database'** button in the sidebar to initialize the system."
    )
    st.info("The database will read all PDFs from the `data/` directory and embed them for searching.")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if this is an assistant message
            if message["role"] == "assistant" and message.get("message_id"):
                message_id = message["message_id"]
                if message_id in st.session_state.sources:
                    sources = st.session_state.sources[message_id]
                    with st.expander("📄 View Sources", expanded=False):
                        for i, source in enumerate(sources, 1):
                            with st.container():
                                st.markdown(f"**Source {i}** (Similarity: {source['similarity_score']})")
                                st.markdown(f"```\n{source['text']}\n```")
                                if source.get('metadata'):
                                    st.caption(f"📌 {source['metadata']}")

# Input section
st.markdown("---")
input_col1, input_col2 = st.columns([1, 0.15])

with input_col1:
    user_input = st.text_input(
        "Your question:",
        placeholder="E.g., What are the punishment provisions for terrorism?",
        label_visibility="collapsed",
        disabled=not database_exists  # Disable input if database doesn't exist
    )

with input_col2:
    send_button = st.button("Send", use_container_width=True, disabled=not database_exists)

# Process user input
if send_button and user_input and database_exists:
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Show loading state
    with st.spinner("Retrieving context and generating response..."):
        try:
            # Query the RAG pipeline
            response = query_rag_pipeline(user_input, groq_api_key)
            
            # Retrieve sources for citation
            retrieved_chunks = retrieve_relevant_chunks(user_input, k=5)
            
            # Generate unique message ID
            message_id = f"msg_{len(st.session_state.messages)}"
            
            # Store sources
            st.session_state.sources[message_id] = retrieved_chunks
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "message_id": message_id
            })
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
                
                # Display sources in expandable section
                with st.expander("📄 View Sources", expanded=False):
                    for i, source in enumerate(retrieved_chunks, 1):
                        st.markdown(f"**Source {i}** (Similarity: {source['similarity_score']})")
                        st.markdown(f"```\n{source['text']}\n```")
                        if source.get('metadata'):
                            st.caption(f"📌 {source['metadata']}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please make sure your GROQ_API_KEY is set in the .env file.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
    This assistant provides answers based strictly on official legal documents provided.
    For legal advice, please consult with a qualified legal professional.
    </div>
    """,
    unsafe_allow_html=True
)
