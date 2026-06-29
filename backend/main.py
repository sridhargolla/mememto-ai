import os
import tempfile
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from model_wrapper import LocalLLM
from database import init_db, get_db
from models import Memory, Conversation, PerformanceMetrics
from memory_service import MemoryService, ConversationService
from document_ingestion import DocumentExtractor, MemoryExtractor
from audio_processor import AudioProcessorService
from retrieval import MemoryRetriever
from embedding_service import EmbeddingService
from memory_extractor_service import MemoryExtractorService
from memory_schema import MemorySchema
from system_monitor import SystemMonitor
from cache_service import response_cache
from async_processor import async_processor, ProcessingStatus
from auth_service import create_user, authenticate_user, create_access_token, decode_token
from language_service import detect_language, get_language_instruction
from retry_utils import retry_with_logging
from prompt_sanitizer import PromptSanitizer
from metrics_service import MetricsService
from sqlalchemy.orm import Session
from models import User

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
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Initialize local LLM
model_path = os.getenv("MODEL_PATH", "./models/model.gguf")
n_ctx = int(os.getenv("N_CTX", "2048"))
n_threads = int(os.getenv("N_THREADS", "4"))

llm = None
model_loaded = False

# Check if model file exists before attempting to load
if os.path.exists(model_path):
    try:
        llm = LocalLLM(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads)
        model_loaded = True
        print(f"[SUCCESS] Model loaded successfully from {model_path}")
        
        # Record model load metric
        from database import SessionLocal
        db = SessionLocal()
        try:
            metrics_service = MetricsService(db)
            model_name = model_path.split('/')[-1] if '/' in model_path else model_path
            metrics_service.record_model_load(model_name, llm.model_load_time)
        finally:
            db.close()
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        print(f"  Model path: {model_path}")
        print(f"  The system will run in degraded mode (no AI chat).")
else:
    print(f"[ERROR] Model file not found: {model_path}")
    print(f"  Please run 'python setup_models.py' to download required models.")
    print(f"  Or manually download a GGUF model and update MODEL_PATH in .env")
    print(f"  The system will run in degraded mode (no AI chat).")


# Pydantic models
class ChatRequest(BaseModel):
    message: str


class SourceCitation(BaseModel):
    document: Optional[str] = None
    memory: str
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[SourceCitation] = []


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
    tags: Optional[str] = None
    json_metadata: Optional[str] = None
    source_document: Optional[str] = None


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    json_metadata: Optional[str] = None
    source_document: Optional[str] = None


class MemoryResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[str]
    json_metadata: Optional[str]
    source_document: Optional[str]
    created_at: datetime
    memory_type: Optional[str] = None
    importance: Optional[str] = None
    entities_people: Optional[str] = None
    entities_organizations: Optional[str] = None
    entities_locations: Optional[str] = None
    entities_skills: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    source_documents: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    question: str
    answer: str
    timestamp: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    message: str
    memories_created: int
    memories: List[MemoryResponse]


class AsyncUploadResponse(BaseModel):
    message: str
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    filename: str
    status: str
    result: Optional[dict]
    error: Optional[str]
    created_at: str
    completed_at: Optional[str]


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
    type: Optional[str] = None
    title: str
    content: str
    date: Optional[str] = None
    entities: Optional[dict] = None
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
        "model_path": model_path
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
        "external_api_calls": 0
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
            created_at=user.created_at.isoformat()
        )
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
            created_at=user.created_at.isoformat()
        )
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
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at.isoformat()
    )


