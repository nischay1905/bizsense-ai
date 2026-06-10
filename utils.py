"""
utils.py — Utility functions for BizSense AI
"""

import json
import re
import requests


# ── Claude API ────────────────────────────────────────────────────────────────

def call_claude_api(prompt: str, api_key: str) -> str:
    """Call Claude claude-sonnet-4-20250514 and return the raw text response."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
        "system": (
            "You are a business process automation expert. "
            "Always respond with valid JSON only. "
            "No markdown code fences, no explanatory text before or after the JSON."
        ),
    }
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]
    except requests.exceptions.Timeout:
        return '{"error": "Request timed out. Try again."}'
    except requests.exceptions.HTTPError as e:
        return f'{{"error": "API error: {e.response.status_code} — {e.response.text[:200]}"}}'
    except Exception as e:
        return f'{{"error": "Unexpected error: {str(e)}"}}'


# ── JSON Parser ───────────────────────────────────────────────────────────────

def parse_llm_response(raw: str) -> dict:
    """Safely parse the LLM response into a dict."""
    # Strip markdown fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    # Extract the first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return {"error": "No JSON found in response", "raw": raw[:500]}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": raw[:500]}


# ── PDF Text Extractor ────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from an uploaded PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        import io

        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        full_text = "\n".join(text_parts).strip()
        if not full_text:
            return "⚠️ No extractable text found in PDF. It may be a scanned image."
        return full_text

    except ImportError:
        return (
            "⚠️ PyMuPDF not installed. Run: pip install pymupdf\n"
            "Or paste your process description in the text tab instead."
        )
    except Exception as e:
        return f"⚠️ Could not extract PDF text: {e}"
