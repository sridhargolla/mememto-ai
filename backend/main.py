import json
import os
import tempfile
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from async_processor import async_processor
from audio_processor import AudioProcessorService
from auth_service import authenticate_user, create_access_token, create_user, decode_token
from cache_service import response_cache
from conversation_intelligence import ConversationIntelligence
from database import get_db, init_db
from document_ingestion import DocumentExtractor
from embedding_service import EmbeddingService
from followup_generator import FollowupGenerator
from language_service import detect_language
from memory_service import ConversationService, MemoryService
from metrics_service import MetricsService
from model_wrapper import LocalLLM
from models import Conversation, Memory, User
from personality_engine import PersonalityEngine
from progress_tracker import AsyncProgressEmitter
from prompt_builder import PromptBuilder
from prompt_sanitizer import PromptSanitizer
from response_formatter import ResponseFormatter
from retry_utils import retry_with_logging
from smart_retrieval import DocumentAwareRetriever
from system_monitor import SystemMonitor

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Memento AI Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import contextlib

from fastapi.staticfiles import StaticFiles

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")

    # Initialize embedding service
    try:
        embedding_service = EmbeddingService()
        if embedding_service.is_loaded():
            print("Embedding service initialized successfully")
        else:
            print("Warning: Embedding service failed to initialize")
    except Exception as e:
        print(f"Warning: Failed to initialize embedding service: {e}")

    # Initialize audio processor
    global audio_processor
    try:
        audio_processor = AudioProcessorService()
        if audio_processor.is_loaded():
            print("Audio processor initialized successfully")
        else:
            print("Warning: Audio processor failed to initialize")
    except Exception as e:
        print(f"Warning: Failed to initialize audio processor: {e}")
        audio_processor = None

    # Start async processor
    try:
        await async_processor.start()
        print("Async processor started successfully")
    except Exception as e:
        print(f"Warning: Failed to start async processor: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await async_processor.stop()
    print("Async processor stopped")


# ---------------------------------------------------------------------------
# Initialize local LLM — robust path resolution + detailed startup logging
# ---------------------------------------------------------------------------


def _resolve_model_path(raw_path: str) -> str:
    """
    Resolve MODEL_PATH to an absolute path.

    Priority order:
      1. The path as-is (works for absolute paths)
      2. Relative to the backend directory (where main.py lives)
      3. Relative to the project root (one level above backend)
    """
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)

    candidates = [
        raw_path,
        os.path.join(backend_dir, raw_path),
        os.path.join(project_root, raw_path.lstrip("./").lstrip("../")),
        os.path.join(project_root, "models", os.path.basename(raw_path)),
    ]

    for candidate in candidates:
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)

    return raw_path  # Return original so the error message is informative


_raw_model_path = os.getenv("MODEL_PATH", "../models/qwen2.5-3b-instruct-q4_k_m.gguf")
model_path = _resolve_model_path(_raw_model_path)
n_ctx = int(os.getenv("N_CTX", "2048"))
n_threads = int(os.getenv("N_THREADS", "4"))
n_batch = int(os.getenv("N_BATCH", "512"))

llm = None
model_loaded = False

print("=" * 60)
print("  Memento AI — Local LLM Initialization")
print("=" * 60)
print(f"  Checking model path : {model_path}")
print(f"  Context size        : {n_ctx}")
print(f"  CPU threads         : {n_threads}")
print(f"  Batch size          : {n_batch}")
print("  GPU offload layers  : 0 (CPU-only)")
print("=" * 60)

if not os.path.isfile(model_path):
    print(f"[ERROR] Model file not found: {model_path}")
    print(f"  Raw MODEL_PATH value in .env: {_raw_model_path}")
    print()
    print("  To fix, run ONE of these:")
    print("    python setup_models.py --model llm")
    print(f"    OR place a GGUF file at: {model_path}")
    print("  The system will run in degraded mode (no AI chat).")
    print("=" * 60)
