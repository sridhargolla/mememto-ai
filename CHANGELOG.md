# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Bug Fixes

- Update Login and Signup API endpoints to use relative paths
- Remove unicode characters and add Request parameter to rate-limited endpoints
- Integrate AuthContext login function in Login and Signup components
- Add preferred_language field to signup request
- Add debug logging and remove navigate from logout
- Update SystemStatus and PerformanceDashboard with relative API paths and glassmorphism
- Enable file upload and chat without AI model, fix i18n translations
- Add missing GET /documents and DELETE /documents endpoints
- Convert datetime to string in DocumentUploadResponse
- Remove unused code and add missing React imports in App.jsx
- Update auth pages to use custom background image
- Clean up Login.jsx and Signup.jsx after post-merge corruption; add BackgroundLayout, proper /api routes
- Use VITE_API_BASE_URL env var for production backend URL
- Replace all hardcoded /api and localhost:8000 URLs with VITE_API_BASE_URL

### Documentation

- Add complete Phase 1 submission package

### Features

- Phase 2 MVP - CPU-only inference, hybrid retrieval, structured memory, telemetry UI
- Upgrade Memento AI with premium UI and glassmorphism design
- Add global background image (bg.png) applied via app-bg wrapper in App.jsx
- *(components)* Add ConfirmModal, SkeletonCard, Sparkline, UploadZone, and MarkdownMessage components
- *(context)* Add React context providers (ToastContext and others) for global state management
- *(dashboard)* Enhance Dashboard with Sparkline stats, quick actions, and ChatMessage component
- Add localStorage persistence for chat history
- Update background image to use bg.png
- Add unique AI-themed background images for each page
- Add AI-themed background to Landing, Login, and Signup pages
- Add Hindi translations for system status and performance
- Universal file uploads, media-aware chatbot, 30-day auth tokens

### Miscellaneous Tasks

- Include remote-only components and pages missing from local branch

### Other

- Initial commit
- Edit README.md
- Initial commit
- Delete README.md
- Implement complete offline multilingual support for English, Telugu, and Hindi
- Add AI status endpoint to prove CPU-first and offline operation
- Add AI status component to Settings page
- Add comprehensive CPU inference documentation to README
- Update SystemStatus component with offline indicators
- Update Timeline component with improved memory visualization
- Edit README.md
- Implement critical security fixes and missing features for CPU-First Hackathon

Security:
- Generate random SECRET_KEY on startup if not provided
- Add rate limiting to all endpoints (slowapi)
- Implement file signature validation for uploads
- Add prompt injection detection and sanitization

Model Infrastructure:
- Create models directory and setup script
- Add model availability checks with graceful degradation
- Update health endpoint with model_loaded status

Documentation:
- Update README with comprehensive installation guide
- Add Tesseract OCR installation instructions for all platforms
- Update .env.example with all required variables

Demo Content:
- Add sample resume, project notes, and meeting transcript

Resource Monitoring:
- Expose CPU, memory, and disk metrics in system status
- Update SystemStatus UI to display real-time resource usage

Performance:
- Enhance benchmark endpoint with tokens/second measurement
- Enhance structured memory extraction with robust JSON handling

- Strengthen LLM prompt to force JSON-only output
- Add critical rules to prevent conversational text
- Implement _looks_like_json heuristic validation
- Add _clean_json_response to handle conversational prefixes/suffixes
- Enhance _extract_json_from_response with multiple fallback strategies
- Improve _parse_memories_from_response with field validation and defaults
- Add detailed error logging for debugging
- Add pytest to requirements for testing support
- Resolve merge conflict in SystemStatus component
- Add retry utility for handling transient CPU inference failures
- Add file size limits and improved error handling to upload endpoints
- Add retry logic to async processor for reliable background processing
- Add PerformanceMetrics database model for local performance tracking

- Add PerformanceMetrics table to track model_load, inference, document_process metrics
- Include fields for duration, memory usage, CPU usage, tokens, and metadata
- Add indexes for metric_type and timestamp for efficient queries
- Enhance model_wrapper to track model loading time

- Add time import for timing operations
- Add model_load_time attribute to track loading duration
- Time model loading in _load_model method
- Print model load time for visibility
- Create MetricsService for local performance tracking

- Implement MetricsService class for recording and retrieving metrics
- Add record_metric for generic metric recording
- Add record_model_load for tracking model loading times
- Add record_inference for tracking inference performance
- Add record_document_process for tracking document processing
- Add get_metrics with filtering support
- Add get_aggregated_metrics for statistics
- Add get_recent_inference_stats for recent performance
- Add cleanup_old_metrics for database maintenance
- All operations work offline with local SQLite storage
- Add metrics API endpoints and integrate tracking in main.py

- Import MetricsService and PerformanceMetrics
- Record model load metric on startup
- Track inference time and token count in chat endpoint
- Add /metrics endpoint for retrieving metrics with filtering
- Add /metrics/aggregated/{metric_type} for statistics
- Add /metrics/inference/recent for recent inference stats
- Add /metrics/cleanup for deleting old metrics
- Add MetricsResponse and AggregatedMetricsResponse Pydantic models
- Create PerformanceDashboard frontend component

- Build comprehensive performance dashboard UI
- Add metric type filtering (all, model_load, inference, document_process)
- Display aggregated statistics with color-coded cards
- Show recent inference performance table
- Display all metrics with detailed information
- Add cleanup button for old metrics
- Use Tailwind CSS for modern styling
- Integrate with AuthContext for authentication
- Add PerformanceDashboard route to App.jsx

