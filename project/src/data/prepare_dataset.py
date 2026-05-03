from pathlib import Path
import os
from PIL import Image
from src.constants import DATA_PATH


removed_count = 0
errors = []

for img_path in Path(DATA_PATH).rglob("*.jpg"):
    try:
        img = Image.open(img_path)
        img.load()  # Принудительная проверка целостности

        # Если изображение полностью чёрное или пустое
        if img.getbbox() is None or min(img.getdata()) == max(img.getdata()) == 0:
            os.remove(img_path)
            print(f"Удалено: {str(img_path)}")
            removed_count += 1

    except Exception as e:
        errors.append((img_path.name, str(e)))

print(f"Удалено файлов: {removed_count}")

if errors:
    print(f"Ошибки при обработке: {len(errors)}")
    for name, err in errors[:5]:
        print(f"{name}: {err}")
        
