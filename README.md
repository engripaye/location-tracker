# Location Tracker API

Secure, consent-based live location tracking backend built with FastAPI.

## Features

- Login and register endpoints
- JWT-protected account, session, location-history, and SOS endpoints
- Rotating refresh tokens stored as hashes
- Supabase-compatible PostgreSQL through `DATABASE_URL`
- Alembic migrations
- WebSockets for live tracking updates
- Expiring share links
- Google Maps reverse geocoding with OpenStreetMap fallback
- Hashed device fingerprinting
- Emergency SOS endpoint
- Redis caching for reverse geocoding
- Docker Compose deployment
- GitHub Actions CI pipeline

## Run With Docker

```bash
cp .env.example .env
docker compose up --build
```

Open:

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

For Supabase, set `DATABASE_URL` to the Supabase PostgreSQL connection string:

```bash
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres
```

## Core Endpoints

Authentication:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

Sessions:

- `POST /sessions/start`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `POST /sessions/{session_id}/stop`

Tracking:

- `POST /track/{share_token}/location`
- `GET /track/{share_token}`
- `GET /sessions/{session_id}/locations`
- `WS /ws/track/{share_token}`

Emergency:

- `POST /sos`
- `GET /sos`

## Example Flow

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Device-Fingerprint: demo-device" \
  -d '{"name":"Amina","email":"amina@example.com","password":"strong-password"}'
```

Create a session:

```bash
curl -X POST http://127.0.0.1:8000/sessions/start \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expires_in_hours":24}'
```

Submit location from the shared device:

```bash
curl -X POST http://127.0.0.1:8000/track/SHARE_TOKEN/location \
  -H "Content-Type: application/json" \
  -H "X-Device-Fingerprint: demo-phone" \
  -d '{"latitude":6.5244,"longitude":3.3792,"accuracy":12}'
```

Trigger SOS:

```bash
curl -X POST http://127.0.0.1:8000/sos \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"latitude":6.5244,"longitude":3.3792,"message":"Need help"}'
```

## Environment

- `DATABASE_URL`: PostgreSQL URL, including Supabase URLs
- `REDIS_URL`: optional Redis URL for reverse-geocoding cache
- `JWT_SECRET_KEY`: long random secret for JWT signing
- `GOOGLE_MAPS_API_KEY`: optional Google reverse-geocoding key

## Privacy

Location data is sensitive. Use HTTPS, strong secrets, short retention windows,
audit logs, and clear consent before using this with real people.
