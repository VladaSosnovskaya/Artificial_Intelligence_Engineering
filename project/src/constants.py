from typing import Final
from pathlib import Path

# PROJECT_ROOT = Path.cwd().parent
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
ARTIFACTS_PATH = f"{PROJECT_ROOT}/artifacts"
CHECKPOINTS_PATH = f"{ARTIFACTS_PATH}/checkpoints"
FIGURES_PATH = f"{ARTIFACTS_PATH}/figures"
DATA_PATH = f"{PROJECT_ROOT}/data/FER-dataset"
CONFIG_PATH = f"{PROJECT_ROOT}/configs"

STATIC_PATH = f"{PROJECT_ROOT}/src/service/static"

EMOTION_LABELS: Final[list[str]] = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
LABEL_TO_IDX: Final[dict[str, int]] = {name: i for i, name in enumerate(EMOTION_LABELS)}
IDX_TO_LABEL: Final[dict[int, str]] = {i: name for i, name in enumerate(EMOTION_LABELS)}

NUM_CLASSES: Final[int] = len(EMOTION_LABELS)