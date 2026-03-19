# Legal Document RAG Chatbot 🏛️⚖️

A comprehensive legal document retrieval and question-answering system built with **BM25 keyword search**, **query expansion**, and **LLMs** (Groq). Designed to answer questions about Pakistani legal documents including the Pakistan Penal Code (PPC), Code of Criminal Procedure (CRPC), and other legal texts.

## Features

✅ **Fast Keyword-Based Retrieval** - BM25 search without expensive embedding models  
✅ **Query Expansion** - Automatic legal term mapping (section 302 → qatl-i-amd, punishment, etc.)  
✅ **Cross-Document Retrieval** - Search across 13+ legal documents simultaneously  
✅ **Intelligent Caching** - Global retriever cache for millisecond queries  
✅ **Comprehensive Testing** - 50 tests covering all functionality (100% pass rate)  
✅ **Production-Ready** - Deployed on Streamlit Cloud  
✅ **Unicode Support** - Handles Urdu/Arabic diacritics correctly  

## Quick Start

### Local Development

#### 1. Clone Repository
```bash
git clone https://github.com/Faraz-Ghani/LegalBot.git
cd LegalBot
```

#### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables
Create `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com/keys

#### 5. Prepare Legal Documents
Place PDF files in `./Data/` directory:
```
Data/
├── PPC.pdf (Pakistan Penal Code)
├── CRPC.pdf (Code of Criminal Procedure)
├── QSO 1984.pdf (Evidence Act)
└── ... other legal documents
```

#### 6. Run Streamlit App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Deployment on Streamlit Cloud

### Prerequisites
- GitHub account with repository pushed
- Groq API key

### Steps

#### 1. Push Repository to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/LegalBot.git
git branch -M main
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Select your GitHub repository: `YOUR_USERNAME/LegalBot`
4. Select branch: `main`
5. Select main file path: `app.py`
6. Click **"Deploy"**

#### 3. Set Secrets (Environment Variables)
1. In Streamlit Cloud dashboard, click the app
2. Go to **Settings** → **Secrets**
3. Add:
```
GROQ_API_KEY = "your_groq_api_key_here"
```
4. Click **Save**

#### 4. Add Data Files
**Important**: Legal documents must be manually uploaded to Streamlit's file system or stored in cloud storage.

**Option A: Via File Upload in App**
- Use the "Upload PDF Documents" button in the app sidebar
- Documents will be cached in Streamlit's session state

**Option B: Via GitHub (if under 100MB total)**
```bash
# Create Data directory
mkdir -p Data
# Add PDF files
cp /path/to/PPC.pdf Data/
cp /path/to/CRPC.pdf Data/
# Commit and push
git add Data/*.pdf
git commit -m "Add legal documents"
git push
```

**Option C: Via External Storage (Recommended for large files)**
- Use Google Drive, AWS S3, or Azure Blob Storage
- Modify `ingest.py` to download from cloud storage

#### 5. Monitor Deployment
- Check logs in Streamlit Cloud dashboard
- App rebuilds automatically when you push to GitHub

---

## System Architecture

```
User Input (Streamlit UI)
         ↓
Query Expansion (retrieve.py)
         ↓
BM25 Keyword Search (with caching)
         ↓
Context Building (chat.py)
         ↓
Groq LLM (llama-3.3-70b-versatile)
         ↓
Streamed Response
```

### Key Components

**app.py** (273 lines)
- Streamlit UI with sidebar controls
- File upload for PDF documents
- Chat history management
- Mobile-responsive design

**retrieve.py** (315 lines)
- BM25-based keyword search
- Query expansion with legal term mappings
- Global retriever caching
- Intelligent relevance scoring

**chat.py** (144 lines)
- RAG pipeline coordination
- Context assembly from chunks
- Character limit enforcement (3000 chars)
- LLM prompt management

**ingest.py** (196 lines)
- PDF text extraction (PyMuPDF)
- Document chunking (RecursiveCharacterTextSplitter)
- ChromaDB vector storage (backup)

---

## Testing

The project includes a comprehensive 50-test suite covering:
- Basic retrieval functionality
- Query expansion mechanisms
- Context building for LLM
- Cross-document retrieval
- Edge cases and scalability

### Run Tests Locally
```bash
python3 test_suite.py
```

### Expected Output
```
TEST SUMMARY: 50/50 passed (0 failed)
✓ All tests passed successfully
```

### Test Documentation
- **TESTING_GUIDE.md** - Complete testing guide with examples
- **TEST_PROCEDURE.md** - Detailed testing procedures

---

## Configuration

### Streamlit Config (`.streamlit/config.toml`)

**Theme**:
```toml
[theme]
primaryColor = "#0088cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

**Server Settings**:
```toml
[server]
headless = true
port = 8501
enableXsrfProtection = true
maxUploadSize = 200  # MB
```

### Environment Variables

**Local (.env)**:
```
GROQ_API_KEY=sk-xxxx
```

**Production (Streamlit Secrets)**:
- Navigate to app settings → Secrets
- Add: `GROQ_API_KEY = "sk-xxxx"`

---

## Requirements

### Core Dependencies
- **langchain** (>=0.1.0) - LLM orchestration
- **groq** (>=0.4.0) - Groq API client
- **streamlit** (>=1.28.0) - Web UI
- **rank_bm25** (>=0.2.2) - Keyword search
- **pymupdf** (>=1.23.0) - PDF parsing
- **python-dotenv** (>=1.0.0) - Environment variables

### Optional Dependencies (for embeddings)
- **sentence-transformers** (>=2.2.2)
- **langchain-huggingface** (>=0.0.1)
- **chromadb** (>=0.4.0)

### Python Version
- Python 3.9 or higher

### Full Requirements
See `requirements.txt` for complete list with pinned versions.

---

## Performance Metrics

### Query Speed
| Query Type | First Run | Subsequent | 
|------------|-----------|------------|
| Basic section query | 0.5s | 0.05s |
| Complex multi-word | 0.53s | 0.08s |
| Large k=100 retrieval | 0.54s | 0.15s |

**Note**: First query includes PDF loading. Subsequent queries use cached retriever.

### Coverage
- **Documents**: 13 legal documents indexed
- **Chunks**: 3,164 chunks total
- **Keywords**: 300+ legal terms mapped
- **Languages**: English + Urdu/Arabic diacritics

---

## Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution**: 
- Local: Add to `.env` file
- Production: Add to Streamlit Secrets (Settings → Secrets)

### Issue: "No documents found in Data directory"
**Solution**:
- Ensure PDF files are in `./Data/` folder
- Check file permissions
- Try uploading via app sidebar

### Issue: "Slow retrieval queries"
**Solution**:
- First query is slower (loading PDFs) - normal
- Subsequent queries should be fast (cached)
- Check system RAM availability

### Issue: "Streamlit deployment fails"
**Solution**:
- Check GitHub repo is public
- Verify `app.py` exists in root
- Check Streamlit Cloud logs
- Ensure GROQ_API_KEY is set in Secrets

### Issue: "Special characters/Urdu text not displaying"
**Solution**:
- Ensure PDFs are UTF-8 encoded
- Check Streamlit version (>=1.28.0)
- Clear browser cache

---

## Query Expansion

The system automatically expands queries with legal terminology:

### Section Mappings
```python
'302': 'qatl-i-amd', 'punishment', 'death', 'ta\'zir', 'qisas'
'299': 'definitions', 'qatl'
'300': 'qatl-i-amd', 'definition'
'303': 'hurt', 'injury'
'304': 'act', 'danger'
'310': 'grievous hurt'
```

### Legal Term Mappings
```python
'terrorism': 'terrorist', 'sectarian', 'hate', 'extremism'
'qisas': 'retaliation', 'death penalty', 'punishment'
'ta\'zir': 'discretionary punishment', 'correction'
'offence': 'crime', 'punishment', 'liability'
```

---

## Development & Contributing

### Project Structure
```
LegalBot/
├── app.py              # Streamlit UI
├── chat.py             # RAG pipeline
├── retrieve.py         # Keyword search & expansion
├── ingest.py           # PDF processing
├── test_suite.py       # 50 comprehensive tests
├── requirements.txt    # Dependencies
├── .streamlit/
│   └── config.toml     # Streamlit config
├── .env                # Local secrets (git-ignored)
├── Data/               # PDF documents (git-ignored)
├── chroma_db/          # Vector DB (git-ignored)
├── README.md           # This file
├── TESTING_GUIDE.md    # Testing documentation
└── TEST_PROCEDURE.md   # Testing procedures
```

### Adding New Legal Documents
1. Place PDF in `./Data/`
2. Update query expansion in `retrieve.py` if needed
3. Run tests to verify retrieval
4. Commit and push

### Adding New Tests
1. Edit `test_suite.py`
2. Add test to appropriate section (1-5)
3. Run `python3 test_suite.py`
4. Update `TEST_PROCEDURE.md`

### Modifying Query Expansion
Edit `retrieve.py` and update:
- `SECTION_KEYWORDS` - for legal sections
- `LEGAL_EXPANSIONS` - for general terms

---

## Best Practices

✅ **Do**:
- Always activate virtual environment before running
- Set GROQ_API_KEY in `.env` locally
- Test locally before pushing to GitHub
- Run test suite before deployment
- Keep PDFs under 100MB each
- Use meaningful commit messages

❌ **Don't**:
- Commit `.env` file to GitHub
- Push sensitive API keys to repository
- Modify `requirements.txt` without testing
- Upload large PDF files (>100MB) to GitHub
- Leave debug print statements in production

---

## Monitoring & Maintenance

### Weekly Tasks
- Check Streamlit Cloud logs
- Monitor app performance metrics
- Test retrieval quality on sample queries
- Review error logs

### Monthly Tasks
- Update dependency versions: `pip list --outdated`
- Run full test suite: `python3 test_suite.py`
- Review query expansion mappings
- Check document coverage gaps

---

## FAQ

**Q: How many documents can the system handle?**  
A: System tested and optimized for 13+ documents. Should scale to 200+ PDFs with current architecture.

**Q: Why not use embeddings/semantic search?**  
A: BM25 keyword search is faster, requires no ML model loading, and works better for legal terminology that's highly specific.

**Q: How long does deployment take?**  
A: First deploy: 2-5 minutes. Subsequent deployments (on git push): 30-60 seconds.

**Q: Can I use local PDF files on Streamlit Cloud?**  
A: Yes, if under 100MB total. Alternatively, use cloud storage (S3, Google Drive).

**Q: How is caching implemented?**  
A: Global BM25 retriever cached at module level in `retrieve.py`. Persists across Streamlit reruns.

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues, questions, or feature requests:
1. Check [GitHub Issues](https://github.com/Faraz-Ghani/LegalBot/issues)
2. Review [TESTING_GUIDE.md](TESTING_GUIDE.md) and [TEST_PROCEDURE.md](TEST_PROCEDURE.md)
3. Check troubleshooting section above

---

## Credits

- **LLM**: Groq (llama-3.3-70b-versatile)
- **Framework**: Streamlit + LangChain
- **Search**: BM25 from rank_bm25
- **PDF Processing**: PyMuPDF (fitz)

---

**Last Updated**: March 19, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
