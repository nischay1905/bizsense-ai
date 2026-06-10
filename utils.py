"""
utils.py — Utility functions for BizSense AI (Gemini backend)
"""

import json
import re
import requests


# ── Gemini API ────────────────────────────────────────────────────────────────

def call_claude_api(prompt: str, api_key: str) -> str:
    """Call Gemini 1.5 Flash and return the raw text response."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    body = {
        "system_instruction": {
            "parts": [{
                "text": (
                    "You are a business process automation expert. "
                    "Always respond with valid JSON only. "
                    "No markdown code fences, no explanatory text before or after the JSON."
                )
            }]
        },
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        }
    }
    try:
        response = requests.post(url, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.Timeout:
        return '{"error": "Request timed out. Try again."}'
    except requests.exceptions.HTTPError as e:
        return f'{{"error": "API error: {e.response.status_code} — {e.response.text[:300]}"}}'
    except (KeyError, IndexError) as e:
        return f'{{"error": "Unexpected response format: {str(e)}"}}'
    except Exception as e:
        return f'{{"error": "Unexpected error: {str(e)}"}}'


# ── JSON Parser ───────────────────────────────────────────────────────────────

def parse_llm_response(raw: str) -> dict:
    """Safely parse the LLM response into a dict."""
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
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
        import fitz

        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = [page.get_text() for page in doc]
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
