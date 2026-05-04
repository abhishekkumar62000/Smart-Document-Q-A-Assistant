# Smart Document Q&A + Action Agent 🤖

A premium, AI-powered document assistant that not only answers your questions but also suggests actionable steps (reminders, tasks, summaries).

## Features
- **Smart PDF Analysis**: Upload multiple PDFs and chat with them using RAG technology.
- **Action Agent**: Automatically detects deadlines, tasks, and follow-ups in the AI's answers.
- **Premium UI**: Clean, glassmorphism-inspired design.

## Setup & Run

1. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   streamlit run app.py
   ```

3. **Usage**:
   - Enter your **OpenAI API Key** in the sidebar.
   - Upload PDF documents.
   - Click "Process Documents".
   - Ask questions! (e.g., "What are the submission requirements?").
   - Look for **cards** appearing below the answer with suggested actions.

## Tech Stack
- **Streamlit**: Frontend
- **LangChain**: Orchestration
- **OpenAI**: LLM & Embeddings
- **FAISS**: Vector Database

---
*Built by Antigravity*
