import os
import tempfile
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
from dotenv import load_dotenv
from model_wrapper import LocalLLM
from database import init_db, get_db
from models import Memory, Conversation
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
from sqlalchemy.orm import Session
from models import User

# Load environment variables
load_dotenv()

app = FastAPI(title="Memento AI Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

try:
    llm = LocalLLM(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads)
    print(f"Model loaded successfully from {model_path}")
except Exception as e:
    print(f"Warning: Failed to load model: {e}")
    print("The /chat endpoint will return an error message.")


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


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
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
    created_at: str
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
    timestamp: str

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
        "offline": True
    }



# Authentication endpoints
@app.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = create_user(db, user_data.name, user_data.email, user_data.password)
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
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
        offline=True
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
    test_prompt = "Hello"
    
    if llm:
        try:
            llm.generate(test_prompt, max_tokens=10, temperature=0.7)
        except:
            pass
    
    response_time = time.time() - start_time
    
    # Get system metrics
    memory_info = SystemMonitor.get_memory_usage()
    cpu_info = SystemMonitor.get_cpu_usage()
    cache_stats = response_cache.get_stats()
    
    return BenchmarkResult(
        model=model_name,
        response_time=response_time,
        memory_usage_mb=memory_info['rss_mb'],
        cpu_usage_percent=cpu_info['percent'],
        cache_stats=cache_stats
    )


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
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if llm is None:
        async def error_stream():
            yield f"data: {json.dumps({'error': 'Model not loaded. Please check the model path and try again.'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    async def stream_response():
        try:
            # Retrieve relevant memories using Hybrid Search (filtered by user)
            retriever = MemoryRetriever()
            relevant_memories = retriever.retrieve_hybrid(db, request.message, top_k=3, user_id=current_user.id)
            
            # Build context from retrieved memories
            context = retriever.format_context(relevant_memories)
            
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
                # Augment prompt with context and history
                augmented_prompt = f"""You are a helpful offline personal memory assistant. Answer the user's question based on the retrieved context below.
If the answer cannot be found in the context, use your general knowledge but mention it is not in your personal memories.

Retrieved Context:
{context}

Recent Conversation History:
{history_str}
User question: {request.message}

Answer:"""
                stream = llm.generate_stream(augmented_prompt, max_tokens=512, temperature=0.7)
            else:
                # No relevant memories found, use chat history prompt
                chat_prompt = f"""You are a helpful offline personal memory assistant.
                
Recent Conversation History:
{history_str}
User question: {request.message}

Answer:"""
                stream = llm.generate_stream(chat_prompt, max_tokens=512, temperature=0.7)
            
            # Stream tokens
            full_response = ""
            for token in stream:
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
            
            # Prepare performance metrics
            metrics = {
                "inference_time_seconds": round(llm.last_inference_time, 2),
                "tokens_per_second": round(llm.last_tokens_per_second, 1),
                "memory_usage_mb": round(SystemMonitor.get_memory_usage()['rss_mb'], 1),
                "model": llm.model_path.split("/")[-1] if "/" in llm.model_path else llm.model_path
            }
            
            # Send sources and metrics at the end
            sources_data = [s.dict() for s in sources]
            yield f"data: {json.dumps({'sources': sources_data, 'metrics': metrics, 'done': True})}\n\n"
            
            # Save conversation to database
            ConversationService.create_conversation(db, request.message, full_response, current_user.id)
            
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
async def upload_document_async(file: UploadFile = File(...)):
    """Upload document for async background processing."""
    
    # Get file extension
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    # Validate file type
    supported_types = ['pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'wav', 'mp3']
    if file_extension not in supported_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Supported types: {', '.join(supported_types)}")
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    # Submit to async processor
    task_id = await async_processor.submit_task(temp_file_path, file.filename, file_extension)
    
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


# Document upload endpoint
@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document to extract memories."""
    
    if llm is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Cannot extract memories.")
    
    # Get file extension
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    # Validate file type
    supported_types = ['pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'wav', 'mp3']
    if file_extension not in supported_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Supported types: {', '.join(supported_types)}")
    
    # Save uploaded file to temporary location
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text from document
        extractor = DocumentExtractor()
        text = extractor.extract_text(temp_file_path, file_extension, audio_processor)
        
        if not text:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
        # Extract memories using local LLM with structured extraction
        memory_extractor = MemoryExtractor(llm)
        extracted_memories = memory_extractor.extract_memories(text, source_document=file.filename, max_memories=5)
        
        # Store memories in database using structured extraction
        created_memories = []
        for memory_data in extracted_memories:
            # Use structured memory if available
            if 'structured_data' in memory_data and memory_data['structured_data']:
                memory = MemoryService.create_structured_memory(db, memory_data['structured_data'], current_user.id)
            else:
                # Fallback to legacy format
                memory = MemoryService.create_memory(
                    db,
                    title=memory_data['title'],
                    content=memory_data['content'],
                    tags=memory_data['tags'],
                    source_document=memory_data.get('source_document'),
                    user_id=current_user.id
                )
            created_memories.append(memory)
        
        return DocumentUploadResponse(
            message=f"Successfully processed document. Extracted {len(created_memories)} memories.",
            memories_created=len(created_memories),
            memories=created_memories
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
