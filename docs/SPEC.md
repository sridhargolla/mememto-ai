# Memento AI — Technical Specification

## 1. Introduction
**Memento AI** is a CPU-first, offline-first personal memory engine. It is designed to run entirely on local consumer hardware (e.g., standard laptops), transforming unstructured personal data—such as documents, images, audio recordings, and text notes—into a structured, semantic, and easily searchable personal knowledge graph. By executing all AI inference locally using quantized models, Memento AI ensures absolute data privacy, zero cloud subscription costs, and offline independence.

---

## 2. Problem Statement
In the modern digital landscape, individuals generate vast amounts of unstructured information across various formats (meeting notes, PDFs, voice memos, project reports). Currently, organizing and retrieving this information relies on:
1. **Manual Organization**: Time-consuming, rigid, and prone to search failures.
2. **Cloud-Based AI Services**: Solutions like OpenAI, Anthropic, or NotebookLM require uploading sensitive personal data to third-party servers, posing significant privacy risks, requiring constant internet connectivity, and incurring recurring API costs.
3. **GPU-Heavy Local AI**: Most open-source AI pipelines assume high-end GPU/CUDA availability, making them inaccessible to average users with standard laptops or office PCs.

---

## 3. Goals
- **100% Offline Execution**: All data ingestion, indexing, and querying must function without an active internet connection.
- **CPU-First Optimization**: The AI pipeline must be optimized for consumer-grade CPUs using highly efficient execution runtimes (like `llama.cpp` and `Whisper.cpp`) and quantized models.
- **Zero-Trust Privacy**: No user data, metadata, or queries may ever leave the local machine.
- **Structured Knowledge Extraction**: Convert raw, unstructured files into a standardized, relational JSON schema representing people, projects, skills, events, and knowledge.
- **Semantic Retrieval**: Support natural language querying over the extracted memory database.

---

## 4. Non-Goals
- **No Cloud Integration**: The system will not support or fallback to cloud AI APIs (e.g., OpenAI, Anthropic, Cohere).
- **No GPU Requirement**: The system must not require a dedicated GPU (NVIDIA CUDA or AMD ROCm) to run at usable speeds.
- **No Real-Time Streaming Ingestion**: Processing is batch-oriented upon user upload, rather than continuous background system-wide surveillance.
- **No Multi-User Collaboration**: Memento AI is designed as a single-user, local-only desktop application.

---

## 5. Functional Requirements
### Input Formats
- **Text**: `.txt`, `.md`, `.rtf`
- **Documents**: `.pdf` (digital and scanned), `.docx`
- **Images**: `.png`, `.jpg`, `.jpeg` (containing text or diagrams)
- **Audio**: `.mp3`, `.wav`, `.m4a`, `.ogg`

### Processing Pipeline
The ingestion pipeline follows a strict local unidirectional flow:

```
[ Raw Input File ]
       │
       ▼
[ Content Extraction ] (PyMuPDF / Tesseract OCR / Whisper.cpp)
       │
       ▼
[ Text Normalization ] (Clean whitespace, chunking, metadata extraction)
       │
       ▼
[ Local AI Inference ] (ONNX Embeddings & GGUF LLM Extraction)
       │
       ▼
[ Structured JSON ] (Normalized schema validation)
       │
       ▼
[ SQLite Database ] (Relational Storage & Vector Search)
```

---

## 6. AI Pipeline
### A. Document Processing & Extraction
- **Digital PDFs/Text**: Text is extracted using lightweight libraries (`PyMuPDF` or `pdfplumber`).
- **Scanned PDFs & Images**: Sent to a local OCR engine (`Tesseract OCR` or an ONNX-optimized OCR model) to extract raw text coordinates and strings.
- **Chunking**: Text is split using a recursive character text splitter into overlapping chunks (e.g., 512 tokens with 10% overlap) to preserve context for the embedding model.

### B. Speech Processing
- **Audio Decoding**: Incoming audio files are converted to 16kHz mono WAV format using a local `FFmpeg` wrapper.
- **Transcription**: The audio is processed by `Whisper.cpp` using a quantized model (e.g., `ggml-base.en-q5_1.bin`). This produces a timestamped text transcript.

