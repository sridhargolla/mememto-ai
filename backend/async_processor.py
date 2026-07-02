import asyncio
import contextlib
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from retry_utils import retry_with_logging


class ProcessingStatus(str, Enum):
    """Status of document processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingTask:
    """Represents a document processing task."""

    def __init__(self, task_id: str, file_path: str, filename: str, file_type: str):
        self.task_id = task_id
        self.file_path = file_path
        self.filename = filename
        self.file_type = file_type
        self.status = ProcessingStatus.PENDING
        self.result: dict[str, Any] | None = None
        self.error: str | None = None
        self.created_at = datetime.utcnow()
        self.completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "filename": self.filename,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": (self.completed_at.isoformat() if self.completed_at else None),
        }


class AsyncProcessor:
    """Async document processing queue."""

    def __init__(self):
        self.tasks: dict[str, ProcessingTask] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: asyncio.Task | None = None
        self.is_running = False

    async def start(self):
        """Start the background worker."""
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Stop the background worker."""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.worker_task

    async def _worker(self):
        """Background worker to process tasks from queue."""
        while self.is_running:
            try:
                task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                task = self.tasks.get(task_id)

                if task:
                    await self._process_task(task)

                self.queue.task_done()
            except TimeoutError:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    async def _process_task(self, task: ProcessingTask):
        """Process a single task."""
        task.status = ProcessingStatus.PROCESSING

        try:
            # Import here to avoid circular imports
            from database import SessionLocal
            from document_ingestion import DocumentExtractor
            from main import audio_processor, llm
            from memory_service import MemoryService
            from structured_memory_extractor import MemoryExtractorService

            # Extract text with retry logic
            extractor = DocumentExtractor()

            @retry_with_logging(
                max_retries=2,
                initial_delay=1.0,
                backoff_factor=2.0,
                operation_name="Text extraction",
            )
            def extract_with_retry():
                return extractor.extract_text(task.file_path, task.file_type, audio_processor)

            text = extract_with_retry()

            if not text:
                raise RuntimeError(
                    "No text could be extracted from the document. The file may be corrupted or contain no readable text."
                )

            # Extract memories with retry logic (CPU inference can be slow)
            if llm:
                memory_extractor = MemoryExtractorService(llm)

                @retry_with_logging(
                    max_retries=3,
                    initial_delay=2.0,
                    backoff_factor=2.0,
                    operation_name="Memory extraction",
                )
                def extract_memories_with_retry():
                    return memory_extractor.extract_structured_memories(
                        text, source_document=task.filename, max_memories=5
                    )

                memories = extract_memories_with_retry()

                # Store memories in database
                db = SessionLocal()
                try:
                    created_memories = []
                    for memory_schema in memories:
                        memory = MemoryService.create_structured_memory(db, memory_schema)
                        created_memories.append(memory)

                    db.commit()

                    # Convert to dict for storage
                    memory_dicts = [m.dict() for m in memories]
                    task.result = {
                        "memories": memory_dicts,
                        "memories_count": len(memory_dicts),
                        "stored_in_db": True,
                    }
                except Exception as db_error:
                    db.rollback()
                    raise RuntimeError(f"Failed to store memories in database: {db_error!s}")
                finally:
                    db.close()
            else:
                memory_dicts = []
                task.result = {
                    "memories": memory_dicts,
                    "memories_count": 0,
                    "stored_in_db": False,
                    "error": "AI model not loaded",
                }

            task.status = ProcessingStatus.COMPLETED

        except Exception as e:
            task.error = str(e)
            task.status = ProcessingStatus.FAILED
        finally:
            task.completed_at = datetime.utcnow()

            # Clean up temp file
            try:
                if os.path.exists(task.file_path):
                    os.remove(task.file_path)
            except:
                pass

    async def submit_task(self, file_path: str, filename: str, file_type: str) -> str:
        """
        Submit a new processing task.

        Args:
            file_path: Path to the file
            filename: Original filename
            file_type: File type extension

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = ProcessingTask(task_id, file_path, filename, file_type)
        self.tasks[task_id] = task
        await self.queue.put(task_id)
        return task_id

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """
        Get the status of a task.

        Args:
            task_id: Task ID

        Returns:
            Task status dictionary or None
        """
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)

        to_remove = []
        for task_id, task in self.tasks.items():
            if task.completed_at and task.completed_at < cutoff:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]


# Global processor instance
async_processor = AsyncProcessor()
