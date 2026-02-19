# Prospera: AI-Powered Personal Finance Assistant 

Prospera is an intelligent financial agent designed to provide personalized insights, spending analysis, and goal tracking. It leverages **Google Gemini** for natural language understanding and implements the **Model Context Protocol (MCP)** to securely fetch simulated financial data from a mock banking server.

## Architecture

The project follows a decoupled, 3-tier architecture:

1.  **Frontend (React + Vite):** A modern dashboard and chat interface for users to interact with the AI and view data visualizations.
2.  **Backend (Python + FastAPI):** The core logic layer. It hosts the AI Agent (Gemini), manages user sessions, handles goal tracking, and acts as the **MCP Client** to fetch data.
3.  **MCP Server (Go):** A mock financial institution server. It serves "Ground Truth" data (Bank Transactions, Net Worth, Mutual Funds) via REST and SSE (Server-Sent Events).

---

## Key Features

* **💬 Natural Language Chat:** Ask questions like *"How much did I spend on food last month?"* or *"Analyze my investment portfolio."*.
* **📊 Dynamic Visualizations:** The AI generates on-the-fly charts for spending trends and category breakdowns.
* **🎯 Goal Management:** Create savings goals with AI-powered feasibility analysis and tracking.
* **⚡ Real-time Data Streaming:** Uses Server-Sent Events (SSE) for streaming financial data updates.
* **🔒 Model Context Protocol (MCP):** Standardized, secure data fetching pattern between the AI Agent and Financial Data.

---

## Tech Stack

* **Frontend:** React, TypeScript, Tailwind CSS, Vite, Google Charts.
* **Backend:** Python 3.8+, FastAPI, Google Generative AI (Gemini 1.5 Flash), HTTPX.
* **Data Server:** Go (Golang 1.23+).

---

## Getting Started

You will need three separate terminal windows to run the full stack.

### Prerequisites
* Node.js & npm
* Python 3.8+
* Go 1.23+
* A **Google Gemini API Key** (Required for the AI features).

### Step 1: Start the MCP Server (Financial Data Source)

This mock server provides the raw financial data.

1.  Navigate to the directory:
    ```bash
    cd fi-mcp-dev
    ```
2.  Run the server:
    ```bash
    go run .
    ```
    *Server will start on `http://localhost:8081`*.

### Step 2: Start the Backend (AI Agent)

1.  Navigate to the directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```
3.  Configure Environment:
    Create a `.env` file in the backend folder:
    ```ini
    GOOGLE_API_KEY=your_actual_gemini_api_key_here
    MCP_BASE_URL=http://localhost:8081
    GEMINI_MODEL=gemini-1.5-flash
    DEBUG=true
    ```
4.  Run the application:
    ```bash
    python main.py
    ```
    *Server will start on `http://localhost:8000`*.

### Step 3: Start the Frontend (User Interface)

1.  Navigate to the directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    *App will be available at `http://localhost:5000`*.

---

## How to Use (Demo Credentials)

Since the MCP server uses mock data files, you must log in using specific phone numbers that correspond to the data folders in `fi-mcp-dev/test_data_dir`.

1.  Open the Frontend in your browser (http://localhost:5000).
2.  **Login Screen:**
    * **Phone Number:** Use one of the following demo numbers:
        * `1010101010` (Precious Metal Investor)
        * `9999999999` (Fixed Income Investor)
        * `1313131313` (Balanced Growth Portfolio)
        * `2222222222` (High Net Worth / Sudden Wealth)
    * **Session ID:** You can use the same number as the phone number (e.g., `1010101010`).
3.  **Dashboard:** Once logged in, you will see the dashboard populated with data for that specific user profile.
4.  **Chat:** Go to the Chat tab and try these queries:
    * "What is my net worth?"
    * "Show me my spending trend for the last 6 months"
    * "How much have I invested in Mutual Funds?"
    * "Can I afford a vacation to Europe?"

---

## Project Structure

```text
Prospera/
├── backend/                 # Python FastAPI Server
│   ├── agent/               # AI Logic (Gemini integration, Prompts, Tools)
│   ├── api.py               # API Routes (Endpoints for Frontend)
│   ├── mcp_client.py        # Client to talk to Go Server
│   └── main.py              # Entry point
├── fi-mcp-dev/              # Go Data Server
│   ├── main.go              # Server entry point
│   ├── pkg/                 # Tool definitions and port config
│   └── test_data_dir/       # JSON Mock Data (Database of users)
└── frontend/                # React Application
    ├── src/
    │   ├── components/      # Chat, Dashboard, Auth, Charts
    │   └── services/        # API calls to Backend
    └── vite.config.ts       # Proxy configuration (Backend and MCP)
