# BmovieDb

BmovieDb is a movie discovery frontend built with Next.js, React, and TypeScript, backed by the FastAPI service in `backend/`. Browse and search the movie catalog, filter by genre, sort results, create an account, save a watchlist, and rate and review films.

## Run locally

1. Configure the backend environment in `backend/.env` (at minimum, set `DATABASE_URL` and `JWT_SECRET_KEY`), start PostgreSQL, apply the Alembic migrations, and run the API:

   ```powershell
   docker compose up -d db
   cd backend
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

2. In another terminal, install and start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000). The frontend uses `http://localhost:8000` by default. To point it elsewhere, create `frontend/.env.local`:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

   If the frontend is served from a different origin, set `FRONTEND_ORIGIN` in `backend/.env` to that exact origin. The local API also permits `http://127.0.0.1:3000`.

The frontend calls the existing `/movies`, `/genres`, `/auth`, and `/users` endpoints directly. The API does not expose poster artwork, so film imagery in the interface is decorative and does not represent backend movie metadata.

## Frontend pages

- `/` redirects to `/discover`.
- `/discover` browses the active movie catalog, with pagination and sorting.
- `/search` provides title, genre, release-year, minimum-rating, and sort filters. A search from the header opens this page with the title prefilled.
- `/profile` provides account registration/sign-in and the signed-in member profile.
- `/profile/watchlist` lists saved movies and lets signed-in users remove them.