### C. LLM Transformation & Entity Extraction
- **Local LLM Execution**: The normalized text or transcript is fed to `llama.cpp` via local Python bindings.
- **Structured Synthesis**: The LLM is prompted with strict system instructions and a few-shot JSON schema to extract entities, relationships, and attributes.
- **Self-Correction**: If the LLM output fails JSON validation, a lightweight parser attempts to repair it, or a second quick pass is run to correct the syntax.

---

## 7. Structured Data Schema
All extracted memories are classified and saved as JSON structures. Below are examples of the target schemas:

### Memory Type: `project`
```json
{
  "type": "project",
  "title": "Memento AI Offline Engine",
  "description": "A local, CPU-optimized personal knowledge base using GGUF LLMs and Whisper.cpp.",
  "status": "in-progress",
  "skills": [
    "Python",
    "FastAPI",
    "React",
    "llama.cpp",
    "Whisper.cpp",
    "SQLite"
  ],
  "collaborators": [
    "Member 1",
    "Member 2"
  ],
  "timeline": {
    "start_date": "2026-06-20",
    "end_date": null
  },
  "source": "memento_architecture_draft.pdf"
}
```

### Memory Type: `person`
```json
{
  "type": "person",
  "name": "Sridhar",
  "role": "Lead Architect & Developer",
  "organization": "Swecha",
  "associated_projects": [
    "Memento AI Offline Engine"
  ],
  "skills": [
    "C++",
    "Python",
    "System Design"
  ],
  "contact_meta": {
    "email": "sridhar@example.org"
  },
  "source": "meeting_notes_2026_06_28.txt"
}
```

---

## 8. Hardware Requirements

| Resource | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **CPU** | Intel Core i5 / AMD Ryzen 5 (4 Cores, AVX2 support) | Intel Core i7 / AMD Ryzen 7 / Apple Silicon M-series (8+ Cores) |
| **RAM** | 8 GB LPDDR4/DDR4 | 16 GB or 32 GB DDR5 / Unified Memory |
| **Storage** | 5 GB free SSD space (models + DB) | 15 GB free NVMe SSD space |
| **OS** | Windows 10/11, macOS 12+, Linux (Ubuntu 22.04+) | Windows 11, macOS Sonoma, Linux (Ubuntu 24.04+) |

---

## 9. AI Runtime & Model Architecture
The local AI stack is strictly composed of CPU-optimized libraries:

1. **Large Language Model (LLM)**:
   - **Runtime**: `llama.cpp` (via `llama-cpp-python` bindings).
   - **Model**: `Phi-3-mini-4k-instruct-q4.gguf` (3.8 Billion parameters, 4-bit quantization, ~2.2 GB size) or `Llama-3-8B-Instruct-Q4_K_M.gguf` (~4.8 GB size).
2. **Speech-to-Text (STT)**:
   - **Runtime**: `Whisper.cpp` (compiled with AVX2/CPU optimizations).
   - **Model**: `ggml-base.en-q5_1.bin` (~140 MB size).
3. **Text Embeddings**:
   - **Runtime**: `ONNX Runtime` (CPU execution provider).
   - **Model**: `all-MiniLM-L6-v2` (ONNX format, 384 dimensions, ~90 MB size) or `bge-small-en-v1.5` (ONNX format, ~130 MB size).
4. **OCR Engine**:
   - **Runtime**: `Tesseract OCR` (local binary) or `EasyOCR` running on CPU.

---

## 10. Security and Privacy
- **Data Localism**: All raw files, metadata, transcripts, and vector embeddings are stored in a single local directory (`~/.memento/`).
- **Network Isolation**: The application does not open any external network sockets (except for binding to `localhost` for the frontend-backend communication). It has no outbound internet request handlers.
- **Database Encryption (Optional)**: Support for `SQLCipher` to encrypt the SQLite database file (`memento.db`) at rest using a user-supplied master password.

---

## 11. Performance Goals
- **Initialization Time**: The application should boot and load the embedding model in `< 3 seconds`.
- **Text Chunk Embedding**: Embedding generation latency should be `< 50ms` per 256-word chunk.
- **LLM Generation Speed**:
  - Minimum: `5 tokens/second` on a standard 4-core CPU (8GB RAM).
  - Target: `12+ tokens/second` on an 8-core CPU (16GB RAM / Apple Silicon).
- **Audio Transcription Speed**:
  - Real-time factor of `< 0.5x` (e.g., a 10-minute audio file transcribed in under 5 minutes on a 4-core CPU using the `base` Whisper model).