else:
    print(f"  Loading GGUF model  : {os.path.basename(model_path)}")
    print(f"  File size           : {os.path.getsize(model_path) / 1024**2:.1f} MB")

    try:
        # Test that llama_cpp imported the real library, not the dummy stub
        from llama_cpp import Llama as _LlamaCheck

        if not hasattr(_LlamaCheck, "create_chat_completion"):
            raise ImportError("Loaded the dummy Llama stub — llama-cpp-python may not be installed.")

        print("  Initializing llama.cpp ...")
        print("  Loading tokenizer   ...")

        llm = LocalLLM(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, n_batch=n_batch)
        model_loaded = True

        print(f"  [SUCCESS] Model loaded in {llm.model_load_time:.2f}s")
        print("  Ready — CPU inference enabled. Fully offline.")
        print("=" * 60)

        # Record model load metric
        from database import SessionLocal

        db = SessionLocal()
        try:
            metrics_service = MetricsService(db)
            model_name = os.path.basename(model_path)
            metrics_service.record_model_load(model_name, llm.model_load_time)
        finally:
            db.close()

    except ImportError as e:
        print(f"[ERROR] llama-cpp-python not properly installed: {e}")
        print("  Run: uv pip install llama-cpp-python")
        print("       --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
        print("  The system will run in degraded mode (no AI chat).")
        print("=" * 60)
    except FileNotFoundError as e:
        print(f"[ERROR] Model file disappeared during loading: {e}")
        print("  The system will run in degraded mode (no AI chat).")
        print("=" * 60)
    except RuntimeError as e:
        err_msg = str(e).lower()
        if "not a valid gguf" in err_msg or "magic" in err_msg or "corrupt" in err_msg:
            print("[ERROR] Model file is corrupted or invalid GGUF format.")
            print(f"  Details: {e}")
            print("  Please re-download the model:")
            print("    python setup_models.py --model llm --force")
        else:
            print(f"[ERROR] llama.cpp failed to initialize: {e}")
        print("  The system will run in degraded mode (no AI chat).")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Unexpected error loading model: {type(e).__name__}: {e}")
        print("  The system will run in degraded mode (no AI chat).")
        print("=" * 60)


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    language: str | None = "en"
    continue_generating: bool | None = False


class SourceCitation(BaseModel):
    document: str | None = None
    memory: str
    relevance_score: float | None = None


class ChatResponse(BaseModel):
    response: str
    sources: list[SourceCitation] = []


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_date: str
    status: str
    memories_count: int


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    preferred_language: str = "en"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    preferred_language: str
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MemoryCreate(BaseModel):
    title: str
    content: str
    tags: str | None = None
    json_metadata: str | None = None
    source_document: str | None = None


class MemoryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: str | None = None
    json_metadata: str | None = None
    source_document: str | None = None


class MemoryResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: str | None
    json_metadata: str | None
    source_document: str | None
    created_at: datetime | str
    memory_type: str | None = None
    importance: str | None = None
    entities_people: str | None = None
    entities_organizations: str | None = None
    entities_locations: str | None = None
    entities_skills: str | None = None
    time_start: str | None = None
    time_end: str | None = None
    source_documents: str | None = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    question: str
    answer: str
    timestamp: datetime | str

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    message: str
    memories_created: int
    memories: list[MemoryResponse]


class AsyncUploadResponse(BaseModel):
    message: str
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    filename: str
    status: str
    result: dict | None
    error: str | None
    created_at: str
    completed_at: str | None


class SystemStatus(BaseModel):
    ai_engine: str
    model: str
    inference: str
    database: str
    internet: str
    external_api_calls: int
    documents_processed: int
    memories_created: int
    gpu: str = "Disabled"
    offline: bool = True
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_usage_gb: float = 0.0
    disk_free_gb: float = 0.0


class BenchmarkResult(BaseModel):
    model: str
    response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_stats: dict


class TimelineItem(BaseModel):
    id: int
    type: str | None = None
    title: str
    content: str
    date: str | None = None
    entities: dict | None = None
    created_at: str


# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "ai_runtime": "llama.cpp",
        "device": "CPU",
        "offline": True,
        "model_loaded": model_loaded,
        "model_path": model_path,
    }


# AI Status endpoint
@app.get("/status")
async def ai_status():
    """Get AI runtime status to prove CPU-first and offline operation."""
    model_name = "Not loaded"
    if llm and llm.model_path:
        model_name = llm.model_path.split("/")[-1] if "/" in llm.model_path else llm.model_path

    return {
        "runtime": "llama.cpp",
        "model": model_name,
        "device": "CPU",
        "offline": True,
        "external_api_calls": 0,
    }


# Authentication endpoints
@app.post("/auth/signup", response_model=TokenResponse)
@limiter.limit("5/minute")
async def signup(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user = create_user(db, user_data.name, user_data.email, user_data.password, user_data.preferred_language)

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            preferred_language=user.preferred_language,
            created_at=user.created_at.isoformat(),
        ),
    )


