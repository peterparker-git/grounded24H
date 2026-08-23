# Grounded — Policy Answer Assistant

**Grounded** is an AI-powered policy question-answering assistant built for the Brite Spark 2026 hackathon. It is designed to help benefits office staff quickly and accurately answer questions based on a shifting policy manual.

Instead of guessing, the system grounds every answer in actual policy text, tracks historical amendments to ensure answers are accurate for a given date, and abstains when it lacks sufficient information.

## Key Features

- **Time-Aware Resolution:** Automatically determines which policy version applies based on a given determination or change-of-circumstance date.
- **Strict Grounding:** Retrieves relevant policy provisions using FAISS vector search and verifies exact clause citations.
- **Safety First:** If a required date is missing or the question is outside the policy manual, it abstains (`NEEDS_DATE` or `ABSTAIN`) rather than hallucinating.
- **Deterministic Fallback:** If the Gemini API is unavailable or hits a quota limit, the system gracefully falls back to a safe, deterministic response using resolved evidence.

## System Architecture

```text
User Question
      |
      v
FAISS Vector Search
      |
      v
Policy Resolver
      |
      +---- Missing Date? ----> NEEDS_DATE
      |
      v
Confidence Check
      |
      +---- Low Relevance? --> ABSTAIN
      |
      v
Answer Generation
      |
      +---- Gemini available ------> Gemini
      |
      +---- Gemini quota/error ----> Deterministic Fallback
                                      |
                                      v
                              Grounded Response
                                      |
                                      v
                              Citation Verification
                                      |
                                      v
                         Answer + Exact Policy Clause
```

## Example Usage

The assistant adapts its answers based on the timeline of policy amendments.

**Question:** *What is the monthly income threshold for a household of 3?*
- **With date `2026-04-25`:** "$2,075" *(Source: Amendment No. 2026-01)*
- **With date `2026-02-15`:** "$2,000" *(Source: Original Policy Manual)*
- **Without a date:** The system asks the user to provide a determination date.

**Question:** *What medication should I take for a headache?*
- **Result:** `ABSTAIN` (The system stays strictly within the supplied knowledge base).

## Project Structure

```text
grounded/
├── data/                  # Synthetic policy data, provisions, and FAISS index
├── src/
│   ├── assistant.py       # Main orchestration logic
│   ├── policy_engine.py   # Resolves policy versions & amendments
│   ├── retriever.py       # FAISS vector search 
│   ├── generator.py       # Gemini API answer generation
│   ├── fallback.py        # Deterministic fallback logic
│   └── models.py          # Data models
├── tests/                 # Unit tests (pytest)
├── eval/                  # Evaluation suite
├── README.md
├── DECISION.md            # Architecture & design decisions
├── AI-USAGE.md            # AI tools used during development
├── app.py                 # Streamlit UI frontend
└── conftest.py            # Pytest configuration
```

## Setup & Execution

### 1. Installation
Clone the repository and install dependencies in a virtual environment:
```bash
git clone https://github.com/hariharasudan/grounded.git
cd grounded

# Create virtual environment (use python3 on macOS/Linux, python on Windows)
python -m venv .venv

# Activate on macOS/Linux:
source .venv/bin/activate
# Activate on Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory and add your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Running the App
You can test the core assistant via CLI or run the interactive Streamlit UI:
```bash
# Run the interactive UI
streamlit run app.py

# Or test core components via CLI
python src/assistant.py
```

## Testing & Evaluation

The project includes a robust test and evaluation suite covering current policy, historical policy, missing dates, and unsupported questions.

```bash
# Run unit tests (19 passing)
python -m pytest tests/

# Run the evaluation suite (8/8 passing)
python eval/run_eval.py
```

## Limitations & Future Work

- **Prototype Scope:** This is a hackathon prototype using synthetic data. It is not an official legal/benefits determination tool.
- **Future Improvements:** 
  1. Move from chunk-based text extraction to structured policy extraction.
  2. Expand the evaluation set for broader policy coverage.
  3. Implement authentication and audit logging for public-sector use.
  4. API reliability and key management