# LeadGen System (Free, Open-Source, Local-LLM Friendly)

An end-to-end system that:
- Scrapes or imports US leads
- Writes **personalized cold emails** with a **local LLM** via **Ollama**
- Sends emails automatically (SMTP)
- Tracks **opens** (tracking pixel), **clicks** (unique token link), and **replies** (IMAP polling)
- Provides a small **FastAPI dashboard** to view leads & stats

## Quick Start

### 0) Prereqs
- Python 3.10+
- (Optional) **Ollama** installed and running: https://ollama.com
  - Pull a model, e.g.:
    ```bash
    ollama pull mistral
    ```

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your SMTP/IMAP creds (use Gmail app password) and APP_BASE_URL
```

### 2) Initialize & Run
```bash
uvicorn app.main:app --reload --port 8000
```

Visit the docs: http://localhost:8000/docs

### 3) Import Leads
- Option A: CSV import:
  ```bash
  python -m app.scraper.csv_import sample_leads.csv
  ```
  CSV headers required: `name,email,company,website,notes,city,state`

- Option B (advanced): Scrapy spider (Yelp skeleton) at `app/scraper/yelp_spider.py`.
  > ⚠️ Respect robots.txt, Terms of Service, and local laws. Test with a small crawl, do not overload sites.

### 4) Send Campaign
- Create a campaign via API (or see `/docs`).
- The scheduler will pick unsent leads up to `DAILY_SEND_LIMIT` and send emails.
- Opens/clicks tracked via pixel and tokenized links.
- Replies monitored by IMAP every few minutes.

## Architecture
- **FastAPI** (API + tracking endpoints)
- **SQLite** via SQLAlchemy (default; switch to Postgres by changing `DATABASE_URL`)
- **APScheduler** (periodic send + IMAP watcher)
- **Ollama** for on-device personalization (`/v1/chat` compatible)
- **SMTP** for sending
- **IMAP** for reply detection

## Legal & Ethical Notes
- Always comply with **CAN-SPAM** (US) and other relevant laws.
- Only email addresses with a **legitimate interest** and provide an opt-out.
- Respect site **ToS** and **robots.txt**. Prefer public directories or official APIs.

## Cursor Setup (Optional)
- In Cursor settings → Models → Custom OpenAI, you can point to your local Ollama if you expose an OpenAI-compatible endpoint (e.g., using `litellm` or an adapter). This project calls Ollama directly.

## Development Tips
- For safe testing, use a sandbox inbox (like a spare Gmail) and a local mail catcher (e.g., MailHog).
- The email templates are in Jinja2 (`app/templates/email.html.j2`).

---

MIT License. Use responsibly.
