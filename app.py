import io
import contextlib
import traceback
import os
from dotenv import load_dotenv

# 1. Load the hidden API keys FIRST
load_dotenv()

# 2. THEN import Streamlit and your pipeline
import streamlit as st
from pipeline import run_research_pipeline

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)

# ----------------------------------------------------------------------------
# Minimal custom styling
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .main .block-container { padding-top: 2rem; max-width: 1000px; }
        .step-log {
            background-color: #0e1117;
            color: #d1d5db;
            border-radius: 8px;
            padding: 1rem;
            font-family: "Source Code Pro", monospace;
            font-size: 0.8rem;
            max-height: 320px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        .report-box {
            background-color: #f8f9fa;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.5rem;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {topic, state, logs}

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("🔎 Research Assistant")
    st.caption("Search Agent → Reader Agent → Writer → Critic")

    st.markdown("---")
    st.subheader("Past Runs")
    if not st.session_state.history:
        st.caption("No runs yet. Your history will show up here.")
    else:
        for i, run in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            if st.button(f"📄 {run['topic'][:40]}", key=f"hist_{idx}"):
                st.session_state.selected_run = idx

    st.markdown("---")
    if st.button("🗑️ Clear history"):
        st.session_state.history = []
        st.session_state.pop("selected_run", None)
        st.rerun()

# ----------------------------------------------------------------------------
# Header + input
# ----------------------------------------------------------------------------
st.title("Multi-Agent Research Pipeline")
st.write(
    "Enter a topic below. The pipeline will search the web, scrape the most "
    "relevant source, draft a report, and have it reviewed by a critic agent."
)

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of quantum computing on cryptography",
    )
    submitted = st.form_submit_button("🚀 Run Research Pipeline")

# ----------------------------------------------------------------------------
# Run pipeline
# ----------------------------------------------------------------------------
if submitted:
    if not topic or not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        status_box = st.status("Starting pipeline...", expanded=True)
        log_placeholder = status_box.empty()
        log_buffer = io.StringIO()

        result_state = None
        error_msg = None

        try:
            status_box.update(label="Running agents — this can take a minute...")
            with contextlib.redirect_stdout(log_buffer):
                result_state = run_research_pipeline(topic.strip())
            log_placeholder.markdown(
                f'<div class="step-log">{log_buffer.getvalue()}</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            error_msg = f"{e}\n\n{traceback.format_exc()}"
            log_placeholder.markdown(
                f'<div class="step-log">{log_buffer.getvalue()}</div>',
                unsafe_allow_html=True,
            )

        if error_msg:
            status_box.update(label="Pipeline failed", state="error")
            st.error("The pipeline crashed. See details below.")
            with st.expander("Error details"):
                st.code(error_msg)
        elif result_state and "error" in result_state:
            status_box.update(label="Pipeline halted", state="error")
            st.error(result_state["error"])
        else:
            status_box.update(label="Pipeline complete ✅", state="complete")
            st.session_state.history.append(
                {
                    "topic": topic.strip(),
                    "state": result_state,
                    "logs": log_buffer.getvalue(),
                }
            )
            st.session_state.selected_run = len(st.session_state.history) - 1

# ----------------------------------------------------------------------------
# Display selected result
# ----------------------------------------------------------------------------
selected_idx = st.session_state.get("selected_run")
if selected_idx is not None and st.session_state.history:
    run = st.session_state.history[selected_idx]
    state = run["state"]

    st.markdown("---")
    st.header(f"Results: {run['topic']}")

    tab_report, tab_critic, tab_search, tab_scraped, tab_logs = st.tabs(
        ["📝 Final Report", "🧐 Critic Feedback", "🔍 Search Results", "📖 Scraped Content", "🖥️ Run Logs"]
    )

    with tab_report:
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown(state.get("report", "_No report generated._"))
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download report as Markdown",
            data=str(state.get("report", "")),
            file_name=f"{run['topic'][:40].strip().replace(' ', '_')}_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        st.markdown(state.get("feedback", "_No feedback generated._"))

    with tab_search:
        st.text(state.get("search_results", "No search results captured."))

    with tab_scraped:
        st.text(state.get("scraped_content", "No scraped content captured."))

    with tab_logs:
        st.markdown(
            f'<div class="step-log">{run["logs"]}</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("Run a research topic above, or select a past run from the sidebar.")
