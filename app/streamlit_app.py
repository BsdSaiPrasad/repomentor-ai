import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.course_assistant import ask_course_assistant
from backend.services.assignment_generator import generate_assignment
from backend.services.repo_analyzer import analyze_repo
from backend.db.connection import get_connection as get_db_connection
from sqlalchemy import text

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
    "🤖 AutoDev Agent"
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

    if "assignment_topic" not in st.session_state:
        st.session_state.assignment_topic = ""
    if "assignment_format" not in st.session_state:
        st.session_state.assignment_format = "Lab"

    st.caption("Create a polished assignment pack with a brief, rubric, starter code, and review trace.")

    col1, col2, col3 = st.columns(3)
    with col1:
        week = st.number_input("Week", min_value=1, max_value=15, value=3)
    with col2:
        topic = st.text_input("Topic", placeholder="Prompt Engineering", key="assignment_topic")
    with col3:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

    assignment_format = st.selectbox(
        "Assignment Format",
        ["Lab", "Mini Project", "Notebook", "Code Review", "Build-and-Explain"],
        key="assignment_format"
    )

    provided_context = ""
    if assignment_format == "Code Review":
        provided_context = st.text_area(
            "Provided Code Context",
            placeholder="Paste the repo URL, repo path, file list, or a short description of the code students will review.",
            height=100
        )
        st.caption("Code Review assignments require concrete code context. Without it, the generator will refuse to invent one.")

    if st.button("Generate Assignment"):
        if topic:
            if assignment_format == "Code Review" and not provided_context.strip():
                st.warning("Add provided code context before generating a Code Review assignment.")
                st.stop()
            with st.spinner("Step 1: Retrieving syllabus context..."):
                pass
            with st.spinner("Step 2: Generating draft → critiquing → revising..."):
                result = generate_assignment(topic, week, difficulty, assignment_format, provided_context)

            st.success("Assignment pack generated successfully.")
            st.caption(
                f"Week {result['week']} | {result['topic']} | "
                f"{result['difficulty']} | {result['assignment_format']}"
            )

            download_content = f"""# Assignment: {topic} (Week {week})
Difficulty: {difficulty}
Format: {assignment_format}

## Assignment
{result["final"]}

## Grading Rubric
{result["rubric"]}

## Starter Material
{result["starter_code"]}

## Review Trace

### Original Draft
{result["draft"]}

### Professor Critique
{result["critique"]}

### Student Doubts
{result["student_doubts"]}
"""

            st.markdown("---")
            st.download_button(
                label="⬇️ Download Assignment as Markdown",
                data=download_content,
                file_name=f"week{week}_{topic.replace(' ', '_')}_assignment.md",
                mime="text/markdown"
            )

            assignment_tab, rubric_tab, starter_tab, trace_tab = st.tabs([
                "📋 Assignment",
                "📊 Rubric",
                "💻 Starter Code",
                "🔍 Review Trace"
            ])

            with assignment_tab:
                st.markdown(result["final"])

            with rubric_tab:
                st.markdown(result["rubric"])

            with starter_tab:
                starter_material = result["starter_code"].strip()
                if starter_material.startswith("No starter code needed"):
                    st.info(starter_material)
                else:
                    st.code(result["starter_code"], language="python")

            with trace_tab:
                st.markdown("**📝 Original Draft**")
                st.markdown(result["draft"])
                st.markdown("---")
                st.markdown("**🔎 Professor Critique**")
                st.warning(result["critique"])
                st.markdown("---")
                st.markdown("**🙋 Student Doubts**")
                st.warning(result["student_doubts"])
                st.markdown("---")
                st.markdown("**📚 Syllabus Context Used**")
                st.info(result["syllabus_context"])
        else:
            st.warning("Please enter a topic.")

