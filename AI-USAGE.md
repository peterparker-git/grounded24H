# AI-USAGE.md

# AI Usage Disclosure

I used AI tools during the development of this project. I am documenting them here because the Brite Spark rules require AI usage to be disclosed.

I also understand that I am responsible for the final code and should be able to explain how the submitted system works.

## Tools I used

### Claude

I initially used Claude to work on the system design.

I used it mainly to think through the overall architecture and how the different parts of the RAG pipeline should be separated.

The design was then adapted while implementing and testing the actual project.

### ChatGPT

I used ChatGPT mainly for reasoning, planning, debugging, explaining implementation decisions, and working through problems during development.

This included discussing:

- RAG architecture
- policy retrieval and resolution
- handling changing policy versions
- confidence and abstention behavior
- testing strategy
- Gemini quota problems
- fallback behavior
- documentation and release preparation

### Gemini / Antigravity coding assistance

I used Gemini through my coding environment to help implement parts of the project.

This included:

- creating and modifying code
- implementing functions
- debugging errors
- writing and updating tests
- handling API integration
- implementing the deterministic fallback
- making changes based on test results

I reviewed the generated changes and ran the project and tests rather than treating generated code as automatically correct.

## Gemini API usage in the application

Gemini is also part of the actual application.

It is used for:

1. Generating embeddings for policy retrieval.
2. Generating plain-language answers from resolved policy evidence.

The application does not send the user's question to Gemini as an unrestricted general-purpose question. The answer-generation stage receives the policy evidence selected by the retrieval and policy-resolution pipeline.

## Why a fallback was added

During development, the Gemini free-tier request quota was reached.

This exposed an important practical problem: the application should not become unusable simply because the answer-generation API is temporarily unavailable.

I therefore added a deterministic fallback for supported policy answer patterns.

The fallback uses the policy evidence already retrieved by the system. It does not use another LLM, external search, or general knowledge.

If the evidence cannot safely support a fallback answer, the system does not invent one.

## AI-generated code and review

AI assistance was used throughout development, but the final repository was tested and reviewed by me.

I ran the project's automated tests and policy evaluation while developing it.

Some AI-generated changes also caused issues that had to be corrected during development, including:

- citation extraction behavior
- policy resolution test setup
- Gemini quota handling
- unsupported-question handling
- fallback behavior

This was part of the development process rather than simply accepting generated code without testing.

## Human responsibility

I am responsible for the submitted implementation.

I understand the main flow of the application:

```text
Question
   ↓
Retrieval
   ↓
Policy Resolution
   ↓
Confidence Check
   ↓
Answer Generation / Fallback
   ↓
Citation Verification
   ↓
Response
```

I can explain the purpose of each stage and the main decisions behind the architecture.

## Secrets and API keys

No real API key is included in the repository.

The Gemini API key is supplied through an environment variable:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The `.env` file is excluded from Git.

Only `.env.example` is included as a template.

## Final note

AI tools were part of my development workflow, but the goal was not to hide that usage.

I used them as development and reasoning tools, then tested and adapted the implementation to meet the actual problem requirements.
