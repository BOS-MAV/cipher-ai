# CIPHER AI Starter

A small public web application that lets a user ask natural-language questions about the CIPHER phenotype library. The browser never receives the CIPHER client secret or the OpenAI API key.

## Architecture

```text
GitHub Pages (HTML/JS)
        |
        | HTTPS POST /api/ask
        v
FastAPI backend
   |           |
   |           +--> OpenAI Responses API + function tools
   |
   +--------------> CIPHER Web API (OAuth2 client credentials)
```

## Included CIPHER tools

- Search phenotypes
- Get a phenotype by ID or UQID
- Compare phenotypes
- Search data-dictionary variables
- Search data dictionaries
- Get a dictionary and variables
- Retrieve field enumerations

The implementation follows the uploaded CIPHER OpenAPI 3.1 description. Search endpoints are represented there as an object-valued query parameter plus an array-valued JSON request body. This starter serializes the query object using OpenAPI's default `form` + `explode` behavior (individual query parameters) and sends search field filters as the JSON body.

## 1. Run locally

Use Python 3.11+.

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and add:

```text
OPENAI_API_KEY=...
CIPHER_CLIENT_ID=...
CIPHER_CLIENT_SECRET=...
```

Then run the backend:

```bash
uvicorn main:app --reload --port 8001
```

In a second terminal, serve the frontend:

```bash
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000`.

Useful backend URLs:

- `http://localhost:8001/health`
- `http://localhost:8001/docs` (automatic FastAPI Swagger UI)

## 2. Test CIPHER before adding OpenAI

From the `backend` directory with `.env` populated:

```bash
python -c "from cipher_client import CipherClient; import json; print(json.dumps(CipherClient().search_phenotypes('diabetes', limit=3), indent=2)[:10000])"
```

If authentication and search serialization are accepted by the server, you should receive CIPHER JSON. If CIPHER's deployed implementation expects a non-default serialization for the `request` query object, this is the one area to adjust in `_post_search()`.

## 3. Test the complete backend

```bash
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Find validated diabetes phenotypes."}'
```

## 4. Deploy the Python API to Render

A `render.yaml` is included.

1. Push this repository to GitHub.
2. In Render, create a Blueprint from the repository.
3. Add secret environment variables:
   - `OPENAI_API_KEY`
   - `CIPHER_CLIENT_ID`
   - `CIPHER_CLIENT_SECRET`
4. Set `ALLOWED_ORIGINS` to the exact GitHub Pages origin, for example:
   `https://YOUR-GITHUB-USERNAME.github.io`
5. Deploy and note the backend URL, such as `https://cipher-ai-api.onrender.com`.

You can use Railway, Fly.io, Azure App Service, AWS, or Google Cloud Run instead; FastAPI does not depend on Render.

## 5. Publish the frontend with GitHub Pages

Edit `frontend/config.js`:

```js
window.CIPHER_AI_API_BASE = "https://YOUR-BACKEND.example.com";
```

A GitHub Actions workflow is included at `.github/workflows/pages.yml`. In GitHub, enable Pages and choose **GitHub Actions** as the source. Each push to `main` that changes `frontend/` will publish that directory. Do **not** place `.env`, client secrets, bearer tokens, or API keys in the frontend or repository.

## Security and production notes

The starter includes a small in-memory per-IP rate limiter. That is useful for testing but is not sufficient for a heavily used public service because it resets on restart and does not coordinate across multiple server instances. Before a broad public launch, consider a shared rate limiter (Redis), a WAF/CDN, bot protection such as Turnstile, logging/usage budgets, and explicit OpenAI project spend limits.

Also confirm that your CIPHER API agreement permits redisplaying the data through a public application. Authentication capability does not itself establish permission to republish every returned field, particularly if CIPHER data classifications or attachments have access restrictions.

## Why the backend calls CIPHER instead of the browser

The CIPHER token endpoint requires a `client_id` and `client_secret`. The backend exchanges them for a short-lived access token and sends the resulting Bearer token to CIPHER. The browser receives only the final answer and a sanitized list of tool arguments; credentials are never returned.

## Next additions worth making

1. Result cards that link to individual CIPHER phenotype records.
2. Conversation history using `previous_response_id` or an application session.
3. A dedicated "Compare" UI for selected phenotypes.
4. Better source/provenance rendering from CIPHER IDs and UQIDs.
5. Redis-backed rate limiting and usage accounting.
6. An allowlist of CIPHER fields permitted for public display.
7. Automated integration tests against a non-production CIPHER account.
