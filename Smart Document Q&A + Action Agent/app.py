
import streamlit as st
from dotenv import load_dotenv
from utils import PDFProcessor, RAGEngine, ActionAgent
from langchain_openai import ChatOpenAI
from stt_tts_utils import speech_to_text, text_to_speech
from pdf_annotator_component import pdf_annotator_ui
from dashboard_utils import show_dashboard

# Page Configuration
st.set_page_config(page_title="Smart Doc Q&A", page_icon="🤖", layout="wide")


# --- THEME TOGGLE & ENHANCED CSS ---
import streamlit.components.v1 as components

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

def toggle_theme():
    st.session_state.theme_mode = "dark" if st.session_state.theme_mode == "light" else "light"

with st.sidebar:
    st.markdown("---")
    theme_label = "🌙 Switch to Dark Mode" if st.session_state.theme_mode == "light" else "☀️ Switch to Light Mode"
    st.button(theme_label, on_click=toggle_theme, key="theme_toggle_btn")

custom_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');
    .stApp {{
        background: linear-gradient(135deg, #1a0036 0%, #0f2027 40%, #2c5364 100%);
        color: #e0e0ff;
        font-family: 'Orbitron', 'Inter', sans-serif;
        min-height: 100vh;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(135deg, #2d0036 0%, #3a3a5a 100%);
        color: #fff;
        border-radius: 0 20px 20px 0;
        box-shadow: 2px 0 16px 0 rgba(80,0,120,0.25);
    }}
    .stChatMessage {{
        background: linear-gradient(120deg, #2d0036 0%, #23232e 60%, #00cfff 100%);
        color: #e0e0ff;
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(0,255,255,0.10), 0 1.5px 8px rgba(80,0,120,0.10);
        padding: 16px;
        margin-bottom: 16px;
        border: 1.5px solid #7f5cff;
        transition: box-shadow 0.3s;
    }}
    .stChatMessage:hover {{
        box-shadow: 0 0 24px 2px #7f5cff, 0 1.5px 8px rgba(80,0,120,0.10);
    }}
    .action-card {{
        background: linear-gradient(135deg, #2d0036 0%, #7f5cff 100%);
        color: #fff;
        padding: 18px;
        border-radius: 16px;
        margin-top: 14px;
        box-shadow: 0 6px 24px 0 #7f5cff, 0 1.5px 8px rgba(80,0,120,0.10);
        border: 2px solid #00cfff;
        animation: neon-glow 1.5s infinite alternate;
    }}
    @keyframes neon-glow {{
        from {{ box-shadow: 0 0 8px #00cfff, 0 1.5px 8px rgba(80,0,120,0.10); }}
        to {{ box-shadow: 0 0 32px #7f5cff, 0 1.5px 8px rgba(80,0,120,0.10); }}
    }}
    .action-title {{
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 7px;
        letter-spacing: 1px;
        color: #00cfff;
        text-shadow: 0 0 8px #7f5cff;
    }}
    .stTextInput>div>div>input {{
        border-radius: 12px;
        background: #1a0036;
        color: #00cfff;
        border: 2px solid #7f5cff;
        font-size: 1.1em;
        box-shadow: 0 0 8px #7f5cff;
        transition: box-shadow 0.3s;
    }}
    .stTextInput>div>div>input:focus {{
        box-shadow: 0 0 16px #00cfff;
    }}
    .stButton>button {{
        border-radius: 12px;
        font-weight: 700;
        width: 100%;
        background: linear-gradient(90deg, #7f5cff 0%, #00cfff 100%);
        color: #fff;
        border: none;
        box-shadow: 0 0 12px #7f5cff;
        font-size: 1.1em;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        animation: button-pop 1.2s infinite alternate;
    }}
    .stButton>button:hover {{
        background: linear-gradient(90deg, #00cfff 0%, #7f5cff 100%);
        transform: scale(1.04);
        box-shadow: 0 0 32px #00cfff;
    }}
    @keyframes button-pop {{
        from {{ box-shadow: 0 0 8px #7f5cff; }}
        to {{ box-shadow: 0 0 24px #00cfff; }}
    }}
    .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stCaption, .stDataFrame, .stTable {{
        color: #00cfff !important;
        text-shadow: 0 0 8px #7f5cff;
    }}
    .stDownloadButton>button {{
        background: linear-gradient(90deg, #7f5cff 0%, #00cfff 100%);
        color: #fff;
        border-radius: 12px;
        font-weight: 700;
        box-shadow: 0 0 12px #00cfff;
        transition: box-shadow 0.2s;
    }}
    .stDownloadButton>button:hover {{
        box-shadow: 0 0 32px #7f5cff;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def main():
    # --- Dashboard Navigation ---
    dashboard_mode = st.sidebar.radio("Navigation", ["Q&A", "Insights Dashboard"], index=0)
    load_dotenv()

    # --- Collaborative Session State ---
    if "session_code" not in st.session_state:
        import random, string
        st.session_state.session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    if "joined_code" not in st.session_state:
        st.session_state.joined_code = ""

    # Initialize session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "process_complete" not in st.session_state:
        st.session_state.process_complete = False



    # --- Sidebar ---
    with st.sidebar:
        st.title("📂 DocuMind Agent")
        st.markdown("---")
        # --- AI Assistant Persona Selector ---
        st.markdown("### 🧑‍💼 AI Assistant Persona")
        persona = st.selectbox(
            "Choose your assistant's persona:",
            ["Default","Legal Expert","Project Manager","Teacher","Medical Advisor","Data Analyst"]
        )
        st.session_state.persona = persona
        st.markdown("---")
        # --- Document Search & Filters ---
        st.markdown("### 🔎 Document Search")
        search_query = st.text_input("Search documents or Q&A...", key="doc_search")
        filter_author = st.text_input("Filter by Author (optional)", key="filter_author")
        filter_topic = st.text_input("Filter by Topic (optional)", key="filter_topic")
        st.markdown("---")
        # --- Collaborative Session ---
        st.markdown("#### 🤝 Collaborative Session")
        st.info(f"Your Session Code: **{st.session_state.session_code}**")
        join_code = st.text_input("Join a session (enter code):", value=st.session_state.joined_code, key="join_code_input")
        if st.button("Join Session"):
            if join_code and join_code != st.session_state.session_code:
                st.session_state.session_code = join_code
                st.session_state.joined_code = join_code
                st.success(f"Joined session {join_code}")
            elif join_code == st.session_state.session_code:
                st.warning("You are already in this session.")
            else:
                st.error("Please enter a valid session code.")

        # --- Developer Credit ---
        st.markdown("---")
        st.markdown('''<div style="text-align:center; margin-top:2em;">
            <span style="font-size:1.1em; color:#00cfff; font-weight:700;">Developed by</span><br>
            <span style="font-size:1.2em; color:#7f5cff; font-weight:900; letter-spacing:1px;">Abhishek Kumar</span><br>
            <a href="https://github.com/abhishekkumar62000" target="_blank" style="color:#00cfff; text-decoration:none; font-size:1em;">github.com/abhishekkumar62000</a>
            </div>''', unsafe_allow_html=True)
        st.markdown("---")
        # API Key Input
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if not api_key:
            st.warning("Please enter your OpenAI API Key to continue.")
        st.markdown("### 📤 Upload Documents & Images")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here", accept_multiple_files=True, type="pdf"
        )
        image_files = st.file_uploader(
            "Upload images (JPG, PNG, etc.) for OCR", accept_multiple_files=True, type=["jpg", "jpeg", "png"]
        )
        if st.button("Process Documents"):
            if not api_key:
                st.error("API Key required!")
            elif not pdf_docs and not image_files:
                st.error("Please upload at least one PDF or image.")
            else:
                with st.spinner("Processing files and generating insights..."):
                    # 1. Get PDF Texts (list of (filename, text))
                    pdf_texts = PDFProcessor.get_pdf_text(pdf_docs) if pdf_docs else []
                    # 1b. OCR for images
                    ocr_texts = []
                    if image_files:
                        try:
                            import pytesseract
                            from PIL import Image
                            for img_file in image_files:
                                img = Image.open(img_file)
                                text = pytesseract.image_to_string(img)
                                ocr_texts.append((img_file.name, text))
                        except Exception as e:
                            st.error(f"OCR failed: {e}")
                    # 2. Summarize each document and image
                    summaries = []
                    for filename, text in pdf_texts + ocr_texts:
                        summary = PDFProcessor.summarize_text(text, api_key)
                        summaries.append({"filename": filename, "summary": summary})
                    st.session_state.summaries = summaries
                    # 3. Get Text Chunks (for all docs and images combined)
                    all_text = "\n\n".join([t for _, t in pdf_texts + ocr_texts])
                    text_chunks = PDFProcessor.get_text_chunks(all_text)
                    # 4. Create Vector Store
                    vectorstore = RAGEngine.get_vectorstore(text_chunks, api_key)
                    # 5. Create Conversation Chain
                    st.session_state.conversation = RAGEngine.get_conversation_chain(vectorstore, api_key)
                    st.session_state.process_complete = True
                    st.success("Analysis Complete! You can now ask questions.")


    # --- Main Content ---
    if dashboard_mode == "Q&A":
        st.markdown('''
        <div style="text-align:center;margin-bottom:0.5em;">
            <span class="animated-title">🤖 Smart Document Assistant</span>
            <div class="animated-subtitle">Your AI-powered Q&A, Actions & Insights Hub</div>
        </div>
        <style>
        .animated-title {
            font-size: 2.8em;
            font-weight: 900;
            background: linear-gradient(90deg, #00cfff 0%, #7f5cff 40%, #ff00cc 70%, #00ffb3 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-move 3s ease-in-out infinite, title-pop 1.2s infinite alternate;
            letter-spacing: 2px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.18);
            display: inline-block;
            filter: none;
        }
        @keyframes gradient-move {
            0% {background-position:0% 50%}
            50% {background-position:100% 50%}
            100% {background-position:0% 50%}
        }
        @keyframes title-pop {
            from {transform: scale(1);}
            to {transform: scale(1.06);}
        }
        .animated-subtitle {
            font-size: 1.25em;
            color: #00cfff;
            margin-top: 0.2em;
            letter-spacing: 1px;
            text-shadow: 0 1px 4px #7f5cff;
            animation: subtitle-fade 2.5s infinite alternate;
        }
        @keyframes subtitle-fade {
            from {opacity: 0.7;}
            to {opacity: 1;}
        }
        </style>
        ''', unsafe_allow_html=True)

        # --- Live Team Chat ---
        from live_chat_utils import live_chat_ui, comment_thread_ui
        with st.expander("💬 Team Live Chat", expanded=False):
            live_chat_ui()

        # --- Document Search Results ---
        if 'search_query' in locals() and search_query.strip():
            st.markdown(f"### 🔎 Search Results for: `{search_query}`")
            results = []
            # Search in summaries
            for doc in st.session_state.get('summaries', []):
                if search_query.lower() in doc['summary'].lower() or \
                   (filter_author and filter_author.lower() in doc.get('author','').lower()) or \
                   (filter_topic and filter_topic.lower() in doc.get('summary','').lower()):
                    results.append(doc)
            # Search in chat history
            for i, msg in enumerate(st.session_state.get('chat_history', [])):
                if hasattr(msg, 'content') and search_query.lower() in msg.content.lower():
                    results.append({'filename': f'Chat Message #{i+1}', 'summary': msg.content})
            if results:
                for res in results:
                    st.markdown(f"**{res.get('filename','Result')}**: {res.get('summary','')}")
            else:
                st.info("No results found.")
            st.markdown("---")

    # --- Document Summaries & Insights Panel ---
    if "summaries" in st.session_state and st.session_state.summaries:
        with st.expander("📑 Document Summaries & Insights", expanded=True):
            for doc in st.session_state.summaries:
                st.markdown(f"**{doc['filename']}**")
                st.markdown(doc['summary'])
                # PDF Annotation UI (demo)
                if "pdf_docs" in locals() and doc['filename'] in [f.name for f in pdf_docs]:
                    pdf_file = [f for f in pdf_docs if f.name == doc['filename']][0]
                    pdf_annotator_ui(pdf_file)
                # Comment thread for each document
                comment_thread_ui(doc['filename'])
                st.markdown("---")

    # --- Multi-Document Comparison Helper ---
    if "summaries" in st.session_state and len(st.session_state.summaries) > 1:
        st.markdown(":mag: **Tip:** You can ask questions like 'What are the main differences between Document A and Document B?' or 'Compare the key points of all uploaded documents.'")

    # Display Chat History
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)
                # Check for attached actions in session state (logic handled below during generation)



    # --- Collaborative Session Share ---
    st.markdown(f"**Session Code:** `{st.session_state.session_code}`  ")
    st.markdown("Share this code with others to join your Q&A session!")

    # --- Meeting Minutes & Action Items ---
    from meeting_minutes_utils import meeting_minutes_ui
    if st.session_state.get('chat_history'):
        meeting_minutes_ui(st.session_state['chat_history'], api_key)


    # --- Voice Input (Speech-to-Text) ---
    st.markdown("#### 🎤 Voice Input (Optional)")
    audio_bytes = st.audio_recorder("Record your question (click mic)", format="wav") if hasattr(st, "audio_recorder") else None
    user_question = st.chat_input("Ask a question about your documents...")
    if audio_bytes and api_key:
        with st.spinner("Transcribing audio..."):
            transcript = speech_to_text(audio_bytes, api_key)
            st.success(f"Recognized: {transcript}")
            user_question = transcript

    if user_question and st.session_state.conversation:
        if not api_key:
            st.error("Please enter API Key in sidebar.")
            return

        # Add user message to UI immediately
        with st.chat_message("user"):
            st.write(user_question)

        # --- Collaborative Session: Store chat history per session code ---
        if "all_sessions" not in st.session_state:
            st.session_state.all_sessions = {}
        session_key = st.session_state.session_code
        if session_key not in st.session_state.all_sessions:
            st.session_state.all_sessions[session_key] = []

        # Get Response
        # Persona prompt injection
        persona_prompt = ""
        if st.session_state.get('persona') and st.session_state['persona'] != "Default":
            persona_prompt = f"You are acting as a {st.session_state['persona']}. "
        response = st.session_state.conversation({'question': persona_prompt + user_question})
        st.session_state.chat_history = response['chat_history']
        st.session_state.all_sessions[session_key] = st.session_state.chat_history

        answer = response['answer']


        # Display Assistant Response
        with st.chat_message("assistant"):
            st.write(answer)

            # --- Voice Output (Text-to-Speech) ---
            st.markdown("**🔊 Listen to Answer:**")
            if st.button("Play Answer Audio", key=f"tts_{len(st.session_state.chat_history)}"):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(answer)
                    st.audio(audio_bytes, format="audio/mp3")

            # --- Actionable Smart Suggestions ---
            st.markdown("**Smart Suggestions:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Set Reminder", key=f"reminder_{len(st.session_state.chat_history)}"):
                    st.info("Reminder feature coming soon!")
            with col2:
                if st.button("Export Answer", key=f"export_{len(st.session_state.chat_history)}"):
                    st.download_button("Download", answer, file_name="answer.txt")
            with col3:
                if st.button("Share via Email", key=f"share_{len(st.session_state.chat_history)}"):
                    st.info("Email sharing feature coming soon!")
            with col4:
                if st.button("Add to Notes", key=f"notes_{len(st.session_state.chat_history)}"):
                    if "notes" not in st.session_state:
                        st.session_state["notes"] = []
                    st.session_state["notes"].append(answer)
                    st.success("Added to notes!")


            # --- Action Agent Trigger ---
            import urllib.parse
            with st.spinner("Checking for actions..."):
                action_data = ActionAgent.analyze_for_actions(user_question, answer, api_key)
                if action_data and action_data.get("actions"):
                    st.markdown("### ⚡ Recommended Actions")
                    for idx, action in enumerate(action_data["actions"]):
                        label = action.get('label', '')
                        details = action.get('details', '')
                        action_type = action.get('type', 'Action')
                        # Google Calendar event creation link
                        cal_url = (
                            "https://calendar.google.com/calendar/render?action=TEMPLATE"
                            f"&text={urllib.parse.quote(label)}"
                            f"&details={urllib.parse.quote(details)}"
                        )
                        st.markdown(f"""
                        <div class="action-card">
                            <div class="action-title">{action_type}</div>
                            <b>{label}</b><br>
                            {details}<br>
                            <a href="{cal_url}" target="_blank">
                                <button style='margin-top:8px;background:#34a853;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;'>Add to Google Calendar</button>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

    elif user_question and not st.session_state.conversation:
        st.info("Please upload and process documents first.")

if __name__ == '__main__':
    main()
