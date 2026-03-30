# Car Dealership App

This project is a Django web app with two small backend API services:

- a dealership API running on Node.js
- a reviews API running on Flask

The project now uses:

- MongoDB Atlas for dealership and review data
- local Django auth with SQLite for users/admin
- local VADER sentiment analysis instead of Watson NLU

## Project Structure

- `server/`: Django web app
- `functions/dealership-service/`: local dealership API
- `functions/reviews-service/`: local reviews API
- `cloudant/data/`: source JSON files you can use to seed MongoDB Atlas

## Prerequisites

- Python 3.12
- Node.js 20 or similar recent version
- MongoDB Atlas cluster and connection string

## Environment Setup

1. Copy the example env file:

```bash
cp .env.example .env
```

2. Fill in these values in `.env`:

```env
MONGODB_URI=...
MONGODB_DB_NAME=dealerships_db
MONGODB_DEALERS_COLLECTION=dealerships
MONGODB_REVIEWS_COLLECTION=reviews
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
DEALERSHIP_API_URL=http://localhost:3000/api/dealership
REVIEW_API_URL=http://localhost:5000/api/review
```

To generate a Django secret key:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Install Dependencies

Install Python dependencies for Django:

```bash
cd server
python3 -m pip install -r requirements.txt
```

Install Node dependencies for the dealership API:

```bash
cd ../functions/dealership-service
npm install
```

Install Python dependencies for the reviews API:

```bash
cd ../reviews-service
python3 -m pip install -r requirements.txt
```

## Seed MongoDB Atlas

Create these collections in your Atlas database:

- `dealerships`
- `reviews`

Recommended database name:

- `dealerships_db`

You can import data from:

- `cloudant/data/dealerships.json`
- `cloudant/data/reviews.json`

Important:

- Those files are wrapped as `{ "dealerships": [...] }` and `{ "reviews": [...] }`
- The app currently supports that wrapped import format
- A cleaner long-term format is one Mongo document per dealer/review

## Run Locally

Start the dealership API:

```bash
cd functions/dealership-service
node get-dealership.js
```

Start the reviews API in another terminal:

```bash
cd functions/reviews-service
python3 reviews.py
```

Start Django in another terminal:

```bash
cd server
python3 manage.py migrate
python3 manage.py runserver
```

Open the app:

- `http://127.0.0.1:8000/djangoapp/`

Open Django admin:

- `http://127.0.0.1:8000/admin/`

## Create a Django Admin User

If you need an admin account:

```bash
cd server
python3 manage.py createsuperuser
```

## Local URLs

- Django web app: `http://127.0.0.1:8000/djangoapp/`
- Django admin: `http://127.0.0.1:8000/admin/`
- Dealership API: `http://127.0.0.1:3000/api/dealership`
- Reviews API: `http://127.0.0.1:5000/api/review`

## Static Assets

Sentiment emoji images are served from:

- `server/static/emoji/positive.png`
- `server/static/emoji/negative.png`
- `server/static/emoji/neutral.png`

## Common Issues

### No dealerships appear on the home page

This usually means:

- MongoDB Atlas has no dealership data
- `.env` points to the wrong DB or collection
- the dealership API is not running

### Reviews page shows no data

This usually means:

- the selected dealership has no matching review documents
- the reviews API is not running

### MongoDB TLS certificate errors on macOS

If you see `CERTIFICATE_VERIFY_FAILED`, your local Python trust store is likely missing CA certificates.

Typical fixes:

```bash
python3 -m pip install --upgrade certifi pymongo
```

and, if needed on macOS, run the Python certificate installer that came with your Python installation.

### `/.well-known/appspecific/com.chrome.devtools.json` not found

This is harmless browser noise and can be ignored.

## Cloud Deployment

