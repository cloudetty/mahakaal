# ⏳ Mahakaal: The Executive Agent

> *"Time flows. I await your command."*

## 📜 Project Overview
**Mahakaal** (Sanskrit: *Great Time* or *Master of Time*) is an advanced, agentic AI executive assistant designed to master the user's schedule. 

Unlike a standard chatbot, Mahakaal implements a **ReAct (Reason + Act)** architecture. It doesn't just "talk"; it "thinks," decides which tools to use, executes them, and observes the results before responding.

### 🎨 Visual Theme: "The Void"
The UI is designed to look like a futuristic command center.
- **Colors:** Void Black (`#050505`), Divine Gold (`#FFD700`), Terminal Green (`#00FF41`).
- **Vibe:** Minimalist, high-contrast, professional, and slightly mysterious.

---

## 🏗️ Architecture & Structure

The project is a monorepo split into two distinct parts: **The Brain** (Backend) and **The Face** (Frontend).

```text
mahakaal/
├── backend/                 # Python/FastAPI Agent Service
│   ├── .env                 # API Keys (OPENAI_API_KEY)
│   ├── events.json          # Simple file-based DB for calendar events
│   ├── main.py              # FastAPI entry point & streaming endpoint
│   ├── agent.py             # Core "ReAct" Loop (The Brain)
│   ├── skills.py            # Tool definitions (Calendar, Time) - MCP style
│   └── requirements.txt     # Python dependencies
│
└── frontend/                # React + Tailwind CSS UI
    ├── src/
    │   ├── App.tsx          # Main Chat Interface
    │   └── index.css        # Tailwind v4 Configuration
    ├── package.json         # Node dependencies
    └── vite.config.ts       # Build configuration
```

### 🧠 The Neural Architecture (Backend)
1.  **ReAct Loop (`agent.py`):**
    *   The agent receives a message history.
    *   It enters a loop: **Think → Call Tool → Observe Output → Repeat**.
    *   It streams these "thoughts" and "logs" back to the frontend so the user can see the AI working.
2.  **Skills (`skills.py`):**
    *   Functions that the AI can "call" (e.g., `schedule_event`, `get_current_datetime`).
    *   These are defined with JSON schemas that the LLM understands (similar to the **Model Context Protocol** pattern).
3.  **Persistence:**
    *   Currently uses `events.json` as a lightweight database.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- An OpenAI API Key

### 1. Setup The Brain (Backend)

```bash
cd mahakaal/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
# Create a .env file and add your key:
# OPENAI_API_KEY=sk-your-key-here
```

### 2. Setup The Face (Frontend)

```bash
cd mahakaal/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

### 3. Run The System
Ensure both terminals are running.
1.  **Backend:** Runs on `http://localhost:8000`
    ```bash
    # Inside mahakaal/backend
    python -m uvicorn main:app --reload
    ```
2.  **Frontend:** Runs on `http://localhost:5173`
    Open your browser to the local URL provided by Vite.

---

## 🧪 How to Test "Agentic" Behavior

Mahakaal is time-aware. Try these commands to see the **ReAct Loop** in the right-hand debug panel:

1.  **Relative Time Calculation:**
    > *"Schedule a meeting with Sarah for tomorrow at 2 PM."*
    *   **Observation:** The agent will first call `get_current_datetime` to figure out what date "tomorrow" is, *then* call `schedule_event`.

2.  **Conflict Checking:**
    > *"Am I free on January 15th?"*
    *   **Observation:** The agent calls `check_availability` and reads the JSON response.

---

## 🛠️ Tech Stack

*   **LLM:** OpenAI GPT-4o-mini (Configurable in `agent.py`)
*   **Backend:** FastAPI, Uvicorn, Pydantic
*   **Frontend:** React, TypeScript, Vite
*   **Styling:** Tailwind CSS v4

## 🔮 Future Roadmap

*   **True MCP Integration:** Move `skills.py` to a standalone MCP Server.
*   **Real Database:** Migrate `events.json` to SQLite or PostgreSQL.
*   **Voice Interface:** Add speech-to-text for a true "Iron Man" experience.
