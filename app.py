import streamlit as st
import json
import time
from prompts import build_prompt
from utils import extract_text_from_pdf, parse_llm_response, call_claude_api

st.set_page_config(
    page_title="BizSense AI",
    page_icon="🧠",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #666; font-size: 1rem; margin-bottom: 2rem; }
    .metric-card {
        background: #f8f9ff; border-radius: 12px; padding: 1.2rem;
        border-left: 4px solid #667eea; margin-bottom: 1rem;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #667eea; }
    .metric-label { font-size: 0.85rem; color: #888; margin-top: 0.2rem; }
    .issue-card {
        background: #fff5f5; border-radius: 10px; padding: 1rem;
        border-left: 4px solid #fc8181; margin-bottom: 0.8rem;
    }
    .auto-card {
        background: #f0fff4; border-radius: 10px; padding: 1rem;
        border-left: 4px solid #68d391; margin-bottom: 0.8rem;
    }
    .tool-badge {
        display: inline-block; background: #ebf4ff; color: #3182ce;
        border-radius: 20px; padding: 0.2rem 0.8rem;
        font-size: 0.8rem; margin: 0.2rem;
    }
    .section-title {
        font-size: 1.15rem; font-weight: 600; color: #2d3748;
        margin: 1.5rem 0 0.8rem 0; border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.4rem;
    }
    .stTextArea textarea { font-size: 0.9rem; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🧠 BizSense AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Intelligent Business Process Analyzer — '
    'Identify inefficiencies, map automation opportunities & estimate ROI</div>',
    unsafe_allow_html=True
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Get your free key at console.anthropic.com"
    )
    domain = st.selectbox(
        "Business Domain",
        ["Finance & Accounting", "IT & Helpdesk", "HR & Recruitment",
         "Supply Chain", "Customer Support", "General"],
        index=0
    )
    detail_level = st.select_slider(
        "Analysis Depth",
        options=["Quick", "Standard", "Deep"],
        value="Standard"
    )
    st.divider()
    st.markdown("**📌 How to use**")
    st.markdown(
        "1. Enter your API key\n"
        "2. Select your domain\n"
        "3. Paste or upload a process description\n"
        "4. Click **Analyze**\n"
        "5. Download your report"
    )
    st.divider()
    st.markdown(
        "<small>Built for Genpact MT/BA 4A | IIT Roorkee Open Projects 2026</small>",
        unsafe_allow_html=True
    )

# ── Input Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📄 Process Input</div>', unsafe_allow_html=True)

input_tab, upload_tab, example_tab = st.tabs(
    ["✍️ Paste Text", "📎 Upload PDF", "💡 Load Example"]
)

process_text = ""

with input_tab:
    process_text_input = st.text_area(
        "Describe your business process in detail",
        height=200,
        placeholder=(
            "E.g. Our invoice processing starts when a vendor emails an invoice. "
            "The accounts team manually downloads the PDF, re-enters data into SAP, "
            "then routes it to the manager via email for approval. The manager replies "
            "with approval or rejection. If approved, finance manually schedules payment ..."
        )
    )
    if process_text_input:
        process_text = process_text_input

with upload_tab:
    uploaded_file = st.file_uploader("Upload a PDF (SOP, workflow doc)", type=["pdf"])
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            process_text = extract_text_from_pdf(uploaded_file)
        st.success(f"✅ Extracted {len(process_text.split())} words from PDF")
        with st.expander("Preview extracted text"):
            st.text(process_text[:1000] + ("..." if len(process_text) > 1000 else ""))

with example_tab:
    examples = {
        "Invoice Processing (Finance)": (
            "Our invoice processing workflow begins when a vendor sends an invoice via email "
            "to a shared mailbox. An accounts payable clerk manually checks the inbox twice a day, "
            "downloads the PDF, and visually inspects it for completeness. They then manually type "
            "all invoice details—vendor name, amount, line items, tax, due date—into SAP. "
            "Once entered, the clerk prints the invoice and physically walks it to the finance manager "
            "for a signature. If the manager is unavailable, invoices pile up on their desk for days. "
            "Approved invoices are returned to the clerk who then manually schedules payment in the "
            "banking portal. Payment confirmations are emailed to vendors manually. "
            "The entire cycle takes 7–10 business days per invoice. The team processes ~200 invoices/month."
        ),
        "IT Helpdesk (IT Support)": (
            "When an employee has an IT issue, they call the helpdesk or walk to the IT desk. "
            "A technician manually logs the issue in an Excel sheet with a sequential ticket number. "
            "The technician then diagnoses the problem, often needing to escalate to a senior engineer "
            "via phone call. Resolution steps are not documented. After fixing, the technician marks "
            "the Excel row as resolved and verbally informs the employee. No SLA tracking exists. "
            "Common issues like password resets, VPN setup, and printer issues recur daily. "
            "The team handles ~150 tickets/week. There is no self-service portal."
        ),
        "HR Recruitment (HR)": (
            "Recruitment starts when a hiring manager emails HR requesting a new hire. "
            "HR manually posts the JD on the careers portal and LinkedIn. Applications arrive "
            "via email and a shared Google Sheet is used to track candidates. "
            "HR manually screens each resume, copies relevant ones into a separate sheet, "
            "and emails shortlisted candidates individually to schedule interviews. "
            "Interview feedback is collected via email and manually updated in the sheet. "
            "Offer letters are drafted manually in Word for each candidate. "
            "The process from JD to offer takes 45–60 days on average for each position."
        ),
    }
    selected_example = st.selectbox("Choose an example process", list(examples.keys()))
    if st.button("Load this example"):
        process_text = examples[selected_example]
        st.success("✅ Example loaded!")
        st.text_area("Loaded process:", value=process_text, height=150, disabled=True)

# ── Analyze Button ────────────────────────────────────────────────────────────
st.markdown("")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_clicked = st.button(
        "🔍 Analyze Process", type="primary", use_container_width=True,
        disabled=(not api_key or not process_text)
    )

if not api_key:
    st.info("👈 Add your Anthropic API key in the sidebar to get started.")
elif not process_text:
    st.info("👆 Paste a process description, upload a PDF, or load an example above.")

# ── Analysis & Results ────────────────────────────────────────────────────────
if analyze_clicked and api_key and process_text:
    prompt = build_prompt(process_text, domain, detail_level)

    with st.spinner("🤖 Analyzing your business process..."):
        progress = st.progress(0)
        for i in range(40):
            time.sleep(0.02)
            progress.progress(i + 1)

        raw_response = call_claude_api(prompt, api_key)

        for i in range(40, 90):
            time.sleep(0.01)
            progress.progress(i + 1)

        result = parse_llm_response(raw_response)
        progress.progress(100)
        time.sleep(0.3)
        progress.empty()

    if "error" in result:
        st.error(f"❌ Analysis failed: {result['error']}\n\nRaw response:\n{raw_response[:500]}")
    else:
        st.success("✅ Analysis complete!")
        st.balloons()

        # ── KPI Row ───────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('automation_potential', 'N/A')}%</div>
                <div class="metric-label">Automation potential</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('hours_saved_monthly', 'N/A')}</div>
                <div class="metric-label">Hours saved / month</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('issues_count', len(result.get('inefficiencies', [])))}</div>
                <div class="metric-label">Issues identified</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('roi_timeframe', 'N/A')}</div>
                <div class="metric-label">Estimated ROI timeframe</div>
            </div>""", unsafe_allow_html=True)

        # ── Executive Summary ─────────────────────────────────────────────────
        st.markdown('<div class="section-title">📝 Executive Summary</div>', unsafe_allow_html=True)
        st.info(result.get("executive_summary", "No summary available."))

        # ── Two-column layout ─────────────────────────────────────────────────
        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown('<div class="section-title">⚠️ Inefficiencies Found</div>', unsafe_allow_html=True)
            for issue in result.get("inefficiencies", []):
                st.markdown(f"""
                <div class="issue-card">
                    <strong>{issue.get('title', 'Issue')}</strong><br>
                    <small>{issue.get('description', '')}</small><br>
                    <small>⏱️ <b>Impact:</b> {issue.get('impact', 'Unknown')}</small>
                </div>""", unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="section-title">🤖 Automation Opportunities</div>', unsafe_allow_html=True)
            for opp in result.get("automation_opportunities", []):
                tools_html = "".join(
                    f'<span class="tool-badge">{t}</span>'
                    for t in opp.get("tools", [])
                )
                st.markdown(f"""
                <div class="auto-card">
                    <strong>{opp.get('step', 'Step')}</strong><br>
                    <small>{opp.get('solution', '')}</small><br>
                    {tools_html}
                </div>""", unsafe_allow_html=True)

        # ── Recommendations ───────────────────────────────────────────────────
        st.markdown('<div class="section-title">🚀 Prioritized Recommendations</div>', unsafe_allow_html=True)
        for i, rec in enumerate(result.get("recommendations", []), 1):
            priority = rec.get("priority", "Medium")
            color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
            with st.expander(f"{color} {i}. {rec.get('action', 'Recommendation')} — {priority} Priority"):
                st.markdown(f"**Expected outcome:** {rec.get('outcome', 'N/A')}")
                st.markdown(f"**Effort:** {rec.get('effort', 'N/A')}")
                st.markdown(f"**Tools/Tech:** {rec.get('tools', 'N/A')}")

        # ── ROI Table ─────────────────────────────────────────────────────────
        if "roi_breakdown" in result:
            st.markdown('<div class="section-title">💰 ROI Breakdown</div>', unsafe_allow_html=True)
            st.table(result["roi_breakdown"])

        # ── Download JSON Report ──────────────────────────────────────────────
        st.markdown('<div class="section-title">📥 Export</div>', unsafe_allow_html=True)
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label="⬇️ Download JSON Report",
                data=json.dumps(result, indent=2),
                file_name="bizsense_report.json",
                mime="application/json",
                use_container_width=True
            )
        with dl2:
            text_report = f"""
