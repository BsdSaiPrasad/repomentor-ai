import streamlit as st

st.set_page_config(
    page_title="RepoMentor AI",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 RepoMentor AI")
st.caption("GenAI TA Toolkit for CMSC389A — Modern Software Development with GenAI")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 Course Assistant",
    "📝 Assignment Builder",
    "🔍 Repo Reviewer",
    "📊 Analytics Dashboard",
    "⚖️ AI Ethics & Limitations"
])

with tab1:
    st.header("📚 Course Assistant")
    st.info("🚧 Coming soon — RAG-powered Q&A over course syllabus and schedule")

with tab2:
    st.header("📝 Assignment Builder")
    st.info("🚧 Coming soon — Generate assignments, rubrics, and starter code")

with tab3:
    st.header("🔍 Repo Reviewer")
    st.info("🚧 Coming soon — Multi-agent GitHub repo review")

with tab4:
    st.header("📊 Analytics Dashboard")
    st.info("🚧 Coming soon — BigQuery-powered student performance analytics")

with tab5:
    st.header("⚖️ AI Ethics & Limitations")
    st.info("🚧 Coming soon — Hallucination risk estimator and responsible AI guidelines")