@app.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login a user and return JWT token."""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            preferred_language=user.preferred_language,
            created_at=user.created_at.isoformat(),
        ),
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(token: str, db: Session = Depends(get_db)):
    """Get current user info from JWT token."""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=user.id, name=user.name, email=user.email, created_at=user.created_at.isoformat())


# Authentication middleware
async def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    """Dependency to get current authenticated user from JWT token."""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except:
        raise HTTPException(status_code=401, detail="Invalid authentication header")

    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# System status endpoint
@app.get("/system/status", response_model=SystemStatus)
async def system_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get real-time system status."""
    # Get counts from database
    memories_count = db.query(Memory).filter(Memory.user_id == current_user.id).count()
    db.query(Conversation).filter(Conversation.user_id == current_user.id).count()

    # Get distinct count of processed files for this user
    documents_processed = (
        db.query(Memory.source_file)
        .distinct()
        .filter(Memory.user_id == current_user.id, Memory.source_file.isnot(None))
        .count()
    )

    # Get model name from environment or default
    model_name = os.getenv("MODEL_PATH", "./models/model.gguf")
    if model_name:
        model_name = model_name.split("/")[-1] if "/" in model_name else model_name

    # Get system resource metrics
    cpu_info = SystemMonitor.get_cpu_usage()
    memory_info = SystemMonitor.get_memory_usage()
    disk_info = SystemMonitor.get_disk_usage()

    return SystemStatus(
        ai_engine="llama.cpp",
        model=model_name,
        inference="Local (CPU)",
        database="SQLite",
        internet="Offline Mode",
        external_api_calls=0,
        documents_processed=documents_processed,
        memories_created=memories_count,
        gpu="Disabled",
        offline=True,
        cpu_usage_percent=cpu_info["percent"],
        memory_usage_mb=memory_info["rss_mb"],
        memory_available_mb=memory_info["available_mb"],
        disk_usage_gb=disk_info["used_gb"],
        disk_free_gb=disk_info["free_gb"],
    )


# Benchmark endpoint
@app.get("/system/benchmark", response_model=BenchmarkResult)
async def benchmark():
    """Run a quick benchmark test and return performance metrics."""
    import time

    # Get model name
    model_name = os.getenv("MODEL_PATH", "./models/model.gguf")
    if model_name:
        model_name = model_name.split("/")[-1] if "/" in model_name else model_name

    # Measure response time with a simple test
    start_time = time.time()
    test_prompt = "Hello, please respond with a brief greeting."
    tokens_generated = 0

    if llm:
        try:
            response = llm.generate(test_prompt, max_tokens=50, temperature=0.7)
            tokens_generated = len(response.split()) if response else 0
        except Exception as e:
            print(f"Benchmark test failed: {e}")

    response_time = time.time() - start_time

    # Calculate tokens per second
    tokens_per_second = tokens_generated / response_time if response_time > 0 and tokens_generated > 0 else 0

    # Get system metrics
    memory_info = SystemMonitor.get_memory_usage()
    cpu_info = SystemMonitor.get_cpu_usage()
    cache_stats = response_cache.get_stats()

    # Add tokens per second to cache stats
    cache_stats["tokens_per_second"] = round(tokens_per_second, 2)
    cache_stats["tokens_generated"] = tokens_generated

    return BenchmarkResult(
        model=model_name,
        response_time=response_time,
        memory_usage_mb=memory_info["rss_mb"],
        cpu_usage_percent=cpu_info["percent"],
        cache_stats=cache_stats,
    )


# Performance metrics endpoints
class MetricsResponse(BaseModel):
    metric_type: str
    metric_name: str | None
    duration_seconds: float
    memory_usage_mb: float | None
    cpu_usage_percent: float | None
    tokens_generated: int | None
    tokens_per_second: float | None
    document_count: int | None
    timestamp: str


class AggregatedMetricsResponse(BaseModel):
    count: int
    avg_duration: float
    min_duration: float
    max_duration: float
    avg_memory_mb: float
    avg_cpu_percent: float


