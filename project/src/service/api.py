import time
import logging
from collections import defaultdict
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from src.service.inference import engine
from PIL import Image
import io
from src.constants import STATIC_PATH

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Логирование
logging.basicConfig(
    level=getattr(logging, "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("emotion_api")

# Метрики в памяти (для эндпоинта /metrics)
metrics = defaultdict(int) # счетчик запросов
request_times = [] # счетчик времени обработки запросов

app = FastAPI(title="Emotion Classification Service", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(STATIC_PATH)), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_path = f"{STATIC_PATH}/index.html"
    return FileResponse(str(index_path))

# обертка для всех запросов 
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    # засекаем время старта - выполняем запрос - засекаем время окончания
    start = time.time() 
    response = await call_next(request)
    duration = time.time() - start

    # обновляем метрики
    request_times.append(duration)
    metrics[request.url.path] += 1
    metrics[f"{request.url.path}_latency"] += duration

    # логированое 
    logger.info(f"{request.method} {request.url.path} | {response.status_code} | {duration*1000:.1f}ms")
    return response


@app.get("/health")
async def health_check():
    if hasattr(engine, "model") and engine.model is not None: # загрузилась ли модель
        return {"status": "healthy", "device": str(engine.device)}
    return {"status": "degraded", "message": "Model not loaded"}


@app.post("/predict")
async def predict_emotion(file: UploadFile = File(...)):
    # Валидация типа
    if not file.content_type or "image" not in file.content_type:
        raise HTTPException(415, detail="Поддерживатся только изображения")

    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB") 
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        raise HTTPException(500, detail="Ошибка загрузки изображения")

    try:
        result = engine.predict(image)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Ошибка инференса: {e}")
        raise HTTPException(500, detail="Ошибка инференса")


@app.get("/metrics")
async def get_metrics():
    avg_latency = sum(request_times)/len(request_times)*1000 if request_times else 0
    return {
        "request_counts": dict(metrics),
        "avg_latency_ms": round(avg_latency, 2)
    }