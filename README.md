# APP

A simple async job proxy API built with Starlette and aiohttp.

## Requirements

- Python 3.9+
- pip

## Setup

0. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

1. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   pip install -r requirements_dev.txt

   ```

## Running the Application

Start the Starlette app using `uvicorn`:

```sh
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Running Tests

Run the unit tests with coverage using `tox`:

```sh
tox -e unit
```

## Code Formatting and Linting

To check formatting and linting:

```sh
tox -e yapfen
tox -e flake8
```

## Type Checking

To run type checks:

```sh
tox -e typecheck
```

## API Endpoints

- `POST /proxy` — Start a new async job.
- `POST /callback/{job_id}` — Callback endpoint for job completion.
- `GET /status/{job_id}` — Check job status.

---