В папке project

sudo apt update
sudo apt install python3-venv
python3 -m venv project_venv
source project_venv/bin/activate

pip install --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
ИЛИ
pip install --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124

pip install -r requirements.txt
pip install ipykernel

Скачать датасет
python -m src.data.load_dataset

Запуск тестов (проверка датасета - загрузки, форматов тензоров, наличия классов) 
PYTHONPATH=. python -m pytest tests/test_data -v
Ожидание: 3 passed в консоли

pip install -e .
Устанавливает проект в режиме разработки (чтобы можно было делать import src)

Все файлы из notebooks - Это типа "эксперименты", которые мы проводим - выбираем лучшую стратегию обучения (лучшие модели, аугментации). При этом все результаты также записываются в mlflow (должна быть одна функция, куда передаются название эксперимента, оригиналы и предсказания модели, и гиперпараметры обучения). Для обучения используются тренировочный и валидационных наборы данных, для финального теста только тестовый
1) exp01_eda - первичный анализ данных - ничего не сохраняется
2) exp02_baseline_models - эксперимент над LogisticRegression и RandomForest - в папку artifacts сохраняются чекпоинты, создается файл "metrics.csv": название модели + метрики
3) exp03_cnn - несколько экспериментов с CNN - сохраняются чекпоинты и метрики записываются в metrics.csv
4) exp04_augs - проверка аугментаций - сохраняются графики и метрики metrics.csv
5) exp05_metrics - считываются метрики из metric.csv, выбирается лучший подход, график сохраняется

Запуск mlflow:
mlflow ui --backend-store-uri file://$(pwd)/artifacts/mlruns --host 0.0.0.0 --port 5000
http://localhost:5000

В src уже используется финальный лучший результат
1) constants.py - все важные переменные и пути
2) train.py - скрипт для обучения модели пользователем
3) eval.py - скрипт для оценки модели пользователем

4) data/loader.py - описан класс датасета и функция для создания dataloaders (принимает путь к датасету - создает тренировочный, валидационный и тестовый наборы данных), по умолчанию без аугментаций
5) models/baseline - код для обучения базовых моделей
6) models/cnn - код для обучения cnn
7) features/image_transform.py - код с описанием аугментаций
8) utils/experiment_logger - функция для логирования экспериментов в MLflow и сохранения в metrics.csv
9) utils/mlflow_config - функция для инициализации MLflow

10) service
uvicorn src.service.api:app --host 0.0.0.0 --port 8000 --reload

Проверки из консоли:
curl -s http://localhost:8000/health
вывод: {"status":"healthy","device":"cpu"}

curl -s -X POST -F "file=@data/train/angry/Training_3908.jpg" http://localhost:8000/predict
вывод: {"status":"success","data":{"emotion":"unknown","confidence":0.2264,"is_confident":false,"device":"cpu"}}v

curl -s http://localhost:8000/metrics
вывод: {"request_counts":{"/predict":1,"/predict_latency":0.21071934700012207},"avg_latency_ms":210.72}

Открыть по ссылке localhost:8000

В artifacts сохраняются все результаты экспериментов и итоговые результаты проекта, а также эксперименты mlflow

Запустить все тесты
pytest tests/ -v

