from pathlib import Path
import mlflow
from src.constants import ARTIFACTS_PATH

MLFLOW_STORE_PATH = Path(f"{ARTIFACTS_PATH}/mlruns")
MLFLOW_STORE_PATH.mkdir(parents=True, exist_ok=True)

_mlflow_initialized = False

def init_mlflow(experiment_name: str = "emotion_classification"):
    global _mlflow_initialized
    if not _mlflow_initialized:
        mlflow.set_tracking_uri(f"file://{MLFLOW_STORE_PATH}")
        _mlflow_initialized = True
    mlflow.set_experiment(experiment_name)
    return mlflow