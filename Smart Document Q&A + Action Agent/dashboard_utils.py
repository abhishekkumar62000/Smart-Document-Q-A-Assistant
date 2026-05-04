import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def show_dashboard(summaries, actions):
    st.title("📊 Smart Insights Dashboard")
    st.markdown("---")
    # Key Insights
    st.header("Key Insights (from Summaries)")
    for doc in summaries:
        st.markdown(f"**{doc['filename']}**: {doc['summary']}")
    st.markdown("---")
    # Deadlines/Tasks
    st.header("Detected Deadlines & Tasks")
    if actions:
        for a in actions:
            st.markdown(f"- **{a.get('label','')}**: {a.get('details','')}")
    else:
        st.info("No actionable deadlines or tasks detected yet.")
    st.markdown("---")
    # Word Cloud
    st.header("Word Cloud of All Summaries")
    all_text = ' '.join([doc['summary'] for doc in summaries])
    if all_text.strip():
        wc = WordCloud(width=600, height=300, background_color='white').generate(all_text)
        fig, ax = plt.subplots()
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No text for word cloud.")
    # (Placeholder) Timeline/Heatmap
    st.header("Timeline/Action Heatmap (Coming Soon)")
    st.info("Visual timeline and action heatmap will be available in a future update.")
