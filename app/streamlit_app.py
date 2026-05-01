import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.course_assistant import ask_course_assistant
from backend.services.assignment_generator import generate_assignment

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
    st.write("Generate syllabus-aligned assignments and rubrics using AI.")

    col1, col2, col3 = st.columns(3)
    with col1:
        week = st.number_input("Week", min_value=1, max_value=15, value=3)
    with col2:
        topic = st.text_input("Topic", placeholder="Prompt Engineering")
    with col3:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

    if st.button("Generate Assignment"):
        if topic:
            with st.spinner("Step 1: Retrieving syllabus context..."):
                pass
            with st.spinner("Step 2: Generating draft → critiquing → revising..."):
                result = generate_assignment(topic, week, difficulty)

            st.success("Assignment generated successfully!")

            st.markdown("---")
            st.subheader("📋 Final Assignment")
            st.markdown(result["final"])

            st.markdown("---")
            st.subheader("📊 Grading Rubric")
            st.markdown(result["rubric"])

            st.markdown("---")

            st.markdown("---")
            st.subheader("💻 Starter Code")
            st.code(result["starter_code"], language="python")

            st.markdown("---")

            # Download button
            download_content = f"""# Assignment: {topic} (Week {week})
Difficulty: {difficulty}

## Assignment
{result["final"]}

## Grading Rubric
{result["rubric"]}

## Starter Code
```python
{result["starter_code"]}
```
"""
            st.download_button(
                label="⬇️ Download Assignment as Markdown",
                data=download_content,
                file_name=f"week{week}_{topic.replace(' ', '_')}_assignment.md",
                mime="text/markdown"
            )

            st.markdown("---")
            with st.expander("🔍 View AI Reflection Process (Draft → Critique → Final)"):
                st.markdown("**📝 Original Draft:**")
                st.markdown(result["draft"])
                st.markdown("---")
                st.markdown("**🔎 Professor Critique:**")
                st.warning(result["critique"])
                st.markdown("---")
                st.markdown("**📚 Syllabus Context Used:**")
                st.info(result["syllabus_context"])
        else:
            st.warning("Please enter a topic.")

with tab3:
    st.header("🔍 Repo Reviewer")
    st.info("🚧 Coming soon — Multi-agent GitHub repo review")

with tab4:
    st.header("📊 Analytics Dashboard")
    st.info("🚧 Coming soon — BigQuery-powered student performance analytics")

with tab5:
    st.header("⚖️ AI Ethics & Limitations")
    st.info("🚧 Coming soon — Hallucination risk estimator and responsible AI guidelines")
