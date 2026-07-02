# Changelog

All notable changes to the **Memento AI** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-06-28

### Added
- **Backend**: FastAPI backend with llama.cpp integration for CPU-only AI inference
- **Frontend**: React-based web interface with Vite
- **Authentication**: JWT-based authentication system with user signup/login
- **Document Processing**: Multi-format document ingestion (PDF, TXT, PNG, JPG, WAV, MP3)
- **Memory Extraction**: Structured memory extraction with entity recognition
- **Chat Interface**: Streaming chat with context-aware AI responses
- **Hybrid Search**: Vector + keyword search for memory retrieval
- **Multilingual Support**: Language detection and multilingual UI (English, Telugu, Hindi)
- **AI Status Endpoint**: Real-time AI runtime status monitoring
- **Reliability Features**:
  - File size limits (25MB sync, 50MB async)
  - Invalid file type handling
  - Improved error messages
  - Retry handling with exponential backoff
  - Local caching for repeated queries
  - Background processing for large documents
- **PWA Support**: Progressive Web App with offline caching and installability
- **Mobile App**: Flutter Android application with all core features
- **CI/CD**: GitLab CI pipeline with automated quality checks
- **Pre-commit Hooks**: Automated code quality checks before commits
- **Documentation**: Comprehensive README, architecture docs, and contribution guidelines

### Changed
- **Backend**: Enhanced error handling and cleanup for temporary files
- **Frontend**: Added system status component and improved UI
- **Mobile**: Configured for APK generation with proper permissions

### Security
- **No Cloud APIs**: All AI processing is local and offline
- **CPU-Only**: No GPU requirements, runs on standard CPUs
- **Private Data**: All data stored locally, no external data transmission

---

## [0.1.0] - 2026-06-28

### Added
- **Repository Structure**: Created the baseline project hierarchy.
- **Technical Specification (`docs/SPEC.md`)**: Drafted complete specifications for the offline processing pipeline, hardware requirements, and structured data schemas.
- **Technical Architecture (`docs/ARCHITECTURE.md`)**: Designed high-level architecture and ingestion pipelines with Mermaid diagrams.
- **Demo Script (`docs/DEMO.md`)**: Outlined the MVP demonstration steps to prove offline, CPU-only capability.
- **Work Plan (`docs/WORK_PLAN.md`)**: Created a detailed task-division and milestone schedule for the two-member team.
- **Contribution Guidelines (`CONTRIBUTING.md`)**: Established commit conventions and branch-naming rules.
- **Project License**: Added the GNU Affero General Public License v3.0 (`LICENSE`).
- **Gitignore**: Implemented a root-level `.gitignore` file to prevent local models, virtual environments, node modules, and SQLite databases from being tracked.

## v1.0.0

### Added

- CPU-first AI inference
- Offline document processing
- Local LLM integration
- SQLite knowledge base
- OCR support
- Image processing
- Audio transcription
- Video processing
- ChatGPT-like chatbot
- Conversation history
- Timeline view
- Memory management
- Document upload
- Markdown rendering
- Streaming responses
- English interface
- Telugu interface
- Hindi interface
- PWA support
- Mobile APK
- CLI support