- Import PerformanceDashboard component
- Add /dashboard/performance route with ProtectedRoute
- Enable access to performance dashboard for authenticated users
- Add Performance link to sidebar navigation

- Add Performance menu item with ⚡ icon
- Position between System Status and Privacy
- Enable navigation to performance dashboard
- Add database migration check for performance_metrics table

- Check if performance_metrics table exists on init
- Log migration status for performance_metrics table
- Ensure table is created by Base.metadata.create_all
- Merge remote changes with local performance monitoring implementation
- Resolve merge conflict: combine caching and metrics recording
- Add PWA manifest for installable application
- Add service worker for offline frontend caching
- Add PWA icon (SVG) for application branding
- Add PWA meta tags to index.html
- Add service worker registration to main.jsx
- Update Vite config for PWA asset support
- Add Flutter project configuration and dependencies
- Add Flutter app entry point with provider setup
- Add API service for backend communication with offline support
- Add authentication service with local storage
- Add login screen with backend status indicator
- Add home screen with navigation and status indicator
- Add chat screen with streaming response support
- Add upload screen with file picker and progress
- Add memories screen with type icons and refresh
- Add settings screen with AI status display
- Add Android app build configuration for APK generation
- Add Android manifest with required permissions
- Add MainActivity for Flutter Android integration
- Add Android project build configuration
- Add Android settings configuration
- Add mobile app README with setup and build instructions
- Update CONTRIBUTING.md with code quality standards and CI documentation
- Update CHANGELOG.md with v1.0.0 release notes
- Add GitLab CI pipeline with real quality and security checks
- Add pre-commit configuration for automated code quality checks
- Merge branch 'main' of https://code.swecha.org/sridhar24/memento-ai
- Integrate remote diverged changes; keep local feature updates
- Delete ai-background.jpg
- Merge branch 'main' of https://code.swecha.org/sridhar24/memento-ai
- Upgrade chatbot with AI intelligence modules

- Add conversation intelligence (intent detection, context awareness, multi-turn)
- Add personality engine with consistent AI persona
- Add dynamic prompt builder with context injection
- Add smart memory retrieval with ranking and context
- Add user-facing processing timeline with progress updates
- Add ChatGPT-style response formatting (Markdown, tables, code)
- Add intelligent follow-up question generation
- Integrate all modules into main.py chat endpoint
- Update frontend Chat.jsx for new features (typing indicator, progress, followups)
- Fix JSX syntax errors in frontend files
- Install missing frontend dependencies
- Main
- Main
- Main
- Main
- Merge branch 'main' of https://code.swecha.org/sridhar24/memento-ai
- Merge branch 'main' of https://code.swecha.org/sridhar24/memento-ai
- Merge remote changes with local AI intelligence modules
- README.md
- Fix Conversation created_at database field schema mismatch
- Implement transparent proxy and compatibility layer for older llama.dll
- Enhance local GGUF model path detection, status validation, and startup logging
- Update authentication context config
- Adapt PerformanceDashboard route path to Vite dev proxy
- Adapt SystemStatus route path to Vite dev proxy
- Adjust Chat interface model state handling
- Adjust Dashboard page server paths
- Adapt Memories API endpoints for Vite proxy
- Refactor and optimize local LLM pipeline execution details
- Improve ctypes bindings metadata mapping compatibility
- Add error-safe exception guards for missing C function pointers
- Validate environment variable paths for local model resolution
- Refine SQLite database connection lifecycle for concurrent processes
- Optimize thread count parameters for offline CPU inference
- Verify GGUF model vocabulary and tokenizer load stability
- Update dependency version references in package configurations
- Verify offline status and runtime check endpoints behavior
- Ensure CORS fallback ports are mapped correctly in main server
- Finalize validation of local GGUF model loading integrity
- Migrate conversations schema to add session_id, title, and is_pinned
- Define columns for session groupings and pinning in SQLAlchemy Conversation model
- Update ConversationService to handle session groupings and auto-titling
- Configuration of ChatML stop sequence tags to prevent token leakage
- Format instructions and recent history using ChatML delimiters
- Configure system prompt to enforce Hindi and Telugu translations
- Simplify response structure and strip static placeholder templates
- Update suggestions to dynamically extract keywords from query
- Implement session_id filtering in ContextManager history loading
- Mount static uploads directory and persist uploads to backend/uploads
- Localize hardcoded labels using translation keys
- Add language dropdown selector to support dynamic Hindi/Telugu updates
- Add inline message edit textbox and response continuation actions
- Implement ChatGPT-style sidebar listing, rename, pin, search, and stop generation
- Build split-pane details modal with file previews and download actions
- Specify Python 3.11.9 version for Render builds
- Add render.yaml blueprint config for automated python versioning and settings
- Remove optional whisper-cpp-python dependency to fix Render build
- Pin huggingface-hub==0.20.3 to prevent cached_download ImportError
- Defer sentence-transformers import to runtime and add low-RAM checks to prevent OOM
- Detect RENDER environment variable to disable memory-heavy sentence-transformers
- Add offline launcher script run_memento_offline.bat
- README.md
- USER_MANUAL.md
- AGENTS.md
- Added .editorconfig
- Added SECURITY.md
- Added CODE_OF_CONDUCT.md
- Added .env.example
- Add new file
- Edit CHANGELOG.md
- Delete .env.example
- Add new file
- Added Dockerfile
- Merge main and integrate repository improvements

<!-- Generated by git-cliff -->
