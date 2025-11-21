# InboxAI – AI Email Assistant (Devolopment Stage)

InboxAI is a full‑stack AI‑powered Gmail assistant that reads, organizes, summarizes, searches, and answers questions about your email inbox using **Gemini 1.5 Flash**, **Google Text Embeddings**, **ChromaDB**, **FastAPI**, and a **React frontend**.

This README includes:

- Complete installation guide
- Backend setup (FastAPI + Gmail OAuth2 + Gemini + ChromaDB)
- Frontend setup
- Running the system locally
- API endpoints
- Project folder structure
- Sync pipeline + RAG overview
- Troubleshooting

---

# Features:

###  Google OAuth 2.0 Login

- Connect your Gmail securely
- Uses `Authorization Code` flow
- No password ever stored

###  Email Sync Pipeline

- Full sync: fetch all Gmail messages
- Incremental sync using `historyId`
- Parses email MIME → clean text
- Stores embeddings in ChromaDB

### AI Chat (RAG)

- Ask: *“What did John say about the Q3 report?”*
- Retrieves top 5 relevant email chunks
- Uses Gemini 1.5 Flash for answers

### Send Email

- Compose email via InboxAI

### Highlights

- Important email summaries

### 🖥️React Frontend

- Login with Google
- View summaries
- Chat with your inbox
- Run manual sync

---

# Project Folder Structure

```
server/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── gmail_test.py
│   │   ├── sync.py
│   │   ├── chat.py
│   │   └── highlights.py
│   ├── core/
│   │   ├── auth.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── services/
│   │   ├── gmail_service.py
│   │   ├── chroma_store.py
│   │   └── rag_pipeline.py
│   ├── models/
│   │   ├── domain.py
│   │   └── api.py
│   └── utils/
│       └── text_processing.py
│
├── storage/
│   ├── tokens.json
│   ├── sync_state.json
│   └── chroma_db/
│
├── .env
├── Dockerfile
└── requirements.txt

frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── api/
│   └── App.jsx
├── package.json
└── vite.config.js
```

---

# Backend Setup (FastAPI + Uvicorn)

## 1️⃣ Install Python

Use Python **3.10+**

Check:

```
python --version
```

---

## 2️⃣ Create Virtual Environment

```
cd server
python -m venv myenv
myenv\Scripts\activate   # Windows
source myenv/bin/activate # macOS/Linux
```

---

## 3️⃣ Install Backend Dependencies

```
pip install -r requirements.txt
```

### requirements.txt should include:

```
fastapi
uvicorn
loguru
google-api-python-client
google-auth
google-auth-oauthlib
langchain
langchain-community
langchain-google-genai
chromadb
pydantic-settings
```

---

## 4️⃣ Setup `.env` file

Create `server/.env` with:

```
# Google OAuth
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback

# Gemini
GOOGLE_API_KEY=AIza...

# Other
APP_ENV=development
```

⚠️ Make sure the redirect URI matches exactly in Google Cloud.

---

## 5️⃣ Enable Gmail API

Go to: [https://console.cloud.google.com/apis/library/gmail.googleapis.com](https://console.cloud.google.com/apis/library/gmail.googleapis.com)

Enable API → Select your OAuth project.

---

## 6️⃣ Start FastAPI Server

```
cd server
uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

---

# Google OAuth Flow

### 1. User hits `/api/v1/auth/login`

Backend returns Google login URL.

### 2. User logs in & accepts Gmail permissions.

### 3. Google redirects to `/api/v1/auth/callback`

Backend exchanges auth code → access token + refresh token.

### 4. Tokens saved to:

```
storage/tokens.json
```

### 5. `/api/v1/auth/status` returns:

```
{ "is_authenticated": true }
```

---

# Gmail Service Testing APIs:

### 1. Get Gmail Profile

GET:

```
/api/v1/gmail/profile
```

### 2. List recent emails

```
/api/v1/gmail/list?max_results=10
```

### 3. Get full details of email

```
/api/v1/gmail/details/{message_id}
```

### 4. Send email

```
POST /api/v1/gmail/send?to=abc@gmail.com&subject=Hello&body=Test
```



# Email Sync Pipeline:

### Full Sync

- Fetch all messages
- Parse MIME → text + HTML
- Convert to `EmailDocument`
- Embed using Google Text Embedding 004
- Upsert into ChromaDB

### Incremental Sync

- Check `sync_state.json` for `last_history_id`
- Fetch only updated emails
- Store new vectors

Sync trigger endpoint:

```
POST /api/v1/sync
```

---

# RAG Pipeline (Gemini)

### 1. Query → embed

### 2. Retrieve top 5 email chunks

### 3. Construct prompt

### 4. Gemini 1.5 Flash answers

Endpoint:

```
POST /api/v1/chat
```

Body:

```json
{
  "query": "What did John say about the meeting?"
}
```

---

# Frontend Setup (React)

## 1️⃣ Install Node

Use Node **18+**

Check:

```
node -v
```

---

## 2️⃣ Install Dependencies

```
cd frontend
npm install
```

---

## 3️⃣ Environment Variables

Create `frontend/.env`:

```
VITE_SERVER_URL=http://localhost:8000
```

---

## 4️⃣ Start Frontend

```
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

# Testing the System

### 1. Start backend → login → connect Gmail

### 2. Run profile test

### 3. Run list email test

### 4. Run sync

### 5. Query RAG

### 6. View results on UI

---

# Production Deployment

### Backend

Use Dockerfile:

```
docker build -t inboxai-backend .
docker run -p 8000:8000 inboxai-backend
```

### Frontend

```
npm run build
```

Deploy to Vercel/Netlify.

### Environment variables managed by:

- Render
- Railway
- GCP Cloud Run

#

