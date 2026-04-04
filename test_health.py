import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_health_returns_json(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "ok"

def test_health_database_connected(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["database"] == "connected"

def test_404_returns_json(client):
    response = client.get("/nonexistent")
    data = response.get_json()
    assert response.status_code == 404
    assert "error" in data

def test_health_has_uptime(client):
    response = client.get("/health")
    data = response.get_json()
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0  

def test_create_song(client):
    response = client.post("/songs", json={
        "title": "Love Nwantiti",
        "artist": "CKay",
        "genre": "Afropop",
        "duration": 194
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Love Nwantiti"
    assert data["artist"] == "CKay"

def test_get_songs(client):
    response = client.get("/songs")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_song_by_id(client):
    # So we first create a song
    create = client.post("/songs", json={
        "title": "Bandana",
        "artist": "Fireboy DML",
        "genre": "Afrobeats",
        "duration": 180
    })
    song_id = create.get_json()["id"]

    # T,And then we fetch it by ID
    response = client.get(f"/songs/{song_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Bandana"

def test_get_nonexistent_song(client):
    response = client.get("/songs/99999")
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_create_song_missing_fields(client):
    response = client.post("/songs", json={
        "title": "Incomplete Song"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()