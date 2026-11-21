from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
def test_global_exception_handler():
    @app.get("/test-error")
    def test_error():
        raise RuntimeError("Unexpected test error")

    response = client.get("/test-error")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}