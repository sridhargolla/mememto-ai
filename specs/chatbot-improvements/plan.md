# Implementation Plan: Chatbot Context-Aware Memory & Tone Personalization

- **Spec**: [specs/chatbot-improvements/spec.md](spec.md)
- **Author**: Principal Engineer
- **Date**: 2026-07-02
- **Status**: Approved

---

## 1. Technical Goal
The goal of this implementation is to enhance Memento AI's backend retrieval capabilities and tone responsiveness without altering external API routing or storage schemas. We will introduce weight factors for memory ranking in retrieval and dynamic configuration hooks in the personality engine.

---

## 2. Proposed Changes

### Component: Backend

#### [MODIFY] [smart_retrieval.py](file:///c:/Users/sriva/CascadeProjects/memento-ai/backend/smart_retrieval.py)
- Update `retrieve_with_ranking` to calculate a dynamic score combining semantic similarity, document chunk importance, and a recency decay factor:
  $$\text{Score} = w_s \times \text{Similarity} + w_r \times (1 - \text{Decay}) + w_i \times \text{Importance}$$

#### [MODIFY] [personality_engine.py](file:///c:/Users/sriva/CascadeProjects/memento-ai/backend/personality_engine.py)
- Modify `get_response_style` to analyze the query text for intent keywords (like "code", "explain", "hey") and set the target tone dynamically.

#### [MODIFY] [prompt_builder.py](file:///c:/Users/sriva/CascadeProjects/memento-ai/backend/prompt_builder.py)
- Integrate dynamic language checking using `detect_language` from `language_service.py` to localize system prompts automatically on each query.

---

## 3. Database & Schema Changes
No schema changes. Existing tables `memories`, `conversations`, and `documents` will be used as-is.

---

## 4. API Endpoints
No API signature changes. The `/chat` endpoint will transparently benefit from the improved context compilation.

---

## 5. Verification Plan

### Automated Tests
- Run `pytest backend/tests/test_memory_extractor.py`
- Run `pytest backend/tests/test_integration_memory_extraction.py`

### Manual Verification
- Deploy backend locally, send chat queries in English and Hindi, and verify the console log output for selected tone styles.