with tab3:
    st.header("🔍 Repo Reviewer")
    st.write("Paste a local repo path or select a sample repo to analyze.")

    col1, col2 = st.columns(2)
    with col1:
        repo_path = st.text_input("Repo Path", placeholder="sample_repos/good_student")
    with col2:
        sample = st.selectbox("Or pick a sample repo", [
            "-- select --",
            "sample_repos/good_student",
            "sample_repos/average_student",
            "sample_repos/bad_student"
        ])

    if sample != "-- select --":
        repo_path = sample

    if st.button("Analyze Repo"):
        if repo_path:
            st.markdown("---")
            st.subheader("🤖 Agent Status")

            # Create live status placeholders for each agent
            agent_names = ["Code Review Agent", "Security Agent", "Documentation Agent"]
            placeholders = {}
            cols_status = st.columns(3)
            for i, name in enumerate(agent_names):
                with cols_status[i]:
                    placeholders[name] = st.empty()
                    placeholders[name].info(f"🔄 **{name}**\nStatus: Running...")

            # Callback updates the placeholder when each agent finishes
            def on_agent_done(name, score, duration):
                color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
                placeholders[name].success(f"{color} **{name}**\nScore: {score}/100 — {duration}s")

            try:
                report = analyze_repo(repo_path, status_callback=on_agent_done)
            except ValueError as e:
                st.error(f"❌ {str(e)}")
                st.stop()

            st.success(f"✅ Analysis complete! Overall Score: {report['overall_score']}/100 — {report['grade']}")

            st.markdown("---")
            st.subheader("📊 Agent Breakdown")
            cols = st.columns(len(report["breakdown"]))
            for i, agent in enumerate(report["breakdown"]):
                with cols[i]:
                    duration = agent.get("duration", 0)
                    st.metric(label=agent["agent"], value=f"{agent['score']}/100", delta=f"{duration}s")
                    st.caption(agent["summary"])

            st.markdown("---")
            st.subheader("⚠️ All Issues Found")
            if report["all_issues"]:
                security_issues = [i for i in report["all_issues"] if "Security" in i]
                code_issues = [i for i in report["all_issues"] if "Code" in i]
                doc_issues = [i for i in report["all_issues"] if "Documentation" in i]

                if security_issues:
                    st.markdown("🔴 **Security Issues**")
                    for issue in security_issues:
                        st.error(f"🔒 {issue.replace('[Security Agent]', '').strip()}")

                if code_issues:
                    st.markdown("🟡 **Code Quality Issues**")
                    for issue in code_issues:
                        st.warning(f"⚠️ {issue.replace('[Code Review Agent]', '').strip()}")

                if doc_issues:
                    st.markdown("🔵 **Documentation Issues**")
                    for issue in doc_issues:
                        st.info(f"📄 {issue.replace('[Documentation Agent]', '').strip()}")
            else:
                st.success("✅ No issues found — excellent repo!")

            st.markdown("---")
            with st.expander("🔍 Detailed Agent Reports"):
                for agent in report["breakdown"]:
                    score = agent["score"]
                    color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
                    st.markdown(f"{color} **{agent['agent']}** — Score: {agent['score']}/100")
                    st.write(agent["summary"])
                    if agent["issues"]:
                        for issue in agent["issues"]:
                            st.markdown(f"- {issue}")
                    st.markdown("---")
        else:
            st.warning("Please enter a repo path or select a sample repo.")

