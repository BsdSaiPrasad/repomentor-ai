import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.course_assistant import ask_course_assistant

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
    st.write("Ask any question about CMSC389A — topics, schedule, assignments.")
    
    question = st.text_input("Your question:", placeholder="What topics are covered in Week 9?")
    
    if st.button("Ask"):
        if question:
            with st.spinner("Searching course materials..."):
                result = ask_course_assistant(question)
            st.success("Answer:")
            st.write(result["answer"])
            with st.expander("📄 Sources used"):
                for i, chunk in enumerate(result["sources"]):
                    st.text(f"Chunk {i+1}: {chunk[:200]}...")
        else:
            st.warning("Please enter a question.")

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