# Authentication middleware
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
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
    conversations_count = db.query(Conversation).filter(Conversation.user_id == current_user.id).count()
    
    # Get distinct count of processed files for this user
    documents_processed = db.query(Memory.source_file).distinct().filter(
        Memory.user_id == current_user.id,
        Memory.source_file.isnot(None)
    ).count()
    
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
        cpu_usage_percent=cpu_info['percent'],
        memory_usage_mb=memory_info['rss_mb'],
        memory_available_mb=memory_info['available_mb'],
        disk_usage_gb=disk_info['used_gb'],
        disk_free_gb=disk_info['free_gb']
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
    cache_stats['tokens_per_second'] = round(tokens_per_second, 2)
    cache_stats['tokens_generated'] = tokens_generated
    
    return BenchmarkResult(
        model=model_name,
        response_time=response_time,
        memory_usage_mb=memory_info['rss_mb'],
        cpu_usage_percent=cpu_info['percent'],
        cache_stats=cache_stats
    )


# Performance metrics endpoints
class MetricsResponse(BaseModel):
    metric_type: str
    metric_name: Optional[str]
    duration_seconds: float
    memory_usage_mb: Optional[float]
    cpu_usage_percent: Optional[float]
    tokens_generated: Optional[int]
    tokens_per_second: Optional[float]
    document_count: Optional[int]
    timestamp: str


class AggregatedMetricsResponse(BaseModel):
    count: int
    avg_duration: float
    min_duration: float
    max_duration: float
    avg_memory_mb: float
    avg_cpu_percent: float


@app.get("/metrics", response_model=List[MetricsResponse])
async def get_metrics(
    metric_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
            timestamp=m.timestamp.isoformat()
        )
        for m in metrics
    ]


