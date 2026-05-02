from PIL import Image
import numpy as np
from src.service.inference import engine


def test_engine_loaded():
    """Проверяет, что модель загрузилась."""
    assert engine.model is not None
    assert engine.device is not None


def test_predict_dummy():
    # случайное серое изображение 48×48
    img = Image.fromarray(
        np.random.randint(0, 255, (48, 48), dtype=np.uint8), 
        mode="L"
    )
    result = engine.predict(img)
    
    assert "emotion" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_confident"], bool)