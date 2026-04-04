# MLH PE Hackathon 2026

A production-ready Flask API built for the MLH Production Engineering 
Hackathon 2026. Built to survive outages, load tests, and chaos 
engineering challenges.

**Team:** pk504b, gbemilekeadesiyan-a11y

---

## Stack

| Tool | Purpose |
|---|---|
| **Flask** | Web framework — handles incoming requests |
| **PostgreSQL** | Database — stores data permanently |
| **Peewee** | ORM — lets us talk to PostgreSQL using Python |
| **uv** | Package manager — faster alternative to pip |
| **pytest** | Testing framework |
| **pytest-cov** | Measures how much of our code is tested |
| **GitHub Actions** | CI/CD — runs tests automatically on every push |
| **Docker** | Containerizes the app so it runs anywhere |
| **Nginx** | Load balancer — splits traffic across multiple app instances |
| **Redis** | Caching — stores frequent responses in memory |
| **Locust** | Load testing — simulates thousands of concurrent users |

---

## Architecture
Internet
↓
Nginx (Load Balancer)
↓           ↓
App Instance 1  App Instance 2
↓           ↓
Redis Cache
↓
PostgreSQL Database

---

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL running locally
- uv installed
- Docker Desktop (for containerized setup)

### Local Setup
```bash
# 1. Clone the repo
git clone https://github.com/pk504b/mlh-pe-hackathon-2026
cd mlh-pe-hackathon-2026

# 2. Install dependencies
uv sync

# 3. Create database (run in psql)
CREATE DATABASE hackathon_db;

# 4. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL password

# 5. Run the app
uv run run.py
```

### Docker Setup
```bash
# Build and run all containers
docker-compose up --build

# Run in background
docker-compose up -d
```

---

## API Endpoints

| Method | Endpoint | Description | Response |
|---|---|---|---|
| GET | `/health` | Service health check | `{"status": "ok", "database": "connected", "uptime_seconds": 142}` |
| GET | `/songs` | Get all songs | Array of song objects |
| POST | `/songs` | Create a new song | Created song object |
| GET | `/songs/<id>` | Get a song by ID | Single song object |

### Example: Create a Song
```bash
curl -X POST http://localhost:5000/songs \
  -H "Content-Type: application/json" \
  -d '{"title": "Essence", "artist": "Wizkid", 
       "genre": "Afrobeats", "duration": 212}'
```

### Example: Get All Songs
```bash
curl http://localhost:5000/songs
```

---

## Running Tests
```bash
# Run tests
uv run pytest test_health.py -v

# Run with coverage report
uv run pytest test_health.py -v --cov=app --cov-report=term-missing
```

Current coverage: **95%** (10 tests passing)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_NAME` | hackathon_db | PostgreSQL database name |
| `DATABASE_HOST` | localhost | Database host |
| `DATABASE_PORT` | 5432 | Database port |
| `DATABASE_USER` | postgres | Database user |
| `DATABASE_PASSWORD` | postgres | Database password |
| `FLASK_DEBUG` | true | Enable debug mode |
| `REDIS_URL` | redis://localhost:6379 | Redis connection URL |

---

## Reliability Features

- `/health` endpoint checks live database connectivity on every request
- Uptime tracking from the moment the service starts
- Graceful error handling — all errors return clean JSON, never a crash
- 10 automated tests at 95% coverage
- CI/CD via GitHub Actions — blocks merges if tests fail
- Docker restart policy — app auto-recovers if it crashes

---

## Scalability Features

- Docker containers — app runs in isolated, reproducible environments
- Multiple app instances via Docker Compose — horizontal scaling
- Nginx load balancer — distributes traffic evenly across instances
- Redis caching — frequent responses served from memory, not database
- Locust load testing — verified stable under 500 concurrent users

---

## Failure Modes

### Database Goes Down
**What happens:** `/health` catches the error immediately and returns:
```json
{
  "status": "error",
  "database": "unreachable", 
  "reason": "connection refused"
}
```
**How we detect it:** Every `/health` request pings the DB with 
`SELECT 1`. If it fails, we know within seconds.

**How to fix it:** Restart PostgreSQL. App recovers automatically 
on the next request — no app restart needed.

### Bad Request / Unknown Route
**What happens:** Returns clean JSON instead of an HTML error page:
```json
{"error": "Resource not found", "status": 404}
```
**How we detect it:** Global 404/500 error handlers catch everything.

### App Crashes Completely
**What happens:** Docker restart policy automatically brings 
it back up.
**How we detect it:** Uptime counter resets to 0 on `/health`.

### Missing Required Fields on POST
**What happens:** Returns a 400 with exactly which fields are missing:
```json
{"error": "Missing fields: ['artist', 'duration']"}
```

---

## Decision Log

| Decision | Why we made it |
|---|---|
| **Flask over Django** | Django is heavy for a hackathon — Flask is minimal and fast to set up |
| **Peewee over SQLAlchemy** | Peewee is simpler and the template already used it |
| **uv over pip** | Faster installs, handles virtualenv automatically, built into the template |
| **PostgreSQL over SQLite** | SQLite isn't production-grade — PostgreSQL is what real companies use |
| **pytest-cov** | Gives us a coverage report to prove to judges we're not guessing |
| **GitHub Actions** | Free CI/CD, integrates directly with GitHub, zero extra setup |
| **Uptime tracking** | Judges look for observability — knowing how long you've been up is basic SRE |
| **Database health check** | Just checking if Flask is running isn't enough — we verify the DB too |
| **Nginx** | Industry standard load balancer — required for Scalability Silver |
| **Redis** | Caching layer required for Scalability Gold — fastest way to reduce DB load |
| **Locust** | Recommended in the Quest Log, Python-based so fits our stack |
| **Docker restart policy** | Required for Reliability Gold Chaos Mode — auto-resurrection |

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `uv: command not found` | uv not installed | Run the uv installer, restart terminal |
| `password authentication failed` | Wrong password in `.env` | Update `DATABASE_PASSWORD` in `.env` |
| `relation "song" does not exist` | Table not created | Run `db.create_tables([Song])` once |
| `permission denied to repo` | Not added as collaborator | Repo owner adds via Settings → Collaborators |
| `GET /songs 404` | Blueprint not registered | Check `app/routes/__init__.py` has blueprint |
| `[200~git: command not found` | Pasted command with formatting chars | Type commands manually, don't paste |

---

## CI/CD

Every push to main triggers GitHub Actions which:
1. Spins up a fresh Ubuntu machine
2. Installs all dependencies via uv
3. Boots a real PostgreSQL database
4. Creates all tables
5. Runs all 10 tests
6. Reports pass/fail in ~18 seconds

If tests fail, the pipeline blocks the merge. No broken code reaches main.