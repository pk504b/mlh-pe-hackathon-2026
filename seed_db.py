import os
import csv
from peewee import chunked, PostgresqlDatabase
from app.database import db
from app.models.user import User
from app.models.url import Url
from app.models.event import Event
from dotenv import load_dotenv

def seed_users():
    print("Seeding users...")
    filepath = "seed/users.csv"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many(batch).on_conflict_ignore().execute()
    print(f"Inserted {len(rows)} users.")

def seed_urls():
    print("Seeding urls...")
    filepath = "seed/urls.csv"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    with db.atomic():
        for batch in chunked(rows, 100):
            Url.insert_many(batch).on_conflict_ignore().execute()
    print(f"Inserted {len(rows)} urls.")

def seed_events():
    print("Seeding events...")
    filepath = "seed/events.csv"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    with db.atomic():
        for batch in chunked(rows, 100):
            Event.insert_many(batch).on_conflict_ignore().execute()
    print(f"Inserted {len(rows)} events.")

def run_seeding():
    seed_users()
    seed_urls()
    seed_events()

if __name__ == "__main__":
    load_dotenv()
    
    # Setup database connection for standalone run
    database = PostgresqlDatabase(
        os.environ.get("DATABASE_NAME", "hackathon_db"),
        host=os.environ.get("DATABASE_HOST", "localhost"),
        port=int(os.environ.get("DATABASE_PORT", 5432)),
        user=os.environ.get("DATABASE_USER", "postgres"),
        password=os.environ.get("DATABASE_PASSWORD", "postgres"),
    )
    db.initialize(database)
    
    db.connect()
    # Resetting tables is useful for development but dangerous for production!
    print("Resetting tables...")
    db.drop_tables([Event, Url, User])
    print("Creating tables...")
    db.create_tables([User, Url, Event])
    
    run_seeding()
    
    db.close()
    print("Seeding complete!")
