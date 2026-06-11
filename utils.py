import json, re, requests

def call_claude_api(prompt: str, api_key: str) -> str:
    """Call Groq (Llama 3.3 70B) and return raw text response."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a business process automation expert. Always respond with valid JSON only. No markdown fences, no explanatory text before or after the JSON."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers=headers, json=body, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        text = e.response.text[:300].encode("ascii", errors="replace").decode("ascii")
        return f'{{"error": "API error: {status} - {text}"}}'
    except Exception as e:
        msg = str(e).encode("ascii", errors="replace").decode("ascii")
        return f'{{"error": "Unexpected error: {msg}"}}'

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
        return text.strip() or "No text found in PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"
