# Memento AI — Phase 2 MVP Offline Demo Guide

This document provides step-by-step instructions for evaluating the **Memento AI** Phase 2 MVP. This demo is designed to prove that the application performs text extraction, structured memory synthesis, and multi-turn semantic question answering **completely offline** on a standard CPU.

---

## 1. Prerequisites & Environment Setup

### Local Models
Before starting the demo, ensure the local models are downloaded and placed in the appropriate directory:
1. **GGUF LLM**: `Qwen2.5-3B-Instruct-Q4_K_M.gguf` (or `Phi-3-mini-4k-instruct-q4.gguf`) placed in `backend/models/model.gguf`
2. **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` cached locally in your Hugging Face cache (or loaded via local path).

---

## 2. Step-by-Step Demo Script

### Step 1: Disconnect from the Internet
1. Disable your Wi-Fi and disconnect any Ethernet cables.
2. Verify the offline status in your terminal:
   ```powershell
   ping google.com
   # Expected result: Ping request could not find host google.com.
   ```

### Step 2: Launch the Services
1. **Start Backend**:
   ```powershell
   cd backend
   .venv\Scripts\activate
   python main.py
   ```
   *Verify in the console logs that the GGUF model is loaded with `n_gpu_layers=0` (CPU-only).*

2. **Start Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`.

---

### Step 3: Verify the Offline & CPU Telemetry Panel
Look at the bottom of the **Dashboard**:
- 🟢 **AI Status**: `Local CPU Mode`
- 🖥️ **GPU Offloading**: `Disabled`
- 🛜 **Internet Connection**: `OFFLINE`
- 📡 **External Cloud API Calls**: `0`
- 🗄️ **Database**: `SQLite`

---

### Step 4: Upload Test Documents
Navigate to the **Documents** tab and upload:
1. `resume.pdf` (containing experience, e.g., *"Worked as a Machine Learning Intern at ABC Technologies in 2025, building an Image Classification System using Python and OpenCV."*)
2. `project.pdf` (containing details about an *"AI Attendance System using Python, OpenCV, and FastAPI."*)

*Observe the processing indicators in the UI. If a PDF has no digital text, the backend will automatically fall back to page-by-page Tesseract OCR.*

---

### Step 5: Inspect the Structured JSON Memories
Navigate to the **Memories** tab. Find the newly extracted memories and click **Show JSON**. Verify that the raw text has been transformed into a clean, structured JSON format:

```json
{
  "type": "experience",
  "title": "Machine Learning Internship",
  "organization": "ABC Technologies",
  "duration": "2025",
  "skills": [
    "Python",
    "OpenCV"
  ],
  "projects": [
    "Image Classification System"
  ],
  "source": "resume.pdf"
}
```

---

### Step 6: Query the Offline Memory Engine
Navigate to the **Chat** tab and ask:
> *"What projects have I worked on, and where did I do my internship?"*

---

### Step 7: Verify Multi-Turn Chat and Citations
The chatbot will respond using the local GGUF model:
> "You have worked on the following projects:
> 1. **Image Classification System** during your Machine Learning Internship at **ABC Technologies** in 2025 (Source: `resume.pdf`).
> 2. **AI Attendance System** using Python, OpenCV, and FastAPI (Source: `project.pdf`)."

#### Citation Verification:
- Click on the source citation pill `📄 resume.pdf` or `📄 project.pdf` below the message bubble. It will open a preview of the source document and highlight the relevant passage.

#### Performance Telemetry Verification:
- Look at the bottom of the assistant's chat bubble. It displays real-time CPU performance metrics:
  - ⏱️ **Inference Time**: `X.XX seconds`
  - ⚡ **Generation Speed**: `XX.X tokens/second`
  - 💾 **RAM Usage**: `XXXX MB`
  - 🤖 **Model**: `model.gguf`
  - 📡 **Network Calls**: `0`
