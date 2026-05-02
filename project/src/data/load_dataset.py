from dotenv import load_dotenv
from src.constants import DATA_PATH, CONFIG_PATH
import os   

load_dotenv(f"{CONFIG_PATH}/.env")
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

# print("Начало скачивания...")
# print("KAGGLE_USERNAME:", os.getenv("KAGGLE_USERNAME"))  # Должно показать ваш логин
# print("KAGGLE_KEY:", os.getenv("KAGGLE_KEY")[:10] + "...")  # Первые 10 символов ключа

# path = kagglehub.dataset_download("msambare/fer2013", path=DATA_PATH)



print("Готово!")