# AI Knowledge Base / Meetings

Интеллектуальная база знаний по протоколам совещаний с использованием технологий **RAG (Retrieval-Augmented Generation)**, **LangChain**, **ChromaDB**, **Ollama** и **FastAPI**.

Проект разработан в рамках производственной практики.

---

## Возможности

* загрузка протоколов совещаний;
* автоматический разбор структуры протокола;
* сохранение метаданных;
* индексация документов в ChromaDB;
* гибридный поиск (Hybrid Search):

  * Semantic Search;
  * Keyword Search;
  * фильтрация по метаданным;
* чат по базе знаний;
* генерация ответов с использованием локальной LLM;
* ссылки на использованные документы (citations);
* поиск связанных встреч;
* REST API;
* Web-интерфейс на FastAPI.

---

## Архитектура

```
data
        │
        ▼
meeting_parser.py
        │
        ▼
Document + metadata
        │
        ▼
ChromaDB
        │
        ▼
Hybrid Search
 ├── Semantic Search
 ├── Keyword Search
 └── Metadata Filters
        │
        ▼
Qwen (Ollama)
        │
        ▼
Ответ + Citations + Related Meetings
```

---

## Используемые технологии

* Python 3.11
* FastAPI
* LangChain
* ChromaDB
* Ollama
* Qwen
* HuggingFace Embeddings
* Jinja2
* HTML / CSS

---

## Структура проекта

```
meeting_kb/

├── data/                 # протоколы совещаний
├── chroma_db/            # векторная база данных
├── src/
│   ├── api.py
│   ├── ask.py
│   ├── ingest.py
│   ├── hybrid_search.py
│   ├── keyword_search.py
│   ├── vectorstore.py
│   ├── embeddings.py
│   ├── llm.py
│   ├── services/
│   │     └── search_service.py
│   ├── parsers/
│   │     ├── meeting_parser.py
│   │     └── filters.py
│   ├── templates/
│   │     └── index.html
│   └── static/
│         └── style.css
└── requirements.txt
```

---

## Установка

### 1. Клонировать репозиторий

```bash
git clone <repository_url>
cd meeting_kb
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Установка Ollama

Необходимо установить Ollama:

https://ollama.com

После установки загрузить модель:

```bash
ollama pull qwen3.5:9b
```

или другую модель, указанную в настройках проекта.

---

## Индексация документов

После добавления новых протоколов необходимо выполнить:

```bash
python -m src.ingest
```

Будет создана (или обновлена) база ChromaDB.

---

## Запуск консольного режима

```bash
python -m src.ask
```

После запуска можно задавать вопросы по базе знаний.

Пример:

```
Ваш вопрос:

Какие решения были приняты по CRM?
```

---

## Запуск Web-интерфейса

```bash
uvicorn src.api:app --reload
```

После запуска открыть браузер:

```
http://127.0.0.1:8000
```

---

## REST API

### Загрузка нового протокола

```
POST /upload
```

JSON:

```json
{
    "text": "Текст протокола..."
}
```

---

### Поиск по базе знаний

```
GET /search?q=<запрос>
```

Пример:

```
GET /search?q=CRM
```

Ответ:

```json
{
    "answer": "...",
    "sources": [...],
    "related": [...]
}
```

---

## Реализованные возможности MVP

* ✔ Автоматический парсинг протоколов
* ✔ Извлечение метаданных
* ✔ Индексация документов
* ✔ Semantic Search
* ✔ Keyword Search
* ✔ Hybrid Search
* ✔ Metadata Filters
* ✔ RAG
* ✔ Citations
* ✔ Related Meetings
* ✔ REST API
* ✔ Web-интерфейс
* ✔ iframe-ready

---

2026
