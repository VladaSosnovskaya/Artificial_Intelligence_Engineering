# S04 – eda_cli: HTTP-сервис качества датасетов (FastAPI)

Расширенная версия проекта `eda-cli` из Семинара 03.

К существующему CLI-приложению для EDA добавлен **HTTP-сервис на FastAPI** с эндпоинтами `/health`, `/quality` и `/quality-from-csv`.  
Используется в рамках Семинара 04 курса «Инженерия ИИ».

---

## Связь с S03

Проект в S04 основан на том же пакете `eda_cli`, что и в S03:

- сохраняется структура `src/eda_cli/` и CLI-команда `eda-cli`;
- добавлен модуль `api.py` с FastAPI-приложением;
- в зависимости добавлены `fastapi` и `uvicorn[standard]`.

Цель S04 – показать, как поверх уже написанного EDA-ядра поднять простой HTTP-сервис.

---

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему
- Браузер (для Swagger UI `/docs`) или любой HTTP-клиент:
  - `curl` / HTTP-клиент в IDE / Postman / Hoppscotch и т.п.

---

## Инициализация проекта

В корне проекта (каталог S04/eda-cli):

```bash
uv sync
```

Команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml` (включая FastAPI и Uvicorn);
- установит сам проект `eda-cli` в окружение.

---

## Запуск CLI (как в S03)

CLI остаётся доступным и в S04.

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

- `--sep` - разделитель (по умолчанию `,`);
- `--encoding` - кодировка (по умолчанию `utf-8`).

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

---

## Запуск HTTP-сервиса

HTTP-сервис реализован в модуле `eda_cli.api` на FastAPI.

### Запуск Uvicorn

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Пояснения:

- `eda_cli.api:app` - путь до объекта FastAPI `app` в модуле `eda_cli.api`;
- `--reload` - автоматический перезапуск сервера при изменении кода (удобно для разработки);
- `--port 8000` - порт сервиса (можно поменять при необходимости).

После запуска сервис будет доступен по адресу:

```text
http://127.0.0.1:8000
```

---

## Эндпоинты сервиса

### 1. `GET /health`

Простейший health-check.

**Запрос:**

```http
GET /health
```

**Ожидаемый ответ `200 OK` (JSON):**

```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

Пример проверки через `curl`:

```bash
curl http://127.0.0.1:8000/health
```

---

### 2. Swagger UI: `GET /docs`

Интерфейс документации и тестирования API:

```text
http://127.0.0.1:8000/docs
```

Через `/docs` можно:

- вызывать `GET /health`;
- вызвать `GET /metrics`;
- вызывать `POST /quality` (форма для JSON);
- вызывать `POST /quality-from-csv` (форма для загрузки файла);
- вызвать `POST /quality-flags-from-csv` (форма для загрузки файла).

---

### 3. `POST /quality` – заглушка по агрегированным признакам

Эндпоинт принимает **агрегированные признаки датасета** (размеры, доля пропусков и т.п.) и возвращает эвристическую оценку качества.

**Пример запроса:**

```http
POST /quality
Content-Type: application/json
```

Тело (были добавлены новые эвристики из домашнего задания 3):

```json
{
  "n_rows": 10000,
  "n_cols": 12,
  "max_missing_share": 0.15,
  "numeric_cols": 8,
  "categorical_cols": 4,
  "has_constant_columns": true,
  "has_high_uniq_cat": true,
  "has_id_duplicates": true
}
```

**Пример ответа `200 OK`:**

```json
{
  "ok_for_model": false,
  "quality_score": 0.6,
  "message": "Качество данных недостаточно, требуется доработка (по текущим эвристикам).",
  "latency_ms": 0.01109996810555458,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "no_numeric_columns": false,
    "no_categorical_columns": false,
    "has_constant_columns": true,
    "has_high_uniq_cat": true,
    "has_id_duplicates": true
  },
  "dataset_shape": {
    "n_rows": 10000,
    "n_cols": 12
  }
}
```

**Пример вызова через `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{"n_rows": 10000, "n_cols": 12, "max_missing_share": 0.15, "numeric_cols": 8, "categorical_cols": 4, "has_constant_columns": true, "has_high_uniq_cat": true, "has_id_duplicates": true}'
```

---

### 4. `POST /quality-from-csv` – оценка качества по CSV-файлу

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;
- возвращает оценку качества датасета в том же формате, что `/quality`.

**Запрос:**

```http
POST /quality-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

Ответ будет содержать:

- `ok_for_model` - результат по эвристикам;
- `quality_score` - интегральный скор качества;
- `flags` - булевы флаги из `compute_quality_flags`;
- `dataset_shape` - реальные размеры датасета (`n_rows`, `n_cols`);
- `latency_ms` - время обработки запроса.

---

### 4. `GET /metrics` – вывод отслеживаемых метрик

**Запрос:**

```http
GET /metrics
```

**Пример ответа `200 OK` (JSON):**

```json
{
  "total_requests": 4,
  "avg_latency_ms": 6.63
}
```

Пример проверки через `curl`:

```bash
curl http://127.0.0.1:8000/metrics
```

---

### 5. `POST /quality-flags-from-csv` – получение флагов качества по загруженному CSV-файлу


Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;
- возвращает набор флагов качества, вычисленных на основе реальных данных.

**Запрос:**

```http
POST /quality-flags-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-flags-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```

В ответе возвращается JSON со структурой flags, содержащей булевы значения ключевых эвристик качества:

- too_few_rows — мало ли строк;
- too_many_missing — много ли столбцов;
- has_constant_columns — есть ли колонки с одинаковыми значениями;
- has_high_uniq_categoricals — есть ли категориальные признаки с большим количеством уникальных значений;
- has_id_duplicates — обнаружены ли дубликаты в колонках с id.

---

## Структура проекта (упрощённо)

```text
S04/
  eda-cli/
    pyproject.toml
    README.md                # этот файл
    src/
      eda_cli/
        __init__.py
        core.py              # EDA-логика, эвристики качества
        viz.py               # визуализации
        cli.py               # CLI (overview/report)
        api.py               # HTTP-сервис (FastAPI)
    tests/
      test_core.py           # тесты ядра
    data/
      example.csv            # учебный CSV для экспериментов
```

---

## Тесты

Запуск тестов (как и в S03):

```bash
uv run pytest -q
```

Рекомендуется перед любыми изменениями в логике качества данных и API:

1. Запустить тесты `pytest`;
2. Проверить работу CLI (`uv run eda-cli ...`);
3. Проверить работу HTTP-сервиса (`uv run uvicorn ...`, затем `/health` и `/quality`/`/quality-from-csv` через `/docs` или HTTP-клиент).
