import mlflow
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score
from src.constants import ARTIFACTS_PATH, CONFIG_PATH
from src.utils.mlflow_config import init_mlflow
import yaml

METRICS_CSV = Path(f"{ARTIFACTS_PATH}/metrics.csv")

def log_experiment(experiment_name, model_name, y_true, y_pred, training_config):
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    
    init_mlflow("emotion_classification")
    with mlflow.start_run() as run:
        mlflow.set_tag("experiment", experiment_name)
        mlflow.log_param("model_name", model_name)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_macro", f1)
        
        for k, v in training_config.items():
            mlflow.log_param(k, v)
            
    row = {"experiment": experiment_name, "model": model_name, "accuracy": acc, "f1_macro": f1}  
    if METRICS_CSV.exists():
        df = pd.read_csv(METRICS_CSV)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(METRICS_CSV, index=False)

    config_path = f"{CONFIG_PATH}/training_config_{model_name}.yaml"

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(training_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"{model_name} | Acc={acc:.3f} | F1={f1:.3f} | Лог сохранен в MLflow и metrics.csv, конфиг записан в {config_path}")
    return {"accuracy": acc, "f1_macro": f1}
