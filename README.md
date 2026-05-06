# NutriSense Context Engine

## Problem Statement
Most food apps fail because they're reactive — they wait for you to open them. NutriSense is different: it detects behavioral triggers (time, mood, patterns) and delivers one personalized micro-intervention before a poor food choice happens, not after.

## What makes it different
- No calorie counting — ever
- Push-based, proactive nudges powered by Vertex AI (gemini-2.0-flash-001)
- Voice-first accessibility (WCAG 2.1 AA, ARIA live regions)
- Works offline (Service Worker + cached responses)
- Learns craving cycles from behavioral time-series data

## Google Services Used
- **Google Cloud Run**: Serverless container hosting for the NutriSense FastAPI backend and UI.
- **Google Cloud Firestore**: NoSQL document database used to store behavioral contexts, nudge history, user preferences, and feedback.
- **Google Cloud Logging**: Integrated structured logging for robust observability and error tracking.
- **Google Vertex AI (Gemini 2.0 Flash)**: Powers the contextual generation of empathetic, non-caloric behavioral nudges and performs food analysis.

## Architecture
```text
  User Device (Web/Voice)
           │
           ▼
  [Cloud Run: FastAPI] ────► [Google Cloud Logging]
           │
     ┌─────┴─────┐
     ▼           ▼
[Firestore]  [Vertex AI]
(Contexts,   (Gemini 2.0 Flash)
 History)
```

## Live Demo
**Web App URL**: [https://nutrisense-api-147518467528.us-central1.run.app](https://nutrisense-api-147518467528.us-central1.run.app)

**Test API Nudge**: 
```bash
curl -X POST https://nutrisense-api-147518467528.us-central1.run.app/nudge \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","context":{"time":"14:00","mood":"stressed"}}'
```

## API Reference
**Base URL:** `https://nutrisense-api-147518467528.us-central1.run.app`

### 1. Health Check
`GET /health`
```bash
curl -X GET https://nutrisense-api-147518467528.us-central1.run.app/health
```

### 2. Save Context
`POST /context`
```bash
curl -X POST https://nutrisense-api-147518467528.us-central1.run.app/context \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","time":"14:00","mood":"stressed","location_type":"work"}'
```

### 3. Generate Nudge
`POST /nudge`
```bash
curl -X POST https://nutrisense-api-147518467528.us-central1.run.app/nudge \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","context":{"time":"14:00","mood":"stressed","location_type":"work"}}'
```

### 4. Analyze Food
`POST /food/analyze`
```bash
curl -X POST https://nutrisense-api-147518467528.us-central1.run.app/food/analyze \
  -H "Content-Type: application/json" \
  -d '{"food_description":"A large blueberry muffin and sweet coffee"}'
```

### 5. Get Nudge History
`GET /history/{user_id}`
```bash
curl -X GET https://nutrisense-api-147518467528.us-central1.run.app/history/demo
```

### 6. Save Preferences
`POST /preferences`
```bash
curl -X POST https://nutrisense-api-147518467528.us-central1.run.app/preferences \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","preferences":{"diet":"vegetarian","tone":"gentle"}}'
```

### 7. Feedback
`POST /feedback`
```bash
curl -X POST https://nutrisense-api-147518467528.us-central1.run.app/feedback \
  -H "Content-Type: application/json" \
  -d '{"nudge_id":"SOME_DOC_ID","helpful":true}'
```

## Setup & Deployment
1. **Initialize Project:**
   ```bash
   gcloud projects create my-nutrisense-project
   gcloud config set project my-nutrisense-project
   ```
2. **Enable APIs:**
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com aiplatform.googleapis.com
   ```
3. **Initialize Firestore:**
   - Go to Google Cloud Console > Firestore > Create Database (Native mode).
4. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy nutrisense-api \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars=GCP_PROJECT_ID=my-nutrisense-project,ENVIRONMENT=production \
     --memory 512Mi --cpu 1
   ```
   *(Note: Set `VERTEX_AI_API_KEY` environment variable in the Cloud Run service to securely authenticate Gemini).*

## Accessibility Features
- **WCAG 2.1 AA Compliance:** High contrast UI, proper heading structures.
- **ARIA Live Regions:** Real-time nudge readouts via `aria-live="polite"` for screen readers.
- **Voice-First Input:** Dictation support for logging food and mood states.
