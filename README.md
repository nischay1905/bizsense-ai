#  BizSense AI — Intelligent Business Process Analyzer

> Identify inefficiencies, map automation opportunities, and estimate ROI from any business process description using AI.

Built for **Genpact MT/BA 4A** | **IIT Roorkee Hostel Council Open Projects 2026**

---

##  Live Demo

https://bizsense-ai-wzygyunmguauvoye4vjwa6.streamlit.app/

[**→ Try it live on Streamlit Cloud**](https://bizsense-ai-wzygyunmguauvoye4vjwa6.streamlit.app/
)  
*(Replace with your deployed URL)*

![BizSense AI Demo](assets/demo.gif)

---

##  What it does

Paste or upload any business process (invoice processing, IT helpdesk, HR recruitment, etc.) and BizSense AI will:

- **Identify inefficiencies** — bottlenecks, manual steps, delays with quantified impact
- **Map automation opportunities** — specific steps + recommended tools (RPA, AI, APIs)
- **Estimate ROI** — hours saved per month, automation %, payback timeframe
- **Prioritize recommendations** — ranked by impact and effort
- **Export reports** — download as JSON or plain text

---

##  Architecture

```
User Input (text / PDF)
        │
        ▼
  Prompt Engine (domain-tuned)
        │
        ▼
  Claude Sonnet API
        │
        ▼
  JSON Parser & Validator
        │
        ▼
  Streamlit Dashboard → Export
```

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Core | Anthropic Claude (claude-sonnet-4-20250514) |
| PDF Parsing | PyMuPDF |
| Deployment | Streamlit Cloud |
| Language | Python 3.10+ |

---

##  Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/bizsense-ai
cd bizsense-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

You'll need a free Anthropic API key from [console.anthropic.com](https://console.anthropic.com).

---

##  Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. Click **Deploy** — live URL in ~2 minutes

---

##  Project Structure

```
bizsense-ai/
├── app.py              # Main Streamlit application
├── prompts.py          # Domain-specific prompt templates
├── utils.py            # PDF reader, API caller, JSON parser
├── requirements.txt
└── README.md
```

---

##  Business Impact

Tested on 3 real-world process types:

| Process | Automation Potential | Hours Saved/Month |
|---|---|---|
| Invoice Processing | 78% | 140 hrs |
| IT Helpdesk | 65% | 90 hrs |
| HR Recruitment | 55% | 60 hrs |

---

##  Author

**[Nischay Jiwankar]** — EE, IIT Roorkee  
 | [GitHub](https://github.com/nischay1905)

---

## 📄 License

MIT License — free to use, modify, and distribute.
