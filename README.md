# MLH PE Hackathon 2026

A production-ready Flask API built for the MLH Production Engineering 
Hackathon 2026. Built to survive outages, load tests, and chaos 
engineering challenges.

**Team:** pk504b, gbemilekeadesiyan-a11y, Optimistic-max (The Shorteners)

---

## Stack

| Tool | Purpose |
|---|---|
| **Flask** | Web framework adn it handles incoming requests |
| **PostgreSQL** | The database for our app, it stores data permanently |
| **Peewee** | It's an ORM that lets us talk to PostgreSQL using Python |
| **uv** | It's a Package manager and it's a faster alternative to pip |
| **pytest** | What we used to run our test|
| **pytest-cov** | Measures how much of our code is tested |
| **GitHub Actions** | It's for the CI/CD it runs tests automatically on every push |
| **Docker** | Containerizes the app so it runs anywhere and we can have multiple versions of it |
| **Nginx** | It's the Load balancer that splits traffic across multiple app instances |
| **Redis** | it's for caching and it stores frequent responses in memory so we do not have to repeat using routes to the main databse |
| **Locust** | It's for Load testing, it simulates thousands of concurrent users |

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

### We needed:
- Python 3.12+
- PostgreSQL running locally
- uv installed
- Docker Desktop (for our containerized setup)

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

### Example: Let's say you want to create a Song
```bash
curl -X POST http://localhost:5000/songs \
  -H "Content-Type: application/json" \
  -d '{"title": "Essence", "artist": "Wizkid", 
       "genre": "Afrobeats", "duration": 212}'
```

### Example: Let us get All Songs
```bash
curl http://localhost:5000/songs
```

---

## Now, on running Tests
```bash
# Run tests
uv run pytest test_health.py -v

# If you want to run with coverage report
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

## Reliability Features we Added

- `/health` endpoint checks live database connectivity on every request
- We added uptime tracking from the moment the service starts
- We also added graceful error handling which means that all errors return clean JSON, never a crash
- 10 automated tests at 95% coverage
- We implemented CI/CD via GitHub Actions which blocks merges if tests fail
- Now the Docker has a restart policy, the app auto-recovers IF it crashes

---

## Scalability Features

- Docker containers which allows the app to run in isolated, reproducible environments. We had to ensure High availability.
- Multiple app instances via Docker Compose for horizontal scaling
- Nginx load balancer which helps distributes traffic evenly across instances
- Redis caching for frequent responses served from memory, not database
- And Locust load testing which we verified as stable under 500 concurrent users

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

**How to fix it:** Restart PostgreSQL. Then the app recovers automatically 
on the next request — no app restart needed.

### Bad Request / Unknown Route
**What happens:** It returns clean JSON instead of the usual HTML error page:
```json
{"error": "Resource not found", "status": 404}
```
**How we detect it:** the global 404/500 error handlers catch everything.

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
| **Flask over Django** | Flask is minimal and fast to set up |
| **Peewee over SQLAlchemy** | Peewee is by far easier |
| **uv over pip** | It installs things faster,and it handles virtualenv automatically. |
| **PostgreSQL over SQLite** | SQLite isn't production-grade — PostgreSQL is what real companies use |
| **pytest-cov** | It gives us actual facts and figures |
| **GitHub Actions** | It's a free CI/CD and it helps alot |
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