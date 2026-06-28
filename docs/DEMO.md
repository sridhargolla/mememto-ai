# Memento AI — Hackathon MVP Demo Plan

This document outlines the step-by-step demonstration script for the **CPU-First Hackathon** evaluation. The goal of this demo is to prove that Memento AI performs advanced document processing, audio transcription, and semantic query answering **completely offline** on a standard CPU.

---

## Demo Overview
- **Goal**: Ingest unstructured files, extract structured knowledge, and answer queries while the machine is completely disconnected from the internet.
- **Hardware Used**: Standard consumer laptop (e.g., Intel Core i5/i7 or Apple M1/M2, 8GB-16GB RAM).
- **Network Status**: Air-gapped (WiFi and Ethernet disabled).

---

## Step-by-Step Demonstration Script

### Step 1: Disconnect the Internet
1. Open the system network settings.
2. **Disable WiFi** and disconnect any Ethernet cables.
3. Open a terminal and run a ping test to confirm the offline state:
   ```powershell
   ping google.com
   # Expected Output: Ping request could not find host google.com. Please check the name and try again.
   ```

### Step 2: Launch the Application
1. Start the local backend server from the workspace root:
   ```powershell
   cd backend
   .venv\Scripts\activate   # (or source .venv/bin/activate on Linux/macOS)
   python main.py
   ```
   *Note: Watch the console logs confirm that `llama.cpp` and `ONNX Runtime` are loading models from the local `./models/` directory.*

2. Start the local frontend development server:
   ```powershell
   cd frontend
   npm run dev
   ```
3. Open a browser and navigate to `http://localhost:5173`.

---

### Step 3: Upload Sample Files
In the Memento AI dashboard, navigate to the **Ingest** section and upload the following three pre-prepared test files:
1. `resume.pdf` (contains professional experience, skills, and education history)
2. `project_report.pdf` (contains details about a software project called "AI Attendance System")
3. `notes.txt` (a brief text file containing meeting notes: *"Discussed AI Attendance System with Sridhar on June 28. He is the lead architect."*)

---

### Step 4: Show the Local Processing Pipeline
As the files are uploaded, point out the real-time pipeline status indicators in the UI:
- **`resume.pdf`**: `Extracting Content` (PyMuPDF) ➔ `Chunking` ➔ `Inference: Local LLM` ➔ `Generating Memory`
- **`project_report.pdf`**: `Extracting Content` (PyMuPDF) ➔ `Inference: Local LLM` ➔ `Generating Memory`
- **`notes.txt`**: `Extracting Content` (Direct) ➔ `Inference: Local LLM` ➔ `Generating Memory`

*Verify in the backend terminal logs that the CPU is executing the local GGUF model and utilizing multiple threads for prompt processing.*

---

### Step 5: Show Extracted Structured JSON Output
Navigate to the **Memories** tab and click on the "Show JSON" button for the newly extracted memories. Show that Memento AI has successfully structured the raw files into JSON:

```json
{
  "type": "project",
  "title": "AI Attendance System",
  "skills": [
    "Python",
    "OpenCV",
    "FastAPI"
  ],
  "collaborators": [
    "Sridhar"
  ],
  "source": "project_report.pdf",
  "relationship_to_source": "extracted_from_project_description"
}
```

---

### Step 6: Query the Offline Memory Engine
Navigate to the **Memory Chat** interface and type the following question:
> *"What projects have I worked on, and who is Sridhar?"*

---

### Step 7: Verify the Answer and Sources
The local LLM will generate a response similar to:
> "Based on your files, you have worked on the **AI Attendance System** using Python and OpenCV (Source: `project_report.pdf`). Additionally, **Sridhar** is the Lead Architect of the AI Attendance System, and you met with him on June 28 to discuss it (Source: `notes.txt`)."

Point out the **clickable source citations** next to the answer. Clicking on them highlights the exact text chunk extracted from the local files.

---

### Step 8: Prove the Offline & CPU-First Architecture
Show the **System Telemetry Panel** built into the Memento AI UI:

- 🛜 **Internet Connection**: `OFFLINE`
- ☁️ **Cloud API Calls**: `0`
- 🤖 **AI Inference Engine**: `Local (llama.cpp)`
- 📊 **CPU Usage**: `~65% (AVX2 acceleration active)`
- 💾 **RAM Usage**: `~2.4 GB (Model) + 0.3 GB (App)`
- 🖥️ **GPU Acceleration**: `None (CPU-Only Mode)`
