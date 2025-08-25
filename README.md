# 🌍 Travel & Weather Assistant

The **Travel & Weather Assistant** is a conversational web app that provides travel recommendations, weather updates, and activity suggestions in a chat-like interface.

Currently built with **Streamlit (frontend)** and a **FastAPI + LangGraph backend**, the app integrates AI agents, external APIs, and web scraping to deliver intelligent, context-aware responses.

---

## ✨ Features (Current)

* **Conversational Interface** – Chat-like user experience.
* **Travel & Activity Recommendations** – AI-powered suggestions.
* **Weather Updates** – Real-time weather for any location.
* **Session Management** – Unique sessions with preserved history.
* **Dynamic Chat History** – Smooth, interactive conversations.

---

## 🏗️ How It Works

1. **User Interaction**

   * Queries entered in a chat box.
   * Example:

     * “What’s the weather in Paris?”
     * “Suggest activities for a weekend in New York.”

2. **Backend Processing**

   * Streamlit frontend sends queries + chat history → FastAPI backend.
   * Backend orchestrates AI workflows using **LangGraph + LangChain**.
   * External APIs + scraping (BeautifulSoup) enrich responses.

3. **Response Display**

   * Streamlit updates chat history dynamically.

---

## 🛠️ Tech Stack (Current)

### Frontend

* **Streamlit** – UI, session management

### Backend

* **FastAPI** – Backend framework (async APIs & AI services)
* **LangGraph** – Agent workflows (stateful AI orchestration)
* **LangChain-Core / LangChain-Google-GenAI** – LLM integration
* **Uvicorn** – ASGI server
* **Pydantic** – Data validation
* **BeautifulSoup4** – Web scraping (weather & travel data)
* **Loguru** – Structured logging

---

## 🚀 Installation

### Prerequisites

* Python 3.9+
* Pip
* Docker

### Setup

```bash
git clone https://github.com/your-username/weather-agent.git
cd weather-agent
```

Run with Docker:

```bash
make up
```
or

```bash
docker compose up -d
```

Then Open : [Frontend](http://localhost:8501/)

View logs:

```bash
make logs
```

Stop services:

```bash
make down
```

---

## ⚙️ Configuration

Create a `.env` file from .env.examples and fill:

```
GOOGLE_API_KEY=your_key_here   (from google AI studio - Free)
LANGSMITH_API_KEY=optional_debug_key  
```

---

## 📂 Codebase

```
weather-agent/
├── app/
│   ├── frontend/        # Streamlit app
│   ├── backend/         # FastAPI + LangGraph agents
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 🔮 Planned Improvements & Scaling

This prototype is designed for easy scaling into a **production-ready architecture**. Future enhancements include:

### 🔧 Improvements

* **Frontend Scaling**

  * Migrate to **Next.js** for performance and flexibility.
  * Add authentication with **NextAuth** (OAuth/OpenID providers such as Google, GitHub, AWS Cognito).

* **Backend Enhancements**

  * Expand **FastAPI agents** for real-time AI services.
  * Add **Redis caching** for weather scrapers, FastAPI responses, and LLM queries.

* **Database Integration**

  * Store sessions, chat history, user profiles, and business-related data (e.g., activities).

---

### 🏗️ Target Architecture

```
┌────────────────────┐        ┌───────────────────────┐
│   Next.js Frontend │ <----> │ FastAPI + LangGraph   │
│ (UI + Business     │        │ AI Agents             │
│  Logic)            │        │ (Python async APIs)   │
└─────────┬──────────┘        └─────────────┬─────────┘
          │                                  │
 ┌────────▼─────────┐              ┌─────────▼─────────┐
 │ Authentication   │              │ Redis Cache       │
 │ (NextAuth +      │              │ - Weather scraper │
 │ OAuth Providers) │              │ - API responses   │
 └────────┬─────────┘              │ - LLM caching     │
          │                        └─────────┬─────────┘
 ┌────────▼─────────┐              ┌─────────▼─────────┐
 │ Database (SQL/NoSQL)            │ External APIs     │
 │ - Sessions                      │ - Weather API     │
 │ - User Data                     │ - Travel Data     │
 │ - Chat History                  │ - Maps / Places   │
 └───────────────────┘              └───────────────────┘
```

---

### 🛠️ Tech Stack (Planned)

**Frontend**

* Next.js (React-based frontend)
* NextAuth (OAuth / AWS Cognito / Google, etc.)
* TailwindCSS (UI styling)

**Backend**

* FastAPI (Python async API)
* LangGraph (agent workflows)
* LangChain-Core, LangChain-Google-GenAI (LLM integration)
* Redis (caching for weather, API, and LLM queries)
* Pydantic (data models & validation)
* Loguru (logging)

**Database**

* PostgreSQL / MySQL / MongoDB (user & session persistence)

**Caching**

* Redis

**Infrastructure**

* Docker & Docker Compose
* Cloud deployment (AWS / GCP / Azure)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 👥 Contributors

* [Hamza AIT BAALI](https://github.com/your-username)

