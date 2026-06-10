import json, re, requests

def call_claude_api(prompt: str, api_key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    body = {
        "system_instruction": {"parts": [{"text": "You are a business process automation expert. Always respond with valid JSON only. No markdown fences, no text before or after JSON."}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
    }
    try:
        r = requests.post(url, json=body, timeout=60)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        return f'{{"error": "API error: {e.response.status_code} — {e.response.text[:300]}"}}'
    except Exception as e:
        return f'{{"error": "Unexpected error: {str(e)}"}}'

def parse_llm_response(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return {"error": "No JSON found", "raw": raw[:500]}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": raw[:500]}

def extract_text_from_pdf(uploaded_file) -> str:
    try:
        import fitz
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join(p.get_text() for p in doc)
        doc.close()
        return text.strip() or "⚠️ No text found in PDF."
    except Exception as e:
        return f"⚠️ Error: {e}"
