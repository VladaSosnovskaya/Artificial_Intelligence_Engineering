from dotenv import load_dotenv
from src.constants import DATA_PATH, PROJECT_ROOT
import os   

load_dotenv(f"{PROJECT_ROOT}/.env")
os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")

from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

print("Начало скачивания...")

api.dataset_download_files(
    "msambare/fer2013",
    path=DATA_PATH,
    unzip=True
)

print("Готово!")