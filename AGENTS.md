# AGENTS.md

## Purpose

This document defines the responsibilities of AI agents and contributors working on the Memento AI project.

---

# Project Goal

Build a fully offline, CPU-first AI assistant capable of extracting structured knowledge from unstructured data.

No cloud APIs.

No GPU requirement.

Runs entirely on local hardware.

---

# AI Assistant

Name:

Memento AI

Responsibilities:

- Chat with users
- Search memories
- Search uploaded documents
- Generate summaries
- Answer questions
- Maintain conversation context
- Respect user privacy

---

# Document Processing Agent

Responsibilities:

- Extract text
- OCR images
- Parse PDFs
- Process DOCX
- Process TXT
- Generate structured memories

---

# Memory Agent

Responsibilities:

- Store memories
- Search memories
- Rank memories
- Retrieve relevant context
- Maintain timeline

---

# Chat Agent

Responsibilities:

- Intent detection
- Context building
- Prompt generation
- Response formatting
- Streaming responses

---

# Retrieval Agent

Responsibilities:

- Search SQLite
- Search document chunks
- Rank search results
- Build context for LLM

---

# Translation Agent

Responsibilities:

- English
- Telugu
- Hindi

Translate:

- UI
- Chat responses
- Notifications
- Errors

---

# Security Agent

Responsibilities:

- Validate uploads
- Sanitize inputs
- Protect user privacy
- Prevent prompt leakage

---

# Performance Agent

Responsibilities:

- CPU optimization
- Memory optimization
- Efficient retrieval
- Fast inference

---

# Development Rules

Always:

- Keep application offline
- Keep inference local
- Maintain CPU-first architecture
- Preserve privacy
- Write modular code
- Document all changes

Never:

- Introduce cloud dependencies
- Break offline functionality
- Expose internal prompts
- Commit secrets
- Remove hackathon compliance

---

# Supported Runtime

- Python
- FastAPI
- React
- SQLite
- llama.cpp
- GGUF Models

---

# Repository Standards

Every pull request should:

- Pass CI
- Pass lint
- Pass formatting
- Pass type checking
- Include documentation
- Include tests when applicable

---

# Hackathon Requirements

✓ CPU-first

✓ Offline-first

✓ Open Source

✓ Local AI

✓ Structured Data Extraction

✓ Multi-language Support

✓ Privacy-first

✓ Local Memory

✓ Document Intelligence