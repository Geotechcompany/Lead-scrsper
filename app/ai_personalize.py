import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def personalize_email(lead, subject_template, body_template):
    """
    Generates personalized subject & body using Gemini AI.
    """
    subject_filled = subject_template.format(**lead)
    body_filled = body_template.format(**lead)

    prompt = f"""
    You are an expert cold outreach copywriter.
    Personalize this email for the lead:

    Lead Data: {lead}
    Draft Subject: {subject_filled}
    Draft Body: {body_filled}

    Output JSON with:
    subject: short, engaging, human-like
    body: friendly but professional, under 120 words
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        import json
        data = json.loads(response.text)
    except:
        # Fallback: simple dict if JSON parse fails
        data = {"subject": subject_filled, "body": body_filled}

    return data["subject"], data["body"]
