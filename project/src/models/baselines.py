import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib
from src.constants import CHECKPOINTS_PATH

def prepare_flat_features(dataloader):
    """
    Преобразует батчи изображений (B, 1, H, W) в плоские векторы (B, H*W).
    Используется только для классических ML-моделей.
    """
    print("Подготовка данных (flattening + scaling)...")
    X, y = [], []
    for images, labels in dataloader:
        # images: (B, 1, 48, 48) -> flatten to (B, 2304)
        X.append(images.view(images.size(0), -1).numpy())
        y.append(labels.numpy())
    return np.vstack(X), np.concatenate(y)


def train_baseline_models(X_train, y_train):
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs", 
            class_weight="balanced", n_jobs=-1, random_state=42
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=15, 
            class_weight="balanced", n_jobs=-1, random_state=42
        )
    }

    results = {}

    for name, model in models.items():
        print(f"\nОбучение {name}...")
        model.fit(X_train, y_train)
        results[name] = model

        artifact_path = f"{CHECKPOINTS_PATH}/{name}_baseline.pkl"
        joblib.dump({"model": model}, artifact_path)
        print(f"Артефакт сохранен в {artifact_path}")

    return results