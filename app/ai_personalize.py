import httpx
from .config import settings

SYSTEM_PROMPT = "You are a helpful SDR writing concise, personalized cold emails to US small businesses. Keep it under 120 words and avoid hype."

async def personalize(lead: dict, campaign_body_template: str) -> str:
    content = f"""
    Write a short, friendly, personalized email body to this lead about website development services.
    Context:
    Lead: {lead}
    Template (use as guidance, adapt as needed):
    {campaign_body_template}
    Focus on a single quick win and suggest a short call, keep to ~3 sentences.
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{settings.ollama_base_url}/v1/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": content}
                    ]
                },
            )
            r.raise_for_status()
            data = r.json()
            # OpenAI-style response
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # Fallback very simple template without AI
        name = lead.get("name") or "there"
        company = lead.get("company") or ""
        website = lead.get("website") or ""
        return (
            f"Hi {name}, I reviewed {company or 'your business'}{(' at ' + website) if website else ''}. "
            "I can quickly improve load speed and mobile UX and ship a small homepage refresh in 72 hours. "
            "Open to a quick 10‑min chat this week?"
        )
