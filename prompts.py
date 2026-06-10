"""
prompts.py — Domain-tuned prompt templates for BizSense AI
"""

DOMAIN_CONTEXT = {
    "Finance & Accounting": (
        "Focus on invoice processing, payment cycles, reconciliation, audit trails, "
        "ERP integration (SAP, Oracle), and compliance bottlenecks."
    ),
    "IT & Helpdesk": (
        "Focus on ticket resolution times, SLA breaches, repetitive L1 issues, "
        "self-service gaps, escalation patterns, and ITSM tool usage."
    ),
    "HR & Recruitment": (
        "Focus on time-to-hire, manual screening, offer letter generation, "
        "onboarding steps, ATS usage, and compliance documentation."
    ),
    "Supply Chain": (
        "Focus on order processing, inventory reconciliation, supplier communication, "
        "logistics tracking, and demand forecasting gaps."
    ),
    "Customer Support": (
        "Focus on response times, manual ticket routing, repetitive query resolution, "
        "knowledge base gaps, and escalation rates."
    ),
    "General": (
        "Apply general business process improvement principles: eliminate waste, "
        "reduce handoffs, identify automation candidates, and improve cycle time."
    ),
}

DEPTH_INSTRUCTIONS = {
    "Quick": "Provide a concise analysis with top 3 issues and top 3 automation opportunities.",
    "Standard": "Provide a thorough analysis with up to 5 issues and 5 automation opportunities.",
    "Deep": (
        "Provide an exhaustive analysis with all issues, automation opportunities, "
        "a detailed ROI breakdown table, and implementation roadmap."
    ),
}


def build_prompt(process_text: str, domain: str, detail_level: str) -> str:
    domain_ctx = DOMAIN_CONTEXT.get(domain, DOMAIN_CONTEXT["General"])
    depth_inst = DEPTH_INSTRUCTIONS.get(detail_level, DEPTH_INSTRUCTIONS["Standard"])

    prompt = f"""You are a senior business process consultant and automation expert at a top-tier firm like Genpact, McKinsey, or Accenture.

DOMAIN CONTEXT:
{domain_ctx}

ANALYSIS DEPTH:
{depth_inst}

BUSINESS PROCESS TO ANALYZE:
\"\"\"
{process_text}
\"\"\"

Your task is to analyze this process and return a structured JSON report. Be specific, actionable, and quantitative wherever possible. If exact numbers aren't given, make reasonable estimates based on industry benchmarks and state your assumptions.

Return ONLY valid JSON with this exact structure (no markdown, no preamble):
{{
  "executive_summary": "2-3 sentence summary of the process state and key findings",
  "automation_potential": <integer 0-100, % of steps that can be automated>,
  "hours_saved_monthly": "<estimated hours e.g. '120 hrs'>",
  "roi_timeframe": "<e.g. '3-6 months'>",
  "issues_count": <integer>,
  "inefficiencies": [
    {{
      "title": "Short issue name",
      "description": "What the inefficiency is and why it happens",
      "impact": "Quantified impact e.g. '2-3 days delay per cycle'"
    }}
  ],
  "automation_opportunities": [
    {{
      "step": "Which process step to automate",
      "solution": "How to automate it specifically",
      "tools": ["Tool1", "Tool2"]
    }}
  ],
  "recommendations": [
    {{
      "action": "Specific action to take",
      "priority": "High|Medium|Low",
      "outcome": "Expected measurable outcome",
      "effort": "Low|Medium|High",
      "tools": "Specific tools or technologies to use"
    }}
  ],
  "roi_breakdown": [
    {{"Category": "...", "Current State": "...", "After Automation": "...", "Saving": "..."}}
  ]
}}"""

    return prompt