BIZSENSE AI — PROCESS ANALYSIS REPORT
======================================
Domain: {domain}
Analysis depth: {detail_level}

EXECUTIVE SUMMARY
-----------------
{result.get('executive_summary', '')}

KEY METRICS
-----------
Automation Potential : {result.get('automation_potential', 'N/A')}%
Hours Saved / Month  : {result.get('hours_saved_monthly', 'N/A')}
Issues Identified    : {result.get('issues_count', 'N/A')}
ROI Timeframe        : {result.get('roi_timeframe', 'N/A')}

INEFFICIENCIES
--------------
{chr(10).join(f"- {i.get('title','')}: {i.get('description','')}" for i in result.get('inefficiencies', []))}

AUTOMATION OPPORTUNITIES
------------------------
{chr(10).join(f"- {o.get('step','')}: {o.get('solution','')}" for o in result.get('automation_opportunities', []))}

RECOMMENDATIONS
---------------
{chr(10).join(f"{idx+1}. [{r.get('priority','')}] {r.get('action','')}" for idx, r in enumerate(result.get('recommendations', [])))}
""".strip()
            st.download_button(
                label="⬇️ Download Text Report",
                data=text_report,
                file_name="bizsense_report.txt",
                mime="text/plain",
                use_container_width=True
            )