@app.get("/metrics", response_model=list[MetricsResponse])
async def get_metrics(
    metric_type: str | None = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get performance metrics with optional filtering."""
    metrics_service = MetricsService(db)
    metrics = metrics_service.get_metrics(metric_type=metric_type, user_id=current_user.id, limit=limit)

    return [
        MetricsResponse(
            metric_type=m.metric_type,
            metric_name=m.metric_name,
            duration_seconds=m.duration_seconds,
            memory_usage_mb=m.memory_usage_mb,
            cpu_usage_percent=m.cpu_usage_percent,
            tokens_generated=m.tokens_generated,
            tokens_per_second=m.tokens_per_second,
            document_count=m.document_count,
            timestamp=m.timestamp.isoformat(),
        )
        for m in metrics
    ]


@app.get("/metrics/aggregated/{metric_type}", response_model=AggregatedMetricsResponse)
async def get_aggregated_metrics(
    metric_type: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get aggregated statistics for a specific metric type."""
    metrics_service = MetricsService(db)
    return metrics_service.get_aggregated_metrics(metric_type=metric_type, user_id=current_user.id)


@app.get("/metrics/inference/recent")
async def get_recent_inference(
    limit: int = 10, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get recent inference statistics."""
    metrics_service = MetricsService(db)
    return metrics_service.get_recent_inference_stats(user_id=current_user.id, limit=limit)


@app.delete("/metrics/cleanup")
async def cleanup_metrics(
    days_to_keep: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Clean up old metrics (default: keep last 30 days)."""
    metrics_service = MetricsService(db)
    deleted_count = metrics_service.cleanup_old_metrics(days_to_keep=days_to_keep)
    return {"deleted": deleted_count, "message": f"Deleted {deleted_count} old metric records"}


# Timeline endpoint
@app.get("/timeline", response_model=list[TimelineItem])
async def get_timeline(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all memories for timeline visualization (filtered by user)."""
    memories = db.query(Memory).filter(Memory.user_id == current_user.id).order_by(Memory.created_at.asc()).all()

    timeline_items = []
    for memory in memories:
        # Parse entities if available
        entities = None
        if memory.json_metadata:
            try:
                import json

                metadata = json.loads(memory.json_metadata)
                entities = metadata.get("entities", None)
            except:
                pass

        # Use time_start if available, otherwise use created_at
        date = memory.time_start if memory.time_start else memory.created_at.strftime("%Y-%m-%d")

        timeline_items.append(
            TimelineItem(
                id=memory.id,
                type=memory.memory_type,
                title=memory.title,
                content=memory.content,
                date=date,
                entities=entities,
                created_at=memory.created_at.isoformat(),
            )
        )

    return timeline_items


# Chat endpoint (streaming with AI intelligence)
@app.post("/chat")
@limiter.limit("20/minute")
async def chat(
    request: Request,
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if llm is None:

        async def error_stream():
            error_msg = (
                "Memento AI couldn't find a local AI model. Please install a compatible GGUF model. See Setup Guide."
            )
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def stream_response():
        try:
            import uuid

            session_id = chat_data.session_id or str(uuid.uuid4())

            # Initialize AI modules with session_id
            conversation_intel = ConversationIntelligence(db, current_user.id, session_id=session_id)
            personality = PersonalityEngine()
            prompt_builder = PromptBuilder(personality)
            doc_retriever = DocumentAwareRetriever(db, current_user.id)
            progress_emitter = AsyncProgressEmitter()
            response_formatter = ResponseFormatter()
            followup_gen = FollowupGenerator(conversation_intel)

            # Sanitize user input
            sanitized_message = PromptSanitizer.sanitize_input(chat_data.message)

            # Check for injection attempts
            is_injection, _pattern = PromptSanitizer.detect_injection_attempt(chat_data.message)
            if is_injection:
                yield f"data: {json.dumps({'error': 'Invalid input detected. Please rephrase your message.'})}\n\n"
                return

            # Emit typing indicator
            yield f"data: {json.dumps({'type': 'typing', 'message': 'Memento AI is thinking...'})}\n\n"

            # Process message with conversation intelligence
            intelligence = conversation_intel.process_message(sanitized_message)

            # Detect language
            detected_language = chat_data.language or detect_language(sanitized_message) or "en"

            # Emit progress updates
            has_documents = doc_retriever.has_documents()
            async for progress in progress_emitter.emit_processing_pipeline(
                has_memories=True, has_documents=has_documents
            ):
                yield f"data: {json.dumps(progress)}\n\n"

            # Retrieve with document priority
            retrieved_memories, _used_docs = doc_retriever.retrieve_with_document_priority(
                sanitized_message,
                top_k=5,
                intent=intelligence["intent"],
                conversation_context=intelligence["history"],
            )

            # Format memories for prompt
            formatted_memories = []
            for mem in retrieved_memories:
                formatted_memories.append(
                    {
                        "title": mem["title"],
                        "content": mem["content"],
                        "source_file": mem["source_file"],
                        "relevance_score": mem["enhanced_score"],
                    }
                )

            # Build dynamic prompt
            if conversation_intel.should_use_coding_mode(sanitized_message):
                prompt = prompt_builder.build_coding_prompt(
                    sanitized_message, intelligence, intelligence["history"], detected_language
                )
            else:
                prompt = prompt_builder.build_prompt(
                    sanitized_message,
                    intelligence,
                    formatted_memories,
                    intelligence["history"],
                    language=detected_language,
                )

            # If continue_generating is requested, adjust prompt to extend the last answer
            if chat_data.continue_generating and session_id:
                last_conv = (
                    db.query(Conversation)
                    .filter(
                        Conversation.user_id == current_user.id,
                        Conversation.session_id == session_id,
                    )
                    .order_by(Conversation.timestamp.desc())
                    .first()
                )
                if last_conv:
                    prompt = prompt_builder.build_prompt(
                        last_conv.question,
                        intelligence,
                        formatted_memories,
                        intelligence["history"][:-1],
                        language=detected_language,
                    )
                    prompt += f"\nContinue writing the response from the following text (do not repeat it, just continue): {last_conv.answer}"

            # Check cache
            cached_response = None
            if not chat_data.continue_generating:
                cached_response = response_cache.get(prompt, max_tokens=512, temperature=0.7)

            if cached_response:
                # Stream cached response
                for token in cached_response:
                    yield f"data: {json.dumps({'token': token})}\n\n"

                # Build sources
                sources = []
                for mem in retrieved_memories:
                    if mem["source_file"]:
                        sources.append(
                            {
                                "document": mem["source_file"],
                                "memory": mem["title"],
                                "relevance_score": mem["enhanced_score"],
                            }
                        )

                # Generate follow-ups
                followups = followup_gen.generate_followups(
                    sanitized_message,
                    cached_response,
                    intelligence["intent"],
                    has_documents,
                    intelligence["history"],
                )

                # Fetch or generate title for the session
                existing_conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
                if existing_conv:
                    title = existing_conv.title
                else:
                    import re

                    clean_q = chat_data.message.strip()
                    clean_q = re.sub(r"[#*`_\-\n\r\t]", " ", clean_q).strip()
                    title = clean_q[:40] + ("..." if len(clean_q) > 40 else "")
                    if not title:
                        title = "New Chat"

                yield f"data: {json.dumps({'sources': sources, 'followups': followups, 'cached': True, 'done': True, 'session_id': session_id, 'title': title})}\n\n"
                ConversationService.create_conversation(
                    db,
                    chat_data.message,
                    cached_response,
                    current_user.id,
                    session_id=session_id,
                    title=title,
                )
                return

            # Generate response with retry logic
            @retry_with_logging(
                max_retries=2,
                initial_delay=0.5,
                backoff_factor=2.0,
                operation_name="LLM generation",
            )
            def generate_with_retry(prompt_text):
                return llm.generate_stream(prompt_text, max_tokens=512, temperature=0.7)

            stream = generate_with_retry(prompt)

            # Stream tokens
            full_response = ""
            token_count = 0
            for token in stream:
                full_response += token
                token_count += 1
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Format response
            formatted_response = response_formatter.format_markdown(full_response)
            formatted_response = response_formatter.add_structure(formatted_response, intelligence["intent"])
            formatted_response = response_formatter.ensure_readability(formatted_response)

            # Add source attribution
            sources = []
            for mem in retrieved_memories:
                if mem["source_file"]:
                    sources.append(
                        {
                            "document": mem["source_file"],
                            "memory": mem["title"],
                            "relevance_score": mem["enhanced_score"],
                        }
                    )

            # Generate follow-up questions
            followups = followup_gen.generate_followups(
                sanitized_message,
                formatted_response,
                intelligence["intent"],
                has_documents,
                intelligence["history"],
            )

            # Cache the response
            response_cache.set(prompt, full_response, max_tokens=512, temperature=0.7)

            # Record inference metrics
            try:
                metrics_service = MetricsService(db)
                model_name = llm.model_path.split("/")[-1] if "/" in llm.model_path else llm.model_path
                metrics_service.record_inference(
                    model_name=model_name,
                    duration_seconds=llm.last_inference_time,
                    tokens_generated=token_count,
                    user_id=current_user.id,
                )
            except Exception as e:
                print(f"Failed to record inference metric: {e}")

            # Prepare performance metrics
            metrics = {
                "inference_time_seconds": round(llm.last_inference_time, 2),
                "tokens_per_second": round(llm.last_tokens_per_second, 1),
                "memory_usage_mb": round(SystemMonitor.get_memory_usage()["rss_mb"], 1),
                "model": llm.model_path.split("/")[-1] if "/" in llm.model_path else llm.model_path,
            }

            # Fetch or generate title for the session
            existing_conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
            if existing_conv:
                title = existing_conv.title
            else:
                import re

                clean_q = chat_data.message.strip()
                clean_q = re.sub(r"[#*`_\-\n\r\t]", " ", clean_q).strip()
                title = clean_q[:40] + ("..." if len(clean_q) > 40 else "")
                if not title:
                    title = "New Chat"

            # Send final data
            yield f"data: {json.dumps({'sources': sources, 'followups': followups, 'metrics': metrics, 'cached': False, 'done': True, 'session_id': session_id, 'title': title})}\n\n"

            # Save or append conversation
            if chat_data.continue_generating:
                last_conv = (
                    db.query(Conversation)
                    .filter(
                        Conversation.user_id == current_user.id,
                        Conversation.session_id == session_id,
                    )
                    .order_by(Conversation.timestamp.desc())
                    .first()
                )
                if last_conv:
                    last_conv.answer += formatted_response
                    db.commit()
            else:
                ConversationService.create_conversation(
                    db,
                    chat_data.message,
                    formatted_response,
                    current_user.id,
                    session_id=session_id,
                    title=title,
                )

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


# Memory endpoints
@app.post("/memories", response_model=MemoryResponse)
async def create_memory_endpoint(
    memory: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MemoryService.create_memory(
        db,
        memory.title,
        memory.content,
        memory.tags,
        memory.json_metadata,
        memory.source_document,
        current_user.id,
    )


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory_endpoint(
    memory_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    memory = MemoryService.get_memory(db, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return memory


@app.get("/memories", response_model=list[MemoryResponse])
async def get_all_memories_endpoint(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MemoryService.get_all_memories(db, skip, limit, current_user.id)


@app.get("/memories/tag/{tag}", response_model=list[MemoryResponse])
async def get_memories_by_tag_endpoint(
    tag: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MemoryService.get_memories_by_tag(db, tag, skip, limit, current_user.id)


@app.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory_endpoint(
    memory_id: int,
    memory_update: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memory = MemoryService.update_memory(
        db,
        memory_id,
        memory_update.title,
        memory_update.content,
        memory_update.tags,
        memory_update.json_metadata,
        memory_update.source_document,
    )
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return memory


@app.delete("/memories/{memory_id}")
async def delete_memory_endpoint(
    memory_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if not MemoryService.delete_memory(db, memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}


# Structured memory endpoints
@app.get("/memories/type/{memory_type}", response_model=list[MemoryResponse])
async def get_memories_by_type_endpoint(
    memory_type: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get memories by type (person, event, experience, project, education, skill, document)."""
    return MemoryService.get_memories_by_type(db, memory_type, skip, limit)


@app.get("/memories/importance/{importance}", response_model=list[MemoryResponse])
async def get_memories_by_importance_endpoint(
    importance: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get memories by importance level (low, medium, high)."""
    return MemoryService.get_memories_by_importance(db, importance, skip, limit)


@app.get("/memories/entity/{entity_type}/{entity_value}", response_model=list[MemoryResponse])
async def get_memories_by_entity_endpoint(
    entity_type: str,
    entity_value: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get memories containing a specific entity (people, organizations, locations, skills)."""
    return MemoryService.get_memories_by_entity(db, entity_type, entity_value, skip, limit)


# Conversation endpoints
@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    conversation = ConversationService.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.get("/conversations", response_model=list[ConversationResponse])
async def get_all_conversations_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ConversationService.get_all_conversations(db, skip, limit)


@app.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    if not ConversationService.delete_conversation(db, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}


# Pydantic schemas for conversation session endpoints
class SessionRenameRequest(BaseModel):
    title: str


class SessionPinRequest(BaseModel):
    is_pinned: bool


class LanguageUpdateRequest(BaseModel):
    preferred_language: str


@app.get("/conversations/sessions")
async def get_conversation_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all conversation sessions for the current user, ordered by pin status and recency."""
    from sqlalchemy import func

    # Group by session_id, get the title, pin status, and the maximum timestamp (latest turn)
    subquery = (
        db.query(
            Conversation.session_id,
            Conversation.title,
            Conversation.is_pinned,
            func.max(Conversation.timestamp).label("latest_time"),
        )
        .filter(Conversation.user_id == current_user.id, Conversation.session_id.isnot(None))
        .group_by(Conversation.session_id)
        .subquery()
    )

    # Query from the subquery and order
    sessions = db.query(subquery).order_by(subquery.c.is_pinned.desc(), subquery.c.latest_time.desc()).all()

    result = []
    for s in sorted(sessions, key=lambda x: (x.is_pinned, x.latest_time or datetime.min), reverse=True):
        result.append(
            {
                "session_id": s.session_id,
                "title": s.title or "New Chat",
                "is_pinned": bool(s.is_pinned),
                "timestamp": s.latest_time.isoformat() if s.latest_time else None,
            }
        )
    return result


@app.get("/conversations/session/{session_id}")
async def get_session_messages(
    session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get all messages for a specific conversation session."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id, Conversation.session_id == session_id)
        .order_by(Conversation.timestamp.asc())
        .all()
    )

    result = []
    for c in convs:
        # User message
        result.append({"role": "user", "content": c.question, "timestamp": c.timestamp.isoformat()})
        # Assistant response
        result.append({"role": "assistant", "content": c.answer, "timestamp": c.timestamp.isoformat()})
    return result


@app.post("/conversations/session/{session_id}/rename")
async def rename_session(
    session_id: str,
    rename_data: SessionRenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a conversation session."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id, Conversation.session_id == session_id)
        .all()
    )

    if not convs:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    for c in convs:
        c.title = rename_data.title

    db.commit()
    return {
        "message": "Session renamed successfully",
        "session_id": session_id,
        "title": rename_data.title,
    }


@app.post("/conversations/session/{session_id}/pin")
async def pin_session(
    session_id: str,
    pin_data: SessionPinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pin or unpin a conversation session."""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id, Conversation.session_id == session_id)
        .all()
    )

    if not convs:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    pin_val = 1 if pin_data.is_pinned else 0
    for c in convs:
        c.is_pinned = pin_val

    db.commit()
    return {
        "message": "Session pin status updated successfully",
        "session_id": session_id,
        "is_pinned": pin_data.is_pinned,
    }


@app.delete("/conversations/session/{session_id}")
async def delete_session(
    session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete all messages for a specific conversation session."""
    deleted = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id, Conversation.session_id == session_id)
        .delete()
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    db.commit()
    return {"message": "Session deleted successfully", "session_id": session_id}


@app.put("/user/language")
async def update_user_language(
    lang_data: LanguageUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update preferred language for the current authenticated user."""
    current_user.preferred_language = lang_data.preferred_language
    db.commit()
    return {
        "message": "Language preference updated successfully",
        "preferred_language": lang_data.preferred_language,
    }


# Documents endpoint
@app.get("/documents", response_model=list[DocumentResponse])
async def get_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all documents (memories with source_file) for the current user."""
    memories = (
        db.query(Memory)
        .filter(Memory.user_id == current_user.id, Memory.source_file.isnot(None))
        .order_by(Memory.created_at.desc())
        .all()
    )

    # Group by source_file to get unique documents
    documents_dict = {}
    for memory in memories:
        if memory.source_file not in documents_dict:
            documents_dict[memory.source_file] = {
                "filename": memory.source_file,
                "file_size": len(memory.content) if memory.content else 0,
                "upload_date": memory.created_at.isoformat(),
                "status": "completed",
                "memories_count": 0,
            }
        documents_dict[memory.source_file]["memories_count"] += 1

    # Convert to list with IDs
    documents = []
    for idx, (filename, doc_data) in enumerate(documents_dict.items(), 1):
        documents.append(
            DocumentResponse(
                id=idx,
                filename=doc_data["filename"],
                file_size=doc_data["file_size"],
                upload_date=doc_data["upload_date"],
                status=doc_data["status"],
                memories_count=doc_data["memories_count"],
            )
        )

    return documents


@app.delete("/documents/{document_id}")
async def delete_document_endpoint(
    document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete a document and all its associated memories."""
    # Get all memories with this source_file
    documents = db.query(Memory).filter(Memory.user_id == current_user.id, Memory.source_file.isnot(None)).all()

    # Group by source_file to find the document
    documents_dict = {}
    for memory in documents:
        if memory.source_file not in documents_dict:
            documents_dict[memory.source_file] = []
        documents_dict[memory.source_file].append(memory)

    # Get the document by index
    document_list = list(documents_dict.keys())
    if document_id < 1 or document_id > len(document_list):
        raise HTTPException(status_code=404, detail="Document not found")

    filename = document_list[document_id - 1]

    # Delete all memories with this source_file
    db.query(Memory).filter(Memory.user_id == current_user.id, Memory.source_file == filename).delete()

    db.commit()
    return {"message": "Document deleted successfully"}


# Async document upload endpoint
@app.post("/upload/async", response_model=AsyncUploadResponse)
@limiter.limit("10/minute")
async def upload_document_async(request: Request, file: UploadFile = File(...)):
    """Upload document for async background processing."""

    # File size limit: 50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

    # Get file extension
    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""

    # Validate file type
    supported_types = ["pdf", "txt", "png", "jpg", "jpeg", "gif", "bmp", "tiff", "wav", "mp3"]
    if file_extension not in supported_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{file_extension}'. Supported types: {', '.join(supported_types)}",
        )

    # Check file size
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is 50MB. Your file is {file_size / (1024 * 1024):.2f}MB",
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty. Please upload a valid file.")

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    # Submit to async processor
    try:
        task_id = await async_processor.submit_task(temp_file_path, file.filename, file_extension)
    except Exception as e:
        # Clean up temp file if submission fails
        import os

        with contextlib.suppress(BaseException):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to submit document for processing: {e!s}")

    return AsyncUploadResponse(message="Document submitted for processing", task_id=task_id)


# Task status endpoint
@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of an async processing task."""
    status = async_processor.get_task_status(task_id)

    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(**status)


# ─── Universal file upload endpoint ────────────────────────────────────────────
# Accepts ANY file type, saves instantly as memory (no blocking AI calls).
# Text/PDF content is extracted quickly; video/audio/image just stores metadata.

# File-type categories
TEXT_TYPES = {
    "pdf",
    "txt",
    "md",
    "csv",
    "json",
    "xml",
    "html",
    "log",
    "py",
    "js",
    "ts",
    "jsx",
    "tsx",
    "java",
    "c",
    "cpp",
    "cs",
    "go",
    "rs",
    "docx",
    "doc",
    "odt",
    "rtf",
}
IMAGE_TYPES = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp", "svg", "ico"}
AUDIO_TYPES = {"mp3", "wav", "ogg", "flac", "aac", "m4a", "wma", "opus"}
VIDEO_TYPES = {"mp4", "mov", "avi", "mkv", "webm", "flv", "wmv", "mpeg", "mpg", "3gp", "ts", "m4v"}
DOC_TYPES = {"pdf", "txt", "md", "csv", "docx", "doc", "rtf", "odt"}


def _get_file_category(ext: str) -> str:
    ext = ext.lower()
    if ext in VIDEO_TYPES:
        return "video"
    if ext in AUDIO_TYPES:
        return "audio"
    if ext in IMAGE_TYPES:
        return "image"
    if ext in DOC_TYPES:
        return "document"
    return "file"


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    return f"{size_bytes / 1024**3:.1f} GB"


@app.post("/upload", response_model=DocumentUploadResponse)
@limiter.limit("20/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Universal upload: accepts ANY file type and saves it instantly as a memory."""

    # Hard limit: 500 MB
    MAX_FILE_SIZE = 500 * 1024 * 1024

    filename = file.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    category = _get_file_category(file_ext)
    upload_time = datetime.utcnow()

    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large ({_format_size(file_size)}). Max 500 MB.")

    # Save the file persistently to backend/uploads
    persistent_file_path = os.path.join(uploads_dir, filename)
    try:
        with open(persistent_file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        print(f"[UPLOAD] Failed to save persistent file: {e}")

    # ── Try to extract text for documents/PDFs only ───────────────────────────
    extracted_text = ""
    temp_file_path = None
    if category in ("document",) or file_ext in TEXT_TYPES:
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tf:
                tf.write(content)
                temp_file_path = tf.name
            extractor = DocumentExtractor()
            extracted_text = extractor.extract_text(temp_file_path, file_ext, audio_processor) or ""
        except Exception as ex:
            print(f"[UPLOAD] Text extraction skipped for {filename}: {ex}")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                with contextlib.suppress(Exception):
                    os.unlink(temp_file_path)

    # ── Build the memory content ──────────────────────────────────────────────
    size_str = _format_size(file_size)
    upload_ts_str = upload_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Rich metadata block stored as the memory content
    meta_block = (
        f"File: {filename}\n"
        f"Type: {category.upper()} ({file_ext.upper() if file_ext else 'unknown'})\n"
        f"Size: {size_str}\n"
        f"Uploaded: {upload_ts_str}\n"
        f"Uploaded by: {current_user.name} ({current_user.email})\n"
    )

    if extracted_text:
        # Truncate very long documents to keep memory manageable
        preview = extracted_text[:3000] + ("…[truncated]" if len(extracted_text) > 3000 else "")
        memory_content = meta_block + f"\nContent Preview:\n{preview}"
    else:
        memory_content = meta_block + "\nNote: Content not extracted (binary/media file stored as metadata)."

    # ── Save memory immediately ────────────────────────────────────────────────
    memory_title = f"[{category.capitalize()}] {filename}"
    tags = f"upload,{category},{file_ext}" if file_ext else f"upload,{category}"

    import json as _json

    metadata_json = _json.dumps(
        {
            "filename": filename,
            "file_size_bytes": file_size,
            "file_size_human": size_str,
            "file_type": category,
            "file_extension": file_ext,
            "upload_timestamp": upload_ts_str,
            "has_text": bool(extracted_text),
        }
    )

    memory = MemoryService.create_memory(
        db,
        title=memory_title,
        content=memory_content,
        tags=tags,
        metadata=metadata_json,
        source_document=filename,
        user_id=current_user.id,
        type=category,
    )

    return DocumentUploadResponse(
        message=f"✅ '{filename}' uploaded and saved as memory.",
        memories_created=1,
        memories=[memory],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
