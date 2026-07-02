"""
Progress Tracker Module
Provides user-facing progress updates during chat processing.
"""

from collections.abc import AsyncGenerator
from enum import Enum


class ProcessingStage(Enum):
    """Processing stages for user-facing progress updates."""

    UNDERSTANDING = "understanding"
    SEARCHING_MEMORIES = "searching_memories"
    READING_DOCUMENTS = "reading_documents"
    FINDING_INFO = "finding_info"
    BUILDING_CONTEXT = "building_context"
    RUNNING_AI = "running_ai"
    GENERATING_RESPONSE = "generating_response"
    FORMATTING_ANSWER = "formatting_answer"
    DONE = "done"


class ProgressTracker:
    """
    Tracks and emits progress updates during chat processing.
    Provides user-friendly status messages.
    """

    STAGE_MESSAGES = {
        ProcessingStage.UNDERSTANDING: "🧠 Understanding your request...",
        ProcessingStage.SEARCHING_MEMORIES: "🔍 Searching memories...",
        ProcessingStage.READING_DOCUMENTS: "📄 Reading uploaded documents...",
        ProcessingStage.FINDING_INFO: "📚 Finding relevant information...",
        ProcessingStage.BUILDING_CONTEXT: "🧩 Building context...",
        ProcessingStage.RUNNING_AI: "🤖 Running local AI...",
        ProcessingStage.GENERATING_RESPONSE: "✍️ Generating response...",
        ProcessingStage.FORMATTING_ANSWER: "✨ Formatting answer...",
        ProcessingStage.DONE: "✅ Done",
    }

    def __init__(self):
        self.current_stage: ProcessingStage | None = None
        self.progress: float = 0.0
        self.details: str | None = None

    async def emit_progress(
        self,
        stage: ProcessingStage,
        progress: float | None = None,
        details: str | None = None,
    ) -> dict:
        """
        Emit a progress update.

        Args:
            stage: Current processing stage
            progress: Progress percentage (0-100)
            details: Additional details about current operation

        Returns:
            Progress update dictionary
        """
        self.current_stage = stage
        if progress is not None:
            self.progress = progress
        else:
            # Auto-calculate progress based on stage
            self.progress = self._calculate_stage_progress(stage)

        self.details = details

        return {
            "type": "progress",
            "stage": stage.value,
            "message": self.STAGE_MESSAGES[stage],
            "progress": self.progress,
            "details": details,
        }

    def _calculate_stage_progress(self, stage: ProcessingStage) -> float:
        """Calculate progress percentage based on stage."""
        stage_order = list(ProcessingStage)
        stage_index = stage_order.index(stage)
        return (stage_index / len(stage_order)) * 100

    async def emit_streaming_start(self) -> dict:
        """Emit initial streaming start signal."""
        return {"type": "streaming_start", "message": "Memento AI is thinking..."}

    async def emit_streaming_end(self) -> dict:
        """Emit streaming end signal."""
        return {"type": "streaming_end", "message": "Response complete"}


class AsyncProgressEmitter:
    """
    Async generator that yields progress updates during processing.
    """

    def __init__(self):
        self.tracker = ProgressTracker()

    async def emit_processing_pipeline(
        self, has_memories: bool = True, has_documents: bool = False
    ) -> AsyncGenerator[dict, None]:
        """
        Emit progress updates for the full processing pipeline.

        Args:
            has_memories: Whether user has memories to search
            has_documents: Whether user has documents to read

        Yields:
            Progress update dictionaries
        """
        # Stage 1: Understanding
        yield await self.tracker.emit_progress(ProcessingStage.UNDERSTANDING)

        # Stage 2: Searching memories (if applicable)
        if has_memories:
            yield await self.tracker.emit_progress(ProcessingStage.SEARCHING_MEMORIES)

        # Stage 3: Reading documents (if applicable)
        if has_documents:
            yield await self.tracker.emit_progress(ProcessingStage.READING_DOCUMENTS)
            yield await self.tracker.emit_progress(ProcessingStage.FINDING_INFO)

        # Stage 4: Building context
        if has_memories or has_documents:
            yield await self.tracker.emit_progress(ProcessingStage.BUILDING_CONTEXT)

        # Stage 5: Running AI
        yield await self.tracker.emit_progress(ProcessingStage.RUNNING_AI)

        # Stage 6: Generating response
        yield await self.tracker.emit_progress(ProcessingStage.GENERATING_RESPONSE)

        # Stage 7: Formatting
        yield await self.tracker.emit_progress(ProcessingStage.FORMATTING_ANSWER)

        # Stage 8: Done
        yield await self.tracker.emit_progress(ProcessingStage.DONE)

    async def emit_custom_progress(self, message: str, progress: float) -> dict:
        """Emit a custom progress update."""
        return {"type": "progress", "message": message, "progress": progress}


class ProcessingTimeline:
    """
    Manages the complete processing timeline with detailed stages.
    """

    def __init__(self):
        self.stages_completed = []
        self.current_stage = None
        self.start_time = None
        self.stage_times = {}

    def start(self):
        """Start the processing timeline."""
        import time

        self.start_time = time.time()

    def complete_stage(self, stage_name: str):
        """Mark a stage as completed."""
        import time

        if self.start_time:
            elapsed = time.time() - self.start_time
            self.stage_times[stage_name] = elapsed
        self.stages_completed.append(stage_name)

    def get_summary(self) -> dict:
        """Get a summary of the processing timeline."""
        import time

        total_time = time.time() - self.start_time if self.start_time else 0

        return {
            "stages_completed": self.stages_completed,
            "stage_times": self.stage_times,
            "total_time": total_time,
            "current_stage": self.current_stage,
        }

    def get_progress_percentage(self, total_stages: int) -> float:
        """Calculate progress percentage based on completed stages."""
        if total_stages == 0:
            return 0.0
        return (len(self.stages_completed) / total_stages) * 100