with tab4:
    st.header("📊 Analytics Dashboard")

    try:
        with get_db_connection() as conn:
            reviews = conn.execute(text("SELECT repo_path, overall_score, grade, created_at FROM repo_reviews ORDER BY created_at DESC")).fetchall()

        if not reviews:
            st.info("No reviews yet. Analyze a repo first to see analytics here.")
        else:
            scores = [r[1] for r in reviews]
            total = len(reviews)
            avg_score = round(sum(scores) / total, 1)
            best = max(scores)
            worst = min(scores)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Reviews", total)
            col2.metric("Average Score", avg_score)
            col3.metric("Best Score", best)
            col4.metric("Worst Score", worst)

            st.markdown("---")

            import plotly.graph_objects as go

            labels = [f"{r[0].split('/')[-1]} ({str(r[3])[:10]})" for r in reviews]
            values = [r[1] for r in reviews]
            colors = ["#2ecc71" if v >= 75 else "#f39c12" if v >= 60 else "#e74c3c" for v in values]

            fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors))
            fig.update_layout(
                title="Score per Repo Review",
                xaxis_title="Repo",
                yaxis_title="Score",
                yaxis=dict(range=[0, 100]),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            st.subheader("📋 Grade Distribution")
            grade_counts = {}
            for r in reviews:
                grade_counts[r[2]] = grade_counts.get(r[2], 0) + 1

            gcol1, gcol2, gcol3, gcol4 = st.columns(4)
            gcol1.metric("🟢 Excellent", grade_counts.get("Excellent", 0))
            gcol2.metric("🟡 Good", grade_counts.get("Good", 0))
            gcol3.metric("🟠 Needs Improvement", grade_counts.get("Needs Improvement", 0))
            gcol4.metric("🔴 Poor", grade_counts.get("Poor", 0))

            st.markdown("---")

            st.subheader("🕓 Recent Reviews")
            for r in reviews[:10]:
                score = r[1]
                color = "🟢" if score >= 75 else "🟡" if score >= 60 else "🔴"
                st.write(f"{color} **{r[0]}** — Score: {score} — Grade: {r[2]} — {str(r[3])[:16]}")

    except Exception as e:
        st.error(f"Could not load analytics: {e}")

with tab5:
    from backend.autodev.orchestrate import run_autodev, AGENT_ORDER
    from backend.autodev.graph_component import build_graph_html
    import streamlit.components.v1 as components

    st.header("🤖 AutoDev Agent")
    st.write("Describe any software idea in plain English. 7 AI agents will autonomously plan, build, test, secure, and deploy it.")

    st.markdown("---")

    # Example ideas
    st.caption("💡 Try: *\"A CLI todo app with JSON persistence\"* or *\"A REST API for a book library\"* or *\"A Slack bot that summarizes daily standups\"*")

    idea = st.text_area(
        "Your idea:",
        placeholder="A CLI tool that monitors a folder and alerts when new files appear",
        height=80,
    )

    col_run, col_clear = st.columns([1, 5])
    run_btn = col_run.button("🚀 Build It", type="primary")

    if run_btn:
        if not idea.strip():
            st.warning("Please describe your idea first.")
        else:
            st.markdown("---")
            st.subheader("🔄 Live Agent Workflow")

            # Initialize all agents as waiting
            agent_statuses = {a: "waiting" for a in AGENT_ORDER}
            graph_placeholder = st.empty()

            def render_graph():
                html = build_graph_html(agent_statuses)
                graph_placeholder.empty()
                with graph_placeholder:
                    components.html(html, height=590, scrolling=False)

            render_graph()

            # Observability sidebar metrics
            st.markdown("---")
            st.subheader("📡 Observability")
            obs_cols = st.columns(len(AGENT_ORDER))
            obs_placeholders = {a: obs_cols[i].empty() for i, a in enumerate(AGENT_ORDER)}

            for name in AGENT_ORDER:
                obs_placeholders[name].metric(name, "—", delta=None)

            # Status text log
            log_placeholder = st.empty()
            log_lines = []

            def on_update(agent_name, status, snippet):
                agent_statuses[agent_name] = status
                render_graph()
                icon = {"running": "🔵", "done": "✅", "failed": "❌"}.get(status, "⚪")
                log_lines.append(f"{icon} **{agent_name}** — {status}")
                log_placeholder.markdown("\n\n".join(log_lines))

            # Run the pipeline
            pipeline = run_autodev(idea, on_update=on_update)

            # Update obs metrics with final data
            for agent_name in AGENT_ORDER:
                r = pipeline["results"].get(agent_name)
                if r:
                    icon = "✅" if r.status == "done" else "❌"
                    obs_placeholders[agent_name].metric(
                        f"{icon} {agent_name}",
                        f"{r.tokens} tok",
                        delta=f"{r.duration}s",
                    )

            st.markdown("---")
            # Summary banner
            if pipeline["success"]:
                st.success(f"✅ All {pipeline['total_agents']} agents completed — {pipeline['total_tokens']} tokens — {pipeline['total_duration']}s total")
            else:
                st.warning(f"⚠️ {pipeline['done_count']}/{pipeline['total_agents']} agents succeeded")

            st.markdown("---")

            # Tabbed output per agent
            result_tabs = st.tabs([f"{a}" for a in AGENT_ORDER])
            tab_icons = {
                "Orchestrator": "🧠",
                "Architect":    "🏗️",
                "Coder":        "💻",
                "Tester":       "🧪",
                "Security":     "🔒",
                "Git Agent":    "📦",
                "Deploy Agent": "🚀",
            }
            for i, agent_name in enumerate(AGENT_ORDER):
                with result_tabs[i]:
                    r = pipeline["results"].get(agent_name)
                    if not r:
                        st.error("Agent did not run.")
                        continue
                    icon = tab_icons.get(agent_name, "")
                    st.markdown(f"### {icon} {agent_name}")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Status", r.status.upper())
                    col_m2.metric("Tokens", r.tokens)
                    col_m3.metric("Latency", f"{r.duration}s")

                    if r.status == "done":
                        if agent_name in ("Coder", "Tester", "Git Agent", "Deploy Agent"):
                            st.code(r.output, language="python" if agent_name in ("Coder", "Tester") else "yaml")
                        else:
                            st.markdown(r.output)
                    else:
                        st.error(f"Error: {r.error}")

                    with st.expander("🔍 Prompt sent to this agent"):
                        st.text(r.prompt or "(not captured)")

            # Download full report
            st.markdown("---")
            full_report = f"# AutoDev Report — {idea[:60]}\n\n"
            for agent_name in AGENT_ORDER:
                r = pipeline["results"].get(agent_name)
                full_report += f"## {agent_name}\n\n{r.output if r else 'Failed'}\n\n---\n\n"
            st.download_button(
                "⬇️ Download Full Report",
                data=full_report,
                file_name="autodev_report.md",
                mime="text/markdown",
            )
