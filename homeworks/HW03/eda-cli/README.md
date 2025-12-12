# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Вывод первых n строк CSV-файла 

```bash
uv run eda-cli head data/example.csv
```

Параметры:

- `--n` - сколько строк вывести (по умолчанию 5);
- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

Новые параметры, которые были добавлены для reports в рамках домашнего задания:
- `title` - заголовок отчёта в файле report.md;
- `min_missing_share` - порог доли пропусков (0.0–1.0), выше которого колонка добавляется в missing.csv. По умолчанию 0;
- `top_k_categories` - сколько top-значений выводить для категориальных признаков (для всех файлов в top_categories).

Пример вызова eda-cli report с использованием всех новых параметров:
```bash
uv run eda-cli report --title "новый отчет" --min-missing-share 0.01 --top-k-categories 2  data/example.csv
```

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

Также есть второй вариант датасета (специально с плохими данными) для проверки расчета score с учетом новых эвристик:
```bash
uv run eda-cli report data/dataset_with_low_score.csv
```

## Тесты

```bash
uv run pytest -q
```
