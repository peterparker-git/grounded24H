# DECISION.md

# Project Decisions

This document records the core decisions, technology choices, and trade-offs I made while building Grounded for the Brite Spark 2026 hackathon.

## 1. Why I Chose This Problem

I chose **The Grounded Answer** because I liked the combination of RAG, policy reasoning, and reliability. The interesting challenge was not just making a chatbot answer a question, but handling a policy that changes over time. The system needs to determine which version of a rule applies, and critically, it needs to be willing to say "I don't know."

## 2. The Golden Principle

The main design principle I followed was:
> *If the system cannot support an answer from the policy evidence, it should not pretend that it can.*

For this problem, being strictly grounded and honest is far more important than answering every single question.

## 3. System Architecture & Data Flow

I kept the architecture modular with clear stages, ensuring day-two change readiness. If requirements change, I can update a specific stage without rewriting the whole application.

### Phase 1: Data Ingestion Pipeline (Missing from earlier drafts)
Before answering questions, the system processes raw policy data:
1. **Parsing & Structuring:** `ingest.py` reads the markdown and structures it using Pydantic-style classes in `models.py`.
2. **Embedding:** `embeddings.py` converts the text into vector representations.
3. **Indexing:** `index.py` stores the vectors into a local FAISS index.

### Phase 2: Inference Workflow
The query execution flows through distinct stages:
```text
Retrieval (FAISS Vector Search) 
   ↓
Policy Resolution (Filters out outdated amendments based on date) 
   ↓
Confidence Check (Rejects low-relevance queries)
   ↓
Answer Generation (Gemini) 
   ↓
Citation Verification (Ensures exact clauses are referenced)
```

## 4. Why Policy Resolution is Separate from Retrieval

Retrieval tells me which provisions are relevant, but it does not automatically tell me which provision is *applicable*. For example, an income threshold changed on `2026-03-01`. By separating resolution, the system checks the determination date (e.g., `2026-02-15` vs `2026-04-25`) and applies the correct rule instead of just returning the highest-scoring text. If no date is provided, it asks for one.

## 5. Confidence, Citations, and Abstention

I did not want the assistant to guess just because the retriever found something vaguely similar. 
- **Confidence Check:** If the retrieved evidence is not relevant enough, the system strictly abstains.
- **Citation Verification:** An answer is not complete just because it sounds plausible. The system checks the generated response against the retrieved evidence so the user can see the exact supporting clause.

## 6. Handling API Limits (The Deterministic Fallback)

During development, I reached the Gemini free-tier request limit. Instead of letting the application crash, I built a deterministic fallback (`fallback.py`). If Gemini is unavailable, the system outputs the raw, resolved policy evidence directly. It does not call another AI service and does not use outside knowledge, keeping the demo highly reliable.

## 7. Technology Choices

- **Python:** Chosen for its straightforward RAG, vector, and testing libraries.
- **Gemini:** Used for text embeddings and natural-language generation.
- **FAISS:** The policy manual is small enough that a local FAISS index is practical. It gives direct control over the evidence without the overhead of an external vector database.
- **Streamlit:** I prioritized backend logic over UI polish for this problem. Streamlit allowed me to quickly build a functional, interactive interface (`app.py`) while keeping the setup clean.
- **Pytest:** Focused testing on high-risk areas (citations, resolution, dates, fallback), resulting in 19 passing unit tests and an 8/8 evaluation score.

## 8. What the System Does NOT Do

The system does not:
- Answer questions outside the supplied knowledge base.
- Replace an official caseworker or policy decision.
- Guarantee that every possible natural-language question can be answered.
- Use general internet knowledge to fill gaps in the policy.
- Provide legal advice.

## 9. Trade-offs: What I Rejected and Cut for Time

Because this was a short individual hackathon, I avoided over-engineering.

**What I rejected:**
- Complex multi-agent architectures or large backend frameworks.
- Multiple external AI providers or cloud vector databases.
- Heavy frontend frameworks (e.g., React/Next.js).

**What I cut for time (Future Improvements):**
1. Structured extraction of complex policy tables (currently relies on text chunks).
2. Expanded evaluation sets for broader policy question types.
3. Expanded deterministic fallback coverage.
4. Production-grade authentication, user management, and audit logging.
5. Better monitoring and logging around retrieval failures.

I chose to build a smaller system where the critical behaviors work flawlessly, rather than a massive system with unfinished parts.