@app.get("/metrics/aggregated/{metric_type}", response_model=AggregatedMetricsResponse)
async def get_aggregated_metrics(
    metric_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated statistics for a specific metric type."""
    metrics_service = MetricsService(db)
    return metrics_service.get_aggregated_metrics(metric_type=metric_type, user_id=current_user.id)


@app.get("/metrics/inference/recent")
async def get_recent_inference(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent inference statistics."""
    metrics_service = MetricsService(db)
    return metrics_service.get_recent_inference_stats(user_id=current_user.id, limit=limit)


@app.delete("/metrics/cleanup")
async def cleanup_metrics(
    days_to_keep: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up old metrics (default: keep last 30 days)."""
    metrics_service = MetricsService(db)
    deleted_count = metrics_service.cleanup_old_metrics(days_to_keep=days_to_keep)
    return {"deleted": deleted_count, "message": f"Deleted {deleted_count} old metric records"}


# Timeline endpoint
@app.get("/timeline", response_model=List[TimelineItem])
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
                entities = metadata.get('entities', None)
            except:
                pass
        
        # Use time_start if available, otherwise use created_at
        date = memory.time_start if memory.time_start else memory.created_at.strftime('%Y-%m-%d')
        
        timeline_items.append(TimelineItem(
            id=memory.id,
            type=memory.memory_type,
            title=memory.title,
            content=memory.content,
            date=date,
            entities=entities,
            created_at=memory.created_at.isoformat()
        ))
    
    return timeline_items


# Chat endpoint (streaming)
@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, chat_data: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if llm is None:
        async def error_stream():
            error_msg = "AI model not loaded. Please download models using 'python setup_models.py' "
            error_msg += "or place a GGUF model in the models/ directory and update MODEL_PATH in .env"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    async def stream_response():
        try:
            # Sanitize user input to prevent prompt injection
            sanitized_message = PromptSanitizer.sanitize_input(chat_data.message)
            
            # Check for injection attempts
            is_injection, pattern = PromptSanitizer.detect_injection_attempt(chat_data.message)
            if is_injection:
                yield f"data: {json.dumps({'error': 'Invalid input detected. Please rephrase your message.'})}\n\n"
                return
            
            # Detect language from user message
            detected_language = detect_language(sanitized_message)
            language_instruction = get_language_instruction(detected_language)
            
            # Retrieve relevant memories using Hybrid Search (filtered by user)
            retriever = MemoryRetriever()
            relevant_memories = retriever.retrieve_hybrid(db, sanitized_message, top_k=3, user_id=current_user.id)
            
            # Build context from retrieved memories
            retrieved_context = retriever.format_context(relevant_memories)
            
            # Query all files uploaded by this user to answer questions about media files, sizes, upload times, and storage space
            all_user_memories = db.query(Memory).filter(Memory.user_id == current_user.id).all()
            uploaded_files = []
            total_space = 0
            for m in all_user_memories:
                if m.source_file or (m.tags and 'upload' in m.tags):
                    file_info = {
                        "name": m.source_file or m.title,
                        "type": "file",
                        "size": "unknown",
                        "uploaded": m.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
                    }
                    if m.metadata_json:
                        try:
                            meta = json.loads(m.metadata_json)
                            file_info["type"] = meta.get("file_type", file_info["type"])
                            file_info["size"] = meta.get("file_size_human", file_info["size"])
                            total_space += meta.get("file_size_bytes", 0)
                        except:
                            pass
                    uploaded_files.append(file_info)
            
            files_summary_lines = []
            if uploaded_files:
                files_summary_lines.append("\nUploaded Files & Storage Metadata:")
                files_summary_lines.append(f"- Total storage occupied: {_format_size(total_space)}")
                for f in uploaded_files:
                    files_summary_lines.append(
                        f"- File: '{f['name']}' | Type: {f['type'].upper()} | Size: {f['size']} | Uploaded: {f['uploaded']}"
                    )
            
            files_context = "\n".join(files_summary_lines)
            context = (retrieved_context + "\n" + files_context).strip()
            
            # Load conversation history (last 5 turns) for multi-turn conversational context
            recent_convs = ConversationService.get_all_conversations(db, skip=0, limit=5, user_id=current_user.id)
            recent_convs.reverse()  # chronological order
            
            history_str = ""
            for conv in recent_convs:
                history_str += f"User: {conv.question}\nAssistant: {conv.answer}\n"
            
            # Build structured source citations
            sources = []
            for memory, score in relevant_memories:
                citation = SourceCitation(
                    document=memory.source_file,
                    memory=memory.title,
                    relevance_score=score
                )
                sources.append(citation)
            
            # Generate response with or without context
            if context:
                # Augment prompt with context, history, and language instruction
                augmented_prompt = f"""You are a helpful offline personal memory assistant. Answer the user's question based on the retrieved context below.
If the answer cannot be found in the context, use your general knowledge but mention it is not in your personal memories.

{language_instruction}

Retrieved Context:
{context}

Recent Conversation History:
{history_str}
User question: {sanitized_message}

Answer:"""
                
                # Check cache first for repeated queries
                cached_response = response_cache.get(augmented_prompt, max_tokens=512, temperature=0.7)
                if cached_response:
                    # Stream cached response
                    for token in cached_response:
                        yield f"data: {json.dumps({'token': token})}\n\n"
                    
                    # Send sources and metrics (cached)
                    sources_data = [s.dict() for s in sources]
                    yield f"data: {json.dumps({'sources': sources_data, 'cached': True, 'done': True})}\n\n"
                    ConversationService.create_conversation(db, chat_data.message, cached_response, current_user.id)
                    return
                
                # Use retry logic for LLM generation (CPU inference can be slow)
                @retry_with_logging(max_retries=2, initial_delay=0.5, backoff_factor=2.0, operation_name="LLM generation")
                def generate_with_retry(prompt):
                    return llm.generate_stream(prompt, max_tokens=512, temperature=0.7)
                
                stream = generate_with_retry(augmented_prompt)
            else:
                # No relevant memories found, use chat history prompt with language instruction
                chat_prompt = f"""You are a helpful offline personal memory assistant.
                
{language_instruction}

Recent Conversation History:
{history_str}
User question: {sanitized_message}

Answer:"""
                
                # Check cache first for repeated queries
                cached_response = response_cache.get(chat_prompt, max_tokens=512, temperature=0.7)
                if cached_response:
                    # Stream cached response
                    for token in cached_response:
                        yield f"data: {json.dumps({'token': token})}\n\n"
                    
                    # Send sources and metrics (cached)
                    yield f"data: {json.dumps({'sources': [], 'cached': True, 'done': True})}\n\n"
                    ConversationService.create_conversation(db, chat_data.message, cached_response, current_user.id)
                    return
                
                # Use retry logic for LLM generation (CPU inference can be slow)
                @retry_with_logging(max_retries=2, initial_delay=0.5, backoff_factor=2.0, operation_name="LLM generation")
                def generate_with_retry(prompt):
                    return llm.generate_stream(prompt, max_tokens=512, temperature=0.7)
                
                stream = generate_with_retry(chat_prompt)
            
            # Stream tokens
            full_response = ""
            token_count = 0
            for token in stream:
                full_response += token
                token_count += 1
                yield f"data: {json.dumps({'token': token})}\n\n"
            
            # Cache the response for future use
            if context:
                response_cache.set(augmented_prompt, full_response, max_tokens=512, temperature=0.7)
            else:
                response_cache.set(chat_prompt, full_response, max_tokens=512, temperature=0.7)
            
            # Record inference metrics to database
            try:
                metrics_service = MetricsService(db)
                model_name = llm.model_path.split("/")[-1] if "/" in llm.model_path else llm.model_path
                metrics_service.record_inference(
                    model_name=model_name,
                    duration_seconds=llm.last_inference_time,
                    tokens_generated=token_count,
                    user_id=current_user.id
                )
            except Exception as e:
                print(f"Failed to record inference metric: {e}")
            
            # Prepare performance metrics
            metrics = {
                "inference_time_seconds": round(llm.last_inference_time, 2),
                "tokens_per_second": round(llm.last_tokens_per_second, 1),
                "memory_usage_mb": round(SystemMonitor.get_memory_usage()['rss_mb'], 1),
                "model": llm.model_path.split("/")[-1] if "/" in llm.model_path else llm.model_path
            }
            
            # Send sources and metrics at the end
            sources_data = [s.dict() for s in sources]
            yield f"data: {json.dumps({'sources': sources_data, 'metrics': metrics, 'cached': False, 'done': True})}\n\n"
            
            # Save conversation to database
            ConversationService.create_conversation(db, chat_data.message, full_response, current_user.id)
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")



# Memory endpoints
@app.post("/memories", response_model=MemoryResponse)
async def create_memory_endpoint(memory: MemoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MemoryService.create_memory(db, memory.title, memory.content, memory.tags, memory.json_metadata, memory.source_document, current_user.id)


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory_endpoint(memory_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memory = MemoryService.get_memory(db, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return memory


@app.get("/memories", response_model=List[MemoryResponse])
async def get_all_memories_endpoint(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MemoryService.get_all_memories(db, skip, limit, current_user.id)


@app.get("/memories/tag/{tag}", response_model=List[MemoryResponse])
async def get_memories_by_tag_endpoint(tag: str, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MemoryService.get_memories_by_tag(db, tag, skip, limit, current_user.id)


@app.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory_endpoint(memory_id: int, memory_update: MemoryUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memory = MemoryService.update_memory(db, memory_id, memory_update.title, memory_update.content, memory_update.tags, memory_update.json_metadata, memory_update.source_document)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return memory


@app.delete("/memories/{memory_id}")
async def delete_memory_endpoint(memory_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if not MemoryService.delete_memory(db, memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}


# Structured memory endpoints
@app.get("/memories/type/{memory_type}", response_model=List[MemoryResponse])
async def get_memories_by_type_endpoint(memory_type: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get memories by type (person, event, experience, project, education, skill, document)."""
    return MemoryService.get_memories_by_type(db, memory_type, skip, limit)


@app.get("/memories/importance/{importance}", response_model=List[MemoryResponse])
async def get_memories_by_importance_endpoint(importance: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get memories by importance level (low, medium, high)."""
    return MemoryService.get_memories_by_importance(db, importance, skip, limit)


@app.get("/memories/entity/{entity_type}/{entity_value}", response_model=List[MemoryResponse])
async def get_memories_by_entity_endpoint(entity_type: str, entity_value: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get memories containing a specific entity (people, organizations, locations, skills)."""
    return MemoryService.get_memories_by_entity(db, entity_type, entity_value, skip, limit)


# Conversation endpoints
@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    conversation = ConversationService.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.get("/conversations", response_model=List[ConversationResponse])
async def get_all_conversations_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ConversationService.get_all_conversations(db, skip, limit)


@app.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: int, db: Session = Depends(get_db)):
    if not ConversationService.delete_conversation(db, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}


# Async document upload endpoint
@app.post("/upload/async", response_model=AsyncUploadResponse)
@limiter.limit("10/minute")
async def upload_document_async(request: Request, file: UploadFile = File(...)):
    """Upload document for async background processing."""
    
    # File size limit: 50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    
    # Get file extension
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    # Validate file type
    supported_types = ['pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'wav', 'mp3']
    if file_extension not in supported_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: '{file_extension}'. Supported types: {', '.join(supported_types)}"
        )
    
    # Check file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is 50MB. Your file is {file_size / (1024 * 1024):.2f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty. Please upload a valid file."
        )
    
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
        try:
            os.unlink(temp_file_path)
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit document for processing: {str(e)}"
        )
    
    return AsyncUploadResponse(
        message="Document submitted for processing",
        task_id=task_id
    )


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
TEXT_TYPES   = {'pdf', 'txt', 'md', 'csv', 'json', 'xml', 'html', 'log', 'py',
                'js', 'ts', 'jsx', 'tsx', 'java', 'c', 'cpp', 'cs', 'go', 'rs',
                'docx', 'doc', 'odt', 'rtf'}
