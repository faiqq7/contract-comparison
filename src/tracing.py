"""
Langfuse tracing utilities and helper functions.

This module provides additional utilities for enhanced tracing,
monitoring, and debugging of the contract analysis workflow.
"""

import time
import uuid
from contextlib import contextmanager
from typing import Dict, Any, Optional
from langfuse import Langfuse
from langfuse.decorators import observe


class ContractAnalysisTracer:
    """
    Enhanced tracing utilities for contract analysis workflows.
    
    Provides structured logging, performance monitoring, and
    debugging capabilities with Langfuse integration.
    """
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        """
        Initialize the tracer.
        
        Args:
            langfuse_client: Optional Langfuse client instance
        """
        self.langfuse = langfuse_client or Langfuse()
        self.active_traces = {}
        
    def create_session(self, contract_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new analysis session with structured metadata.
        
        Args:
            contract_id: Unique identifier for the contract being analyzed
            metadata: Optional session metadata
            
        Returns:
            Session ID for tracing
        """
        session_id = f"contract_analysis_{contract_id}_{uuid.uuid4().hex[:8]}"
        
        session_metadata = {
            "contract_id": contract_id,
            "session_start": time.time(),
            "workflow_type": "contract_comparison",
            **(metadata or {})
        }
        
        # Initialize session trace
        self.langfuse.trace(
            name="contract_analysis_session",
            session_id=session_id,
            metadata=session_metadata
        )
        
        return session_id
    
    @contextmanager
    def trace_agent_execution(
        self,
        agent_name: str,
        session_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict] = None
    ):
        """
        Context manager for tracing agent execution with timing and error handling.
        
        Args:
            agent_name: Name of the agent being executed
            session_id: Session ID for trace correlation
            input_data: Input data for the agent
            metadata: Additional metadata for the trace
            
        Yields:
            Trace span for the agent execution
        """
        start_time = time.time()
        
        span_metadata = {
            "agent_name": agent_name,
            "start_time": start_time,
            "session_id": session_id,
            **(metadata or {})
        }
        
        span = self.langfuse.trace(
            name=f"agent_{agent_name.lower().replace(' ', '_')}",
            session_id=session_id,
            input=input_data,
            metadata=span_metadata
        )
        
        try:
            yield span
            
            # Success metrics
            end_time = time.time()
            span.update(
                metadata={
                    **span_metadata,
                    "execution_time": end_time - start_time,
                    "status": "success"
                }
            )
            
        except Exception as e:
            # Error tracking
            end_time = time.time()
            span.update(
                metadata={
                    **span_metadata,
                    "execution_time": end_time - start_time,
                    "status": "error",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise
    
    def trace_model_usage(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        session_id: str,
        operation: str,
        metadata: Optional[Dict] = None
    ):
        """
        Track LLM model usage for cost and performance monitoring.
        
        Args:
            model_name: Name of the model used
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            session_id: Session ID for correlation
            operation: Operation type (e.g., "image_parsing", "contextualization")
            metadata: Additional metadata
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # Estimate cost (approximate pricing as of 2024)
        cost_per_1k_tokens = {
            "gpt-4": 0.06,  # Combined input/output average
            "gpt-4o": 0.015,  # Combined input/output average
            "gpt-3.5-turbo": 0.002
        }
        
        estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens.get(model_name, 0.03)
        
        usage_metadata = {
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
            "operation": operation,
            "timestamp": time.time(),
            **(metadata or {})
        }
        
        self.langfuse.trace(
            name="model_usage_tracking",
            session_id=session_id,
            metadata=usage_metadata
        )
    
    def trace_validation_results(
        self,
        session_id: str,
        validation_type: str,
        is_valid: bool,
        issues: list,
        data_size: int,
        metadata: Optional[Dict] = None
    ):
        """
        Track validation results for quality monitoring.
        
        Args:
            session_id: Session ID for correlation
            validation_type: Type of validation performed
            is_valid: Whether validation passed
            issues: List of validation issues found
            data_size: Size of data being validated
            metadata: Additional metadata
        """
        validation_metadata = {
            "validation_type": validation_type,
            "is_valid": is_valid,
            "issue_count": len(issues),
            "issues": issues[:10],  # Limit to prevent large payloads
            "data_size": data_size,
            "timestamp": time.time(),
            **(metadata or {})
        }
        
        self.langfuse.trace(
            name="validation_checkpoint",
            session_id=session_id,
            metadata=validation_metadata
        )
    
    def trace_performance_metrics(
        self,
        session_id: str,
        operation: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict] = None
    ):
        """
        Track performance metrics for monitoring and optimization.
        
        Args:
            session_id: Session ID for correlation
            operation: Operation being measured
            duration: Duration in seconds
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        performance_metadata = {
            "operation": operation,
            "duration_seconds": duration,
            "success": success,
            "timestamp": time.time(),
            **(metadata or {})
        }
        
        # Add performance classification
        if duration < 10:
            performance_metadata["performance_category"] = "fast"
        elif duration < 30:
            performance_metadata["performance_category"] = "normal"
        elif duration < 60:
            performance_metadata["performance_category"] = "slow"
        else:
            performance_metadata["performance_category"] = "very_slow"
        
        self.langfuse.trace(
            name="performance_metrics",
            session_id=session_id,
            metadata=performance_metadata
        )
    
    def create_quality_report(
        self,
        session_id: str,
        analysis_result: Dict[str, Any],
        confidence_scores: Dict[str, float],
        metadata: Optional[Dict] = None
    ):
        """
        Generate quality assessment report for analysis results.
        
        Args:
            session_id: Session ID for correlation
            analysis_result: Complete analysis result
            confidence_scores: Confidence scores from different stages
            metadata: Additional metadata
        """
        # Calculate overall quality metrics
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
        
        sections_count = len(analysis_result.get("sections_changed", []))
        topics_count = len(analysis_result.get("topics_touched", []))
        summary_length = len(analysis_result.get("summary_of_the_change", ""))
        
        quality_metadata = {
            "average_confidence": avg_confidence,
            "confidence_breakdown": confidence_scores,
            "sections_identified": sections_count,
            "topics_identified": topics_count,
            "summary_word_count": len(analysis_result.get("summary_of_the_change", "").split()),
            "summary_character_count": summary_length,
            "timestamp": time.time(),
            **(metadata or {})
        }
        
        # Quality assessment
        quality_flags = []
        if avg_confidence < 0.7:
            quality_flags.append("low_confidence")
        if sections_count == 0:
            quality_flags.append("no_sections_identified")
        if topics_count == 0:
            quality_flags.append("no_topics_identified")
        if summary_length < 100:
            quality_flags.append("insufficient_summary")
        
        quality_metadata["quality_flags"] = quality_flags
        quality_metadata["quality_score"] = 1.0 - (len(quality_flags) * 0.2)  # Simple scoring
        
        self.langfuse.trace(
            name="quality_assessment",
            session_id=session_id,
            metadata=quality_metadata
        )
    
    def finalize_session(
        self,
        session_id: str,
        success: bool,
        total_duration: float,
        final_result: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """
        Finalize analysis session with summary metrics.
        
        Args:
            session_id: Session ID to finalize
            success: Whether the overall analysis succeeded
            total_duration: Total session duration
            final_result: Final analysis result if successful
            error_message: Error message if failed
        """
        summary_metadata = {
            "session_id": session_id,
            "success": success,
            "total_duration": total_duration,
            "end_time": time.time(),
            "result_available": final_result is not None
        }
        
        if error_message:
            summary_metadata["error_message"] = error_message
        
        if final_result:
            summary_metadata.update({
                "sections_changed_count": len(final_result.get("sections_changed", [])),
                "topics_touched_count": len(final_result.get("topics_touched", [])),
                "has_summary": bool(final_result.get("summary_of_the_change")),
                "confidence_score": final_result.get("confidence_score")
            })
        
        self.langfuse.trace(
            name="session_summary",
            session_id=session_id,
            metadata=summary_metadata
        )


# Decorator for automatic function tracing
def trace_function(operation_name: str, session_id_param: str = "session_id"):
    """
    Decorator to automatically trace function execution.
    
    Args:
        operation_name: Name for the operation in traces
        session_id_param: Parameter name that contains session_id
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract session_id from kwargs
            session_id = kwargs.get(session_id_param)
            
            if session_id:
                tracer = ContractAnalysisTracer()
                
                input_data = {
                    "function_name": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
                
                with tracer.trace_agent_execution(
                    operation_name, 
                    session_id, 
                    input_data
                ) as span:
                    result = func(*args, **kwargs)
                    
                    span.update(
                        output={
                            "result_type": type(result).__name__,
                            "success": True
                        }
                    )
                    
                    return result
            else:
                # Execute without tracing if no session_id
                return func(*args, **kwargs)
        
        return wrapper
    return decorator