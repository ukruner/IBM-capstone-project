# Cloud Run Deployment

This project deploys as three Cloud Run services:

- `capstone-dealership-api`
- `capstone-reviews-api`
- `capstone-web`

## Prerequisites

1. Install and authenticate `gcloud`.
2. Enable these APIs in your GCP project:
   - Cloud Run
   - Cloud Build
   - Artifact Registry
3. Create a `.env` file locally with your MongoDB Atlas values.

## Required Environment Variables

For the API services:

- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `MONGODB_DEALERS_COLLECTION`
- `MONGODB_REVIEWS_COLLECTION`

For Django:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=<your-web-service-url-host>`
- `DJANGO_CSRF_TRUSTED_ORIGINS=<your-web-service-url>`
- `DEALERSHIP_API_URL=<dealership-api-url>/api/dealership`
- `REVIEW_API_URL=<reviews-api-url>/api/review`

## Build and Deploy

Set your project first:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

Then run:

```bash
PROJECT_ID=YOUR_PROJECT_ID REGION=europe-west2 ./deploy-cloud-run.sh
```

The deploy script will:

1. Build and deploy both API services
2. Read their generated Cloud Run URLs
3. Build and deploy the Django service
4. Update Django with the final host and CSRF origin settings

## Notes

- Cloud Run service URLs are assigned after deployment.
- Keep MongoDB credentials in environment variables, not in source control.
- If your MongoDB password contains reserved URL characters, URL-encode it inside `MONGODB_URI`.
