#!/bin/sh
set -e

read_env_value() {
  key="$1"
  if [ -f ./.env ]; then
    grep -E "^${key}=" ./.env | head -n 1 | cut -d= -f2-
  fi
}

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-europe-west2}"
REPO="${REPO:-capstone}"
IMAGE_PREFIX="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}"

DJANGO_SERVICE="${DJANGO_SERVICE:-capstone-web}"
DEALERSHIP_SERVICE="${DEALERSHIP_SERVICE:-capstone-dealership-api}"
REVIEWS_SERVICE="${REVIEWS_SERVICE:-capstone-reviews-api}"

MONGODB_URI="${MONGODB_URI:-$(read_env_value MONGODB_URI)}"
MONGODB_DB_NAME="${MONGODB_DB_NAME:-$(read_env_value MONGODB_DB_NAME)}"
MONGODB_DEALERS_COLLECTION="${MONGODB_DEALERS_COLLECTION:-$(read_env_value MONGODB_DEALERS_COLLECTION)}"
MONGODB_REVIEWS_COLLECTION="${MONGODB_REVIEWS_COLLECTION:-$(read_env_value MONGODB_REVIEWS_COLLECTION)}"
DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-$(read_env_value DJANGO_SECRET_KEY)}"

MONGODB_URI="${MONGODB_URI:?Set MONGODB_URI in .env}"
MONGODB_DB_NAME="${MONGODB_DB_NAME:-dealerships_db}"
MONGODB_DEALERS_COLLECTION="${MONGODB_DEALERS_COLLECTION:-dealerships}"
MONGODB_REVIEWS_COLLECTION="${MONGODB_REVIEWS_COLLECTION:-reviews}"
DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-change-me-in-cloud-run}"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cat > "${tmp_dir}/dealership-env.env" <<EOF
MONGODB_URI=${MONGODB_URI}
MONGODB_DB_NAME=${MONGODB_DB_NAME}
MONGODB_DEALERS_COLLECTION=${MONGODB_DEALERS_COLLECTION}
EOF

cat > "${tmp_dir}/reviews-env.env" <<EOF
MONGODB_URI=${MONGODB_URI}
MONGODB_DB_NAME=${MONGODB_DB_NAME}
MONGODB_REVIEWS_COLLECTION=${MONGODB_REVIEWS_COLLECTION}
EOF

gcloud artifacts repositories describe "$REPO" \
  --location="$REGION" >/dev/null 2>&1 || \
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION"

gcloud builds submit ./functions/dealership-service \
  --tag "${IMAGE_PREFIX}/${DEALERSHIP_SERVICE}:latest"

gcloud run deploy "$DEALERSHIP_SERVICE" \
  --image "${IMAGE_PREFIX}/${DEALERSHIP_SERVICE}:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --env-vars-file "${tmp_dir}/dealership-env.env"

gcloud builds submit ./functions/reviews-service \
  --tag "${IMAGE_PREFIX}/${REVIEWS_SERVICE}:latest"

gcloud run deploy "$REVIEWS_SERVICE" \
  --image "${IMAGE_PREFIX}/${REVIEWS_SERVICE}:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 5000 \
  --env-vars-file "${tmp_dir}/reviews-env.env"

DEALERSHIP_URL="$(gcloud run services describe "$DEALERSHIP_SERVICE" --region "$REGION" --format='value(status.url)')"
REVIEWS_URL="$(gcloud run services describe "$REVIEWS_SERVICE" --region "$REGION" --format='value(status.url)')"

cat > "${tmp_dir}/web-env-initial.env" <<EOF
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
DEALERSHIP_API_URL=${DEALERSHIP_URL}/api/dealership
REVIEW_API_URL=${REVIEWS_URL}/api/review
EOF

gcloud builds submit ./server \
  --tag "${IMAGE_PREFIX}/${DJANGO_SERVICE}:latest"

gcloud run deploy "$DJANGO_SERVICE" \
  --image "${IMAGE_PREFIX}/${DJANGO_SERVICE}:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --env-vars-file "${tmp_dir}/web-env-initial.env"

WEB_URL="$(gcloud run services describe "$DJANGO_SERVICE" --region "$REGION" --format='value(status.url)')"
WEB_HOST="$(printf '%s' "$WEB_URL" | sed 's#https\?://##')"

cat > "${tmp_dir}/web-env-final.env" <<EOF
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=${WEB_HOST}
DJANGO_CSRF_TRUSTED_ORIGINS=${WEB_URL}
DEALERSHIP_API_URL=${DEALERSHIP_URL}/api/dealership
REVIEW_API_URL=${REVIEWS_URL}/api/review
EOF

gcloud run services update "$DJANGO_SERVICE" \
  --region "$REGION" \
  --env-vars-file "${tmp_dir}/web-env-final.env"

echo "Dealership API: ${DEALERSHIP_URL}"
echo "Reviews API: ${REVIEWS_URL}"
echo "Web app: ${WEB_URL}"
