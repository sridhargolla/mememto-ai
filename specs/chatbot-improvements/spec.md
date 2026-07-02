# Specification: Chatbot Context-Aware Memory & Tone Personalization

- **Status**: Approved
- **Author**: Principal Engineer
- **Date**: 2026-07-02
- **Target Release**: v1.1.0

---

## 1. Objective & Context
Currently, the Memento AI chatbot retrieves document chunks and recent memory logs but does not rank them dynamically based on relevance, recency, and context importance. Additionally, the user experience can be improved by dynamically adjusting the chatbot's conversational tone (e.g., Professional, Casual, Formal) based on the user's input intent, and ensuring localized prompt templates.

---

## 2. Requirements

### Functional Requirements
1. **Context-Aware Retrieval**: The system must extract intent terms from the user query and prioritize memories in SQLite that match these terms, weighting recency (chronological order) and importance.
2. **Dynamic Tone Switching**: The personality engine must analyze the query for context markers (e.g., code requests, formal greetings, casual conversation) and switch its response style configuration dynamically.
3. **Multi-language Prompt Localization**: The prompt builder must detect the primary language of the conversation and load localized system templates (English, Hindi, Telugu).

### Non-Functional Requirements
- **100% Local Inference**: All parsing, classification, and retrieval must run on the local CPU, using llama.cpp and SQLite, without any network API calls.
- **Performance**: Dynamic context building must add less than 100ms latency to the prompt formulation pipeline.
- **Privacy-first**: No prompt, document chunk, or user data can leave the local environment.

---

## 3. Scope Boundaries

### In Scope
- Modifications to `prompt_builder.py` to support dynamic system prompt templates.
- Enhancements in `personality_engine.py` to support dynamic style routing.
- Context injection ranking logic in `smart_retrieval.py`.

### Out of Scope
- Upgrading the GGUF model binary or using GPU-based model execution.
- Modifications to the frontend UI layout.

---

## 4. User Journeys
1. The user asks a technical question in Hindi: "इस कोड को कैसे रन करें?"
2. The chatbot detects Hindi language, loads the Hindi greeting and response template.
3. The chatbot detects a programming intent, switches to a "Professional" tone, and retrieves relevant code-snippet memories.
4. The response is formatted with source attributions and presented to the user offline.