IMAGE_TYPES  = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico'}
AUDIO_TYPES  = {'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'wma', 'opus'}
VIDEO_TYPES  = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'mpeg', 'mpg',
                '3gp', 'ts', 'm4v'}
DOC_TYPES    = {'pdf', 'txt', 'md', 'csv', 'docx', 'doc', 'rtf', 'odt'}


def _get_file_category(ext: str) -> str:
    ext = ext.lower()
    if ext in VIDEO_TYPES:  return 'video'
    if ext in AUDIO_TYPES:  return 'audio'
    if ext in IMAGE_TYPES:  return 'image'
    if ext in DOC_TYPES:    return 'document'
    return 'file'


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:           return f"{size_bytes} B"
    if size_bytes < 1024 ** 2:      return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 ** 3:      return f"{size_bytes / 1024 ** 2:.1f} MB"
    return f"{size_bytes / 1024 ** 3:.1f} GB"


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

    filename     = file.filename or "unknown"
    file_ext     = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    category     = _get_file_category(file_ext)
    upload_time  = datetime.utcnow()

    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large ({_format_size(file_size)}). Max 500 MB.")

    # ── Try to extract text for documents/PDFs only ───────────────────────────
    extracted_text = ""
    temp_file_path = None
    if category in ('document',) or file_ext in TEXT_TYPES:
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
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

    # ── Build the memory content ──────────────────────────────────────────────
    size_str      = _format_size(file_size)
    upload_ts_str = upload_time.strftime('%Y-%m-%d %H:%M:%S UTC')

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
        memory_content = meta_block + f"\nNote: Content not extracted (binary/media file stored as metadata)."

    # ── Save memory immediately ────────────────────────────────────────────────
    memory_title = f"[{category.capitalize()}] {filename}"
    tags         = f"upload,{category},{file_ext}" if file_ext else f"upload,{category}"

    import json as _json
    metadata_json = _json.dumps({
        "filename": filename,
        "file_size_bytes": file_size,
        "file_size_human": size_str,
        "file_type": category,
        "file_extension": file_ext,
        "upload_timestamp": upload_ts_str,
        "has_text": bool(extracted_text),
    })

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

