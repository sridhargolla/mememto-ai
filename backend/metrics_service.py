import time
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from models import PerformanceMetrics
from system_monitor import SystemMonitor


class MetricsService:
    """Service for tracking and storing performance metrics locally."""
    
    def __init__(self, db: Session):
        """
        Initialize the metrics service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def record_metric(
        self,
        metric_type: str,
        duration_seconds: float,
        metric_name: Optional[str] = None,
        memory_usage_mb: Optional[float] = None,
        cpu_usage_percent: Optional[float] = None,
        tokens_generated: Optional[int] = None,
        tokens_per_second: Optional[float] = None,
        document_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> PerformanceMetrics:
        """
        Record a performance metric.
        
        Args:
            metric_type: Type of metric (model_load, inference, document_process)
            duration_seconds: Duration of the operation
            metric_name: Name of the metric (e.g., model name)
            memory_usage_mb: Memory usage during operation
            cpu_usage_percent: CPU usage during operation
            tokens_generated: Number of tokens generated (for inference)
            tokens_per_second: Tokens per second (for inference)
            document_count: Number of documents processed
            metadata: Additional metadata as dictionary
            user_id: User ID if metric is user-specific
        
        Returns:
            Created PerformanceMetrics object
        """
        import json
        
        metric = PerformanceMetrics(
            metric_type=metric_type,
            metric_name=metric_name,
            duration_seconds=duration_seconds,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            tokens_generated=tokens_generated,
            tokens_per_second=tokens_per_second,
            document_count=document_count,
            metadata_json=json.dumps(metadata) if metadata else None,
            user_id=user_id
        )
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        
        return metric
    
    def record_model_load(
        self,
        model_name: str,
        duration_seconds: float,
        user_id: Optional[int] = None
    ) -> PerformanceMetrics:
        """
        Record model loading time.
        
        Args:
            model_name: Name of the model loaded
            duration_seconds: Time taken to load
            user_id: User ID
        
        Returns:
            Created PerformanceMetrics object
        """
        # Get current memory usage
        memory_info = SystemMonitor.get_memory_usage()
        
        return self.record_metric(
            metric_type="model_load",
            metric_name=model_name,
            duration_seconds=duration_seconds,
            memory_usage_mb=memory_info['rss_mb'],
            user_id=user_id
        )
    
    def record_inference(
        self,
        model_name: str,
        duration_seconds: float,
        tokens_generated: int,
        user_id: Optional[int] = None
    ) -> PerformanceMetrics:
        """
        Record inference metrics.
        
        Args:
            model_name: Name of the model used
            duration_seconds: Time taken for inference
            tokens_generated: Number of tokens generated
            user_id: User ID
        
        Returns:
            Created PerformanceMetrics object
        """
        # Get current system metrics
        memory_info = SystemMonitor.get_memory_usage()
        cpu_info = SystemMonitor.get_cpu_usage()
        
        tokens_per_second = tokens_generated / duration_seconds if duration_seconds > 0 else 0
        
        return self.record_metric(
            metric_type="inference",
            metric_name=model_name,
            duration_seconds=duration_seconds,
            memory_usage_mb=memory_info['rss_mb'],
            cpu_usage_percent=cpu_info['percent'],
            tokens_generated=tokens_generated,
            tokens_per_second=tokens_per_second,
            user_id=user_id
        )
    
    def record_document_process(
        self,
        document_count: int,
        duration_seconds: float,
        user_id: Optional[int] = None
    ) -> PerformanceMetrics:
        """
        Record document processing metrics.
        
        Args:
            document_count: Number of documents processed
            duration_seconds: Time taken
            user_id: User ID
        
        Returns:
            Created PerformanceMetrics object
        """
        # Get current system metrics
        memory_info = SystemMonitor.get_memory_usage()
        cpu_info = SystemMonitor.get_cpu_usage()
        
        return self.record_metric(
            metric_type="document_process",
            duration_seconds=duration_seconds,
            document_count=document_count,
            memory_usage_mb=memory_info['rss_mb'],
            cpu_usage_percent=cpu_info['percent'],
            user_id=user_id
        )
    
    def get_metrics(
        self,
        metric_type: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[PerformanceMetrics]:
        """
        Retrieve metrics with optional filtering.
        
        Args:
            metric_type: Filter by metric type
            user_id: Filter by user ID
            limit: Maximum number of records to return
        
        Returns:
            List of PerformanceMetrics objects
        """
        query = self.db.query(PerformanceMetrics)
        
        if metric_type:
            query = query.filter(PerformanceMetrics.metric_type == metric_type)
        
        if user_id:
            query = query.filter(PerformanceMetrics.user_id == user_id)
        
        return query.order_by(PerformanceMetrics.timestamp.desc()).limit(limit).all()
    
    def get_aggregated_metrics(
        self,
        metric_type: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics for a metric type.
        
        Args:
            metric_type: Type of metric to aggregate
            user_id: Filter by user ID
        
        Returns:
            Dictionary with aggregated statistics
        """
        from sqlalchemy import func
        
        query = self.db.query(
            func.count(PerformanceMetrics.id).label('count'),
            func.avg(PerformanceMetrics.duration_seconds).label('avg_duration'),
            func.min(PerformanceMetrics.duration_seconds).label('min_duration'),
            func.max(PerformanceMetrics.duration_seconds).label('max_duration'),
            func.avg(PerformanceMetrics.memory_usage_mb).label('avg_memory'),
            func.avg(PerformanceMetrics.cpu_usage_percent).label('avg_cpu')
        )
        
        query = query.filter(PerformanceMetrics.metric_type == metric_type)
        
        if user_id:
            query = query.filter(PerformanceMetrics.user_id == user_id)
        
        result = query.first()
        
        if result:
            return {
                'count': result.count,
                'avg_duration': float(result.avg_duration) if result.avg_duration else 0,
                'min_duration': float(result.min_duration) if result.min_duration else 0,
                'max_duration': float(result.max_duration) if result.max_duration else 0,
                'avg_memory_mb': float(result.avg_memory) if result.avg_memory else 0,
                'avg_cpu_percent': float(result.avg_cpu) if result.avg_cpu else 0
            }
        
        return {
            'count': 0,
            'avg_duration': 0,
            'min_duration': 0,
            'max_duration': 0,
            'avg_memory_mb': 0,
            'avg_cpu_percent': 0
        }
    
    def get_recent_inference_stats(
        self,
        user_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent inference statistics.
        
        Args:
            user_id: Filter by user ID
            limit: Number of recent records
        
        Returns:
            List of dictionaries with inference stats
        """
        metrics = self.get_metrics(metric_type="inference", user_id=user_id, limit=limit)
        
        return [
            {
                'timestamp': m.timestamp.isoformat(),
                'duration_seconds': m.duration_seconds,
                'tokens_generated': m.tokens_generated,
                'tokens_per_second': m.tokens_per_second,
                'memory_usage_mb': m.memory_usage_mb,
                'cpu_usage_percent': m.cpu_usage_percent
            }
            for m in metrics
        ]
    
    def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """
        Delete metrics older than specified days.
        
        Args:
            days_to_keep: Number of days to keep
        
        Returns:
            Number of records deleted
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted = self.db.query(PerformanceMetrics).filter(
            PerformanceMetrics.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        
        return deleted
