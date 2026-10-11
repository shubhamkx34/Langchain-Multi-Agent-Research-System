# app.py
import streamlit as st
import time
from src.Agents.Agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimalist CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Reset */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #e2e8f0;
}

.stApp {
    background-color: #0b0f19;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2.5rem 3rem 4rem;
    max-width: 1200px;
}

/* Header */
.header-container {
    margin-bottom: 2rem;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 1.5rem;
}

.badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.2);
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.75rem;
}

.title-text {
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #f8fafc;
    margin: 0 0 0.4rem;
}

.subtitle-text {
    font-size: 0.92rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.5;
}

/* Form Container */
.input-box {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.stTextInput > div > div > input {
    background: #0b0f19 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
    font-size: 0.92rem !important;
    padding: 0.7rem 0.9rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: none !important;
}

.stTextInput > label {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #cbd5e1 !important;
}

/* Button */
.stButton > button {
    background: #0284c7 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.4rem !important;
    transition: background-color 0.15s ease !important;
    width: 100%;
}

.stButton > button:hover {
    background: #0369a1 !important;
}

/* Pipeline Step Cards */
.step-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s ease;
}

.step-card.active {
    border-color: #38bdf8;
    background: #0f172a;
}

.step-card.done {
    border-color: #22c55e;
    background: #0f172a;
}

.step-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.step-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #64748b;
    margin-right: 0.6rem;
}

.step-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #f1f5f9;
}

.step-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
}

.status-waiting { color: #475569; }
.status-running { color: #38bdf8; }
.status-done    { color: #22c55e; }

/* Panels */
.output-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}

.panel-header {
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1f2937;
}

.panel-header.accent { color: #38bdf8; }
.panel-header.success { color: #22c55e; }

.raw-content {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #cbd5e1;
    white-space: pre-wrap;
    line-height: 1.6;
}

.footer-text {
    font-size: 0.75rem;
    color: #475569;
    text-align: center;
    margin-top: 3.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Helper: Render Step Card ──────────────────────────────────────────────────
def render_step_card(step_id: str, title: str, state: str, description: str = ""):
    status_display = {
        "waiting": ("PENDING", "status-waiting"),
        "running": ("RUNNING", "status-running"),
        "done":    ("COMPLETED", "status-done"),
    }
    label, status_class = status_display.get(state, ("PENDING", "status-waiting"))
    card_class = {"running": "active", "done": "done"}.get(state, "")

    st.markdown(f"""
    <div class="step-card {card_class}">
        <div class="step-header">
            <div>
                <span class="step-id">{step_id}</span>
                <span class="step-title">{title}</span>
            </div>
            <span class="step-status {status_class}">{label}</span>
        </div>
        {"<div style='font-size:0.78rem; color:#64748b; margin-top:0.3rem; margin-left:1.6rem;'>"+description+"</div>" if description else ""}
    </div>
    """, unsafe_allow_html=True)

# ── Session State Management ──────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <span class="badge">MULTI-AGENT SYSTEM</span>
    <h1 class="title-text">Research Intelligence Engine</h1>
    <p class="subtitle-text">Autonomous orchestration: Search, Deep Scraping, Report Synthesis, and Critique.</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_pipeline = st.columns([5, 4], gap="large")

with col_input:
    st.markdown('<div class="input-box">', unsafe_allow_html=True)
    topic = st.text_input(
        "Enter Research Topic",
        placeholder="e.g., Autonomous AI agents in enterprise workflows 2026",
        key="topic_input",
    )
    run_btn = st.button("Start Research Workflow", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_pipeline:
    st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.75rem;'>Execution Status</p>", unsafe_allow_html=True)
    
    r = st.session_state.results

    def get_step_status(step_name):
        if not r:
            return "waiting"
        steps_order = ["search", "reader", "writer", "critic"]
        if step_name in r:
            return "done"
        if st.session_state.running:
            for active_step in steps_order:
                if active_step not in r:
                    return "running" if active_step == step_name else "waiting"
        return "waiting"

    render_step_card("01", "Search Agent", get_step_status("search"), "Scores and identifies top source targets")
    render_step_card("02", "Reader Agent", get_step_status("reader"), "Scrapes and synthesizes target content")
    render_step_card("03", "Writer Chain", get_step_status("writer"), "Compiles multi-source research report")
    render_step_card("04", "Critic Chain", get_step_status("critic"), "Evaluates coherence and scores depth")

# ── Pipeline Execution ────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic to begin.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # Step 1: Search Agent
    with st.spinner("Search Agent: Querying Tavily & calculating relevance scores..."):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [
                ("user", f"Find recent, reliable and detailed information about: {topic_val}. You MUST use the 'web_search' tool. In your final output, you MUST explicitly copy the ENTIRE 'Top Target URLs for Deep Scraping' section AND the 'All Search Results & Snippets' section exactly as the tool provides them.")
            ]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    # Step 2: Reader Agent
    with st.spinner("Reader Agent: Scraping top targets & synthesizing content..."):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [(
                "user",
                f"From the search results below for '{topic_val}', locate the 'Top Target URLs for Deep Scraping'. "
                f"You MUST use the 'scrape_url' tool to read them. "
                f"CRITICAL INSTRUCTION: After the tool returns the text, you MUST write a detailed, multi-paragraph synthesis of the extracted information in your final response. Do not output raw HTML or empty text.\n\n"
                f"Search Results:\n{results['search']}"
            )]
        })
        results["reader"] = rr["messages"][-1].content

        # Fallback to prevent downstream failures on empty LLM responses
        if not results["reader"].strip():
            results["reader"] = "The Reader Agent failed to summarize the scraped content. Rely on the broad search snippets provided."

        st.session_state.results = dict(results)

    # Step 3: Writer Chain
    with st.spinner("Writer Chain: Synthesizing multi-source report..."):
        research_combined = (
            f"SEARCH RESULTS (Broad Context) :\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT (Deep Evidence) :\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # Step 4: Critic Chain
    with st.spinner("Critic Chain: Reviewing and scoring the final report..."):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()

# ── Display Results ───────────────────────────────────────────────────────────
res = st.session_state.results

if res:
    st.markdown("<hr style='border:none; border-top:1px solid #1e293b; margin:2.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:1.25rem; font-weight:700; color:#f8fafc; margin-bottom:1.5rem;'>Synthesized Deliverables</h2>", unsafe_allow_html=True)

    # Final Report
    if "writer" in res:
        st.markdown("""
        <div class="output-card">
            <div class="panel-header accent">Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(res["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="Download Report (.md)",
            data=res["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic Feedback
    if "critic" in res:
        st.markdown("""
        <div class="output-card">
            <div class="panel-header success">Critic Evaluation</div>
        """, unsafe_allow_html=True)
        st.markdown(res["critic"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Raw Execution Logs (Collapsible)
    with st.expander("Inspect Raw Search & Scraper Telemetry", expanded=False):
        if "search" in res:
            st.markdown("<p style='font-size:0.75rem; font-weight:600; color:#94a3b8;'>SEARCH RESULTS DATA</p>", unsafe_allow_html=True)
            st.markdown(f'<div class="raw-content">{res["search"]}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        if "reader" in res:
            st.markdown("<p style='font-size:0.75rem; font-weight:600; color:#94a3b8;'>DEEP EXTRACTED DATA</p>", unsafe_allow_html=True)
            st.markdown(f'<div class="raw-content">{res["reader"]}</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-text">
    LangChain & Groq Powered Architecture · Production Pipeline
</div>
""", unsafe_allow_html=True)