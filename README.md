\# Instagram API Review Pack



This app demonstrates \*\*minimum scopes\*\* for Instagram Graph API and provides a short, repeatable flow for Meta App Review.



\## Files

\- `app.py` — FastAPI single-file app (real API flows)

\- `requirements.txt`

\- `.env.example`



\## How to run

```bash

python -m venv .venv

\# Windows: .venv\\Scripts\\activate

\# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

uvicorn app:app --host 0.0.0.0 --port 8000

## Scopes used

- `instagram_basic` — display IG profile fields
- `instagram_manage_insights` — display insights
- `pages_show_list` — page linkage for business/creator

## Review steps (<=3 minutes)

1. Open `https://<REVIEW_URL>/` and click `/auth/login`
2. After callback, GET `/auth/status` returns `{ "logged_in": true }`
3. GET `/me/profile` returns `id, username, followers_count, media_count`
4. GET `/me/insights?metric=impressions,reach` returns JSON (period=day)
5. POST `/auth/logout`, then `/auth/status` returns `false`

## Privacy / Data Deletion

- `/privacy` and `/data-deletion` routes are included.




