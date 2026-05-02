from fastapi.testclient import TestClient
from PIL import Image
import io
from src.service.api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]


def test_predict_ok():
    # простое серое изображение 48×48
    img = Image.new("L", (48, 48), color=128)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    
    response = client.post("/predict", files={"file": ("test.jpg", buf, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "emotion" in data["data"]
    assert "confidence" in data["data"]


def test_predict_wrong_type():
    response = client.post("/predict", files={"file": ("bad.txt", b"not image", "text/plain")})
    assert response.status_code == 415  # Unsupported Media Type