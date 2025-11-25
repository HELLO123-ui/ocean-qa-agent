# Autonomous QA Agent – Ocean AI Assignment

This project implements an **Autonomous QA Agent** that can:

1. Ingest project documentation (product specs, UI/UX guidelines, mock APIs, etc.) and the HTML of a target web page (`checkout.html`).
2. Build a **vector-based knowledge base** grounded only in those documents.
3. Generate **documentation-grounded test cases**.
4. Convert a selected test case into a **runnable Selenium WebDriver (Python) script**.

The system uses:

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Vector DB:** ChromaDB
- **Embeddings:** Sentence Transformers
- **LLM Provider:** Groq (LLaMA 3)
- **Automation Output:** Selenium (Python)

---

## 1. Tech Stack

- **Language:** Python 3.11
- **Backend:** FastAPI (`backend/main.py`)
- **Frontend:** Streamlit (`frontend/app.py`)
- **RAG Components:** ChromaDB + Sentence Transformers
- **LLM Client:** Groq API (`backend/llm_client.py`)
- **Automation:** Selenium WebDriver (Chrome)

---

## 2. Project Structure

```text
ocean-qa-agent/
├── assets/
│   ├── checkout.html           # Target E-Shop Checkout page
│   ├── product_specs.md        # Feature / business rules
│   ├── ui_ux_guide.txt         # UI & UX rules
│   ├── api_endpoints.json      # (Optional) Mock API endpoints
│   └── ...                     # Any other support docs
├── backend/
│   ├── __init__.py
│   ├── ingestion.py            # Parsing, chunking, vector DB ingestion
│   ├── rag.py                  # Retrieval from ChromaDB
│   ├── models.py               # Pydantic models (TestCase, etc.)
│   ├── llm_client.py           # Groq LLM wrapper (test cases & scripts)
│   └── main.py                 # FastAPI app entrypoint
├── chroma_db/                  # Local Chroma vector store (created at runtime)
├── frontend/
│   └── app.py                  # Streamlit UI
├── .env                        # (not committed) API keys, config
├── .gitignore                  # Excludes venv, chroma_db, cache, etc.
├── requirements.txt
└── README.md

Setup Instructions

Python version: 3.11

git clone https://github.com/HELLO123-ui/ocean-qa-agent.git
cd ocean-qa-agent

python3.11 -m venv venv
source venv/bin/activate        # macOS / Linux
# .\venv\Scripts\activate       # Windows

pip install -r requirements.txt

Environment variables (Groq)

Create .env in the project root:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

Backend (FastAPI)
cd ocean-qa-agent
source venv/bin/activate

uvicorn backend.main:app --reload --port 8000


Check: http://127.0.0.1:8000 → should return:

{"message": "QA Agent backend is running"}

Frontend (Streamlit)

In another terminal:

cd ocean-qa-agent
source venv/bin/activate

streamlit run frontend/app.py

Usage Workflow
Step 1 – Upload & Build Knowledge Base

In the Streamlit UI:

Upload support documents (left side):

assets/product_specs.md

assets/ui_ux_guide.txt

assets/api_endpoints.json

(any extra .md/.txt/.json/.pdf docs)

Upload assets/checkout.html (right side).

Click “Build Knowledge Base”.

Under the hood:

ingestion.py parses files, chunks text, creates embeddings.

Chunks are stored in ChromaDB at ./chroma_db.

checkout.html is stored and later used for DOM-aware prompts.

Step 2 – Generate Documentation-Grounded Test Cases

In section “2️Generate Documentation-Grounded Test Cases”, type a prompt, e.g.:

Generate all positive and negative test cases for the discount code feature.


Click “ Generate Test Cases”.

The app:

Uses rag.py to retrieve the most relevant chunks from ChromaDB.

Calls Groq via llm_client.py to create structured test cases (JSON).

Displays them in a table and counts them in the sidebar.

Each test case includes:

test_id, feature/scenario

preconditions, steps

expected_result

grounded_in (which support docs were used)

Step 3 – Generate Selenium Script

In “3️Generate Selenium Test Script”, select a test case (e.g. TC-001 — Apply a valid discount code SAVE15).

Expand “Selected Test Case (detailed)” to inspect JSON.

Click “ Generate Selenium Script”.

The backend:

Sends the selected test case + checkout.html + context to Groq.

LLM returns a complete Python function using Selenium WebDriver (Chrome):

Opens local checkout.html.

Performs steps (enter discount code, click Apply, etc.).

Asserts the expected outcome (e.g., 15% discount applied, total updated).

You can copy this code directly into a test file and run it (after configuring Selenium/ChromeDriver).

5. Explanation of Support Documents

All reasoning is grounded in these assets in assets/:

5.1. checkout.html

A realistic E-Shop Checkout page with:

Items and quantities

Cart subtotal

Discount code field + “Apply” button

Name, Email, Address fields

Shipping method radios (Standard/Express)

Payment method radios

“Pay Now” button that shows “Payment Successful!” on valid submission

Used for:

Locators in Selenium (IDs/names/CSS)

Ensuring scripts only use real elements (no hallucinated fields)

5.2. product_specs.md

Contains business rules, e.g.:

How discount codes (e.g. SAVE15) work

Shipping costs, totals, constraints

Drives:

Positive, negative, and boundary test cases

Correct expected results in tests

ui_ux_guide.txt

Contains UI/UX rules, e.g.:

Inline error messages

Colours (red errors, green success)

Button states & layout hints

Drives:

Validation testing (required fields, error text)

Tests that check user-facing behaviour, not just logic

5.4. api_endpoints.json (optional)

Simple JSON schema of checkout-related APIs (e.g. /apply_coupon, /submit_order).

Gives the agent more context for what’s happening server-side.

Helps inspire end-to-end test ideas (UI + API consistency).

You may optionally add more .md/.txt/.json/.pdf docs; they will automatically be ingested and used in the RAG pipeline.

Example Prompts:

Generate all positive, negative, and edge test cases for applying discount codes on the checkout page, including SAVE15.


