
# Integrated AI Assistant

An AI-powered assistant built using FastAPI, Ollama, PostgreSQL, and Python. It supports document question answering, CRM customer lookup, order information retrieval, and email drafting.

## Features

- Document upload and question answering
- CRM customer lookup by ID and email
- Order status and customer order retrieval
- Email drafting with configurable tone
- LLM-powered responses using Ollama
- Unit testing with mocked database responses
- End-to-end testing with response-time tracking

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Ollama (Llama 3.2:1b)
- SQLAlchemy
- Requests
- Pytest

## Project Structure

```text
integrated_AI_Assistant/
│
├── app/
│   ├── main.py
│   └── tools.py
│
├── crm/
│   └── main.py
│
├── orders/
│   └── tools.py
│
├── tests/
│   ├── test_crm.py
│   ├── test_orders.py
│   ├── test_scenarios.py
│   ├── test_report.py
│   └── test_results.csv
│
├── uploads/
│   └── sample.txt
│
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd integrated_AI_Assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn requests python-dotenv ollama pytest psycopg2-binary sqlalchemy
```

### 4. Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Add the required database connection settings and CRM configuration.

Do not commit real credentials or API keys.

### 5. Start Ollama

Make sure Ollama is installed and running.

Pull the model:

```bash
ollama pull llama3.2:1b
```

### 6. Start the CRM service

```bash
uvicorn crm.main:app --reload --port 8001
```

### 7. Start the main API

Open another terminal:

```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Open Swagger UI:

http://127.0.0.1:8000/docs

Main endpoints include:

- `POST /chat` – Chat with the AI assistant
- `POST /documents` – Upload documents
- `POST /draft-email` – Generate an email draft

CRM service runs on port `8001`.

## Testing

Run unit tests:

```bash
python -m pytest tests/ -v
```

Run end-to-end tests:

```bash
python tests/test_report.py
```

The E2E report is saved to:

`tests/test_results.csv`

## Test Results

- Total E2E scenarios: 10
- Passed: 10
- Failed: 0
- CRM and order unit tests: 6 passed

All 10 E2E scenarios passed during the recorded test run.

## Security

- Keep `.env` out of Git.
- Use `.env.example` with placeholder values.
- Never commit database passwords or API keys.

## Future Improvements

- Add semantic search using embeddings and a vector database.
- Improve document retrieval for large files.
- Add authentication and authorization.
- Add more automated integration tests.
