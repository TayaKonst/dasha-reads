# Русский для Даши

Russian reading practice web app for kids. No login required — opens straight to the game.

## Local dev setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Supabase setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Settings → Database → Connection string → URI**
3. Copy the URI and change the scheme:
   - From: `postgresql://...`
   - To: `postgresql+asyncpg://...`
4. Append `?ssl=require` if you get SSL errors

Create a `.env` file:

```
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres?ssl=require
```

## Run migrations & seed

```bash
alembic upgrade head     # creates tables
python seed.py           # seeds 60 exercises
```

## Start dev server

```bash
uvicorn main:app --reload
```

- Game: http://localhost:8000/
- Stats: http://localhost:8000/stats

## Render.com deploy

1. Push this repo to GitHub
2. Create a new **Web Service** on Render, connect the repo
3. Set the **Root Directory** to `dasha-reads` (if needed)
4. Add env var `DATABASE_URL` in Render dashboard (Settings → Environment)
5. Deploy — Render runs `pip install` + `alembic upgrade head` then starts uvicorn

> **Note:** Free tier spins down after 15 min of inactivity. First request after sleep takes ~30–50 seconds.

## Add new exercises

Insert rows directly into the `exercises` table via Supabase Table Editor or `psql`:

```sql
INSERT INTO exercises (id, level, type, question_data, correct_answer, options, is_active)
VALUES (
  gen_random_uuid(), 0, 'letter',
  '{"display": "Ж", "hint": "Как жираф"}',
  'Ж',
  '["Ж", "З", "Ш", "Щ"]',
  true
);
```

Or re-run `python seed.py` to reset all exercises to the defaults.
