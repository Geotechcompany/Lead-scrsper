import csv, sys
from sqlalchemy.orm import Session
from ..db import SessionLocal, Base, engine
from ..models import Lead

def import_csv(path: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row.get("email") or "").strip()
                if not email:
                    continue
                lead = Lead(
                    name=row.get("name"),
                    email=email,
                    company=row.get("company"),
                    website=row.get("website"),
                    notes=row.get("notes"),
                    city=row.get("city"),
                    state=row.get("state"),
                )
                try:
                    db.add(lead)
                    db.commit()
                except Exception:
                    db.rollback()
        print("Import complete.")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.scraper.csv_import sample_leads.csv")
        sys.exit(1)
    import_csv(sys.argv[1])
