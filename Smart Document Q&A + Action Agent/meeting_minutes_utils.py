import streamlit as st
from utils import ActionAgent

def generate_meeting_minutes(chat_history, api_key):
    # Concatenate all Q&A pairs
    transcript = ""
    for i in range(0, len(chat_history), 2):
        q = chat_history[i].content if i < len(chat_history) else ""
        a = chat_history[i+1].content if i+1 < len(chat_history) else ""
        transcript += f"Q: {q}\nA: {a}\n"
    # Use LLM to summarize as meeting minutes and action items
    prompt = f"""
    You are an expert meeting assistant. Given the following Q&A transcript, generate:
    - A concise meeting summary (3-5 bullet points)
    - A list of key decisions
    - A list of action items (with deadlines if mentioned)
    Transcript:
    {transcript}
    """
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(temperature=0, openai_api_key=api_key, model_name='gpt-3.5-turbo', max_tokens=512)
    response = llm.invoke(prompt)
    return response.content.strip()

def meeting_minutes_ui(chat_history, api_key):
    st.markdown("### 📝 Generate Meeting Minutes & Action Items")
    if st.button("Generate Minutes & Actions"):
        with st.spinner("Generating meeting minutes and action items..."):
            minutes = generate_meeting_minutes(chat_history, api_key)
            st.success("Meeting minutes generated!")
            st.markdown(minutes)
            st.download_button("Download as TXT", minutes, file_name="meeting_minutes.txt")
