# Memento AI - User Manual

## Overview

Memento AI is an offline, CPU-first AI assistant that helps users organize, search, and chat with information extracted from documents, images, audio, videos, and conversations.

The application works completely offline using local AI models powered by llama.cpp.

---

# Features

- AI Chat Assistant
- Document Upload
- OCR Support
- Audio & Video Transcription
- Memory Extraction
- Smart Search
- Timeline View
- Conversation History
- Offline AI
- CPU-only Inference
- Multi-language Support (English, Telugu, Hindi)

---

# Login

1. Open the application.
2. Enter your credentials.
3. Click **Login**.

If you do not have an account:

1. Click **Sign Up**.
2. Create a new account.
3. Login.

---

# Dashboard

The dashboard displays:

- Uploaded Documents
- Stored Memories
- Recent Conversations
- CPU Status
- Offline Status
- Performance Metrics

---

# Uploading Documents

Navigate to:

Documents → Upload

Supported formats:

- PDF
- DOCX
- TXT
- Images
- Audio
- Video

After upload, Memento AI automatically:

- Extracts text
- Generates memories
- Stores metadata
- Makes the content searchable

---

# Chat Assistant

Open **Chat**.

Ask questions naturally.

Examples:

- Summarize my resume
- Search my uploaded documents
- What projects have I worked on?
- Explain my research paper

The chatbot automatically searches your local memories before answering.

---

# Memories

The Memory section allows you to:

- View memories
- Search memories
- Filter memories
- Preview memory
- Download memory
- Delete memory

---

# Timeline

Displays uploaded documents and extracted memories in chronological order.

---

# Language Selection

Supported languages:

- English
- Telugu
- Hindi

Change language from:

Settings → Language

---

# Privacy

All processing happens locally.

No cloud APIs are used.

No internet connection is required.

No user data leaves the device.

---

# Troubleshooting

## AI Model Not Loaded

Ensure:

- GGUF model exists
- MODEL_PATH is correct
- llama.cpp is installed

---

## Upload Failed

Verify:

- File format is supported
- File size is within limit

---

## Chat Not Responding

Check:

- Backend is running
- Model is loaded
- SQLite database is accessible

---

# System Requirements

Windows 11

Intel i5 (or higher)

16 GB RAM recommended

CPU-only

No GPU required

---

# Support

Refer to:

README.md

CONTRIBUTING.md

SPEC.md

or open an issue in the repository.
