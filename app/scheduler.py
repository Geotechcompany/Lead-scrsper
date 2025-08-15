from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import secrets
from .db import SessionLocal
from .models import Lead, Campaign, EmailLog, Unsubscribe
from .config import settings
from .mailer import render_email_html, send_email
from .ai_personalize import personalize

scheduler = AsyncIOScheduler()

async def job_send_batch():
    db: Session = SessionLocal()
    try:
        # pick latest campaign
        campaign = db.execute(select(Campaign).order_by(Campaign.id.desc())).scalars().first()
        if not campaign:
            return

        # do not send to unsubscribed or already emailed
        unsubbed = {u.email.lower() for u in db.query(Unsubscribe).all()}

        q = db.query(Lead).filter(Lead.status == "new")
        count = 0
        for lead in q.limit(settings.daily_send_limit).all():
            if lead.email.lower() in unsubbed:
                continue
            token = secrets.token_urlsafe(16)
            pixel_url = f"{settings.app_base_url}/t/pixel/{token}.png"
            click_url = f"{settings.app_base_url}/t/click/{token}"
            unsubscribe_url = f"{settings.app_base_url}/unsubscribe?email={lead.email}"
            lead_dict = {
                "name": lead.name, "company": lead.company, "website": lead.website,
                "city": lead.city, "state": lead.state, "email": lead.email
            }
            body = await personalize(lead_dict, campaign.body_template)
            html = render_email_html(body, pixel_url, unsubscribe_url, settings.smtp_from.split('<')[0].strip(), lead_dict)
            subject = campaign.subject_template.format(company=lead.company or "", name=lead.name or "", city=lead.city or "", state=lead.state or "")
            try:
                message_id = await send_email(lead.email, subject, html)
            except Exception:
                continue
            log = EmailLog(lead_id=lead.id, campaign_id=campaign.id, message_id=message_id, token=token)
            lead.status = "emailed"
            db.add(log)
            db.add(lead)
            db.commit()
            count += 1
    finally:
        db.close()

async def job_check_replies():
    # IMAP polling
    import imapclient, email
    from email.header import decode_header
    db: Session = SessionLocal()
    try:
        imap = imapclient.IMAPClient(settings.imap_host, ssl=True)
        imap.login(settings.imap_username, settings.imap_password)
        imap.select_folder(settings.imap_folder)
        # search last 3 days
        import datetime
        since = (datetime.date.today() - datetime.timedelta(days=3)).strftime("%d-%b-%Y")
        uids = imap.search([u"SINCE", since])
        if not uids:
            imap.logout()
            return
        messages = imap.fetch(uids, ["RFC822", "ENVELOPE"])
        for uid, data in messages.items():
            msg = email.message_from_bytes(data[b"RFC822"])
            in_reply_to = msg.get("In-Reply-To", "") or msg.get("References", "")
            subject = msg.get("Subject", "")
            payload = msg.get_payload(decode=True) if not msg.is_multipart() else None
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        body_text = (part.get_payload(decode=True) or b"").decode(errors="ignore")
                        break
            else:
                body_text = (payload or b"").decode(errors="ignore")

            # Match by token in subject/body (token was in tracking links; if they replied, often quoted)
            # Also try matching by Message-ID threading
            matched = None
            for log in db.query(EmailLog).filter(EmailLog.reply_detected == False).all():
                token = log.token
                if token in subject or token in body_text or token in in_reply_to:
                    matched = log
                    break
            if matched:
                matched.reply_detected = True
                matched.reply_at = datetime.datetime.utcnow()
                lead = db.query(Lead).filter(Lead.id == matched.lead_id).first()
                if lead:
                    lead.status = "replied"
                    db.add(lead)
                db.add(matched)
                db.commit()
        imap.logout()
    except Exception:
        pass
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(job_send_batch, IntervalTrigger(minutes=5), id="send_batch", replace_existing=True)
    scheduler.add_job(job_check_replies, IntervalTrigger(minutes=7), id="check_replies", replace_existing=True)
    scheduler.start()
