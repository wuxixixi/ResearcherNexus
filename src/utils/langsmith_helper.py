"""
LangSmith helper module for accessing trace data and analytics.
"""

import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from langsmith import Client

from src.config.langsmith import LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

logger = logging.getLogger(__name__)


def get_langsmith_client() -> Optional[Client]:
    """
    Get a LangSmith client instance.
    
    Returns:
        Client instance if API key is available, None otherwise
    """
    if not LANGCHAIN_API_KEY:
        logger.warning("LangSmith API key not set. Cannot create client.")
        return None
    
    return Client(api_key=LANGCHAIN_API_KEY)


def get_recent_runs(
    days: int = 1, 
    project_name: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get recent runs from LangSmith.
    
    Args:
        days: Number of days to look back
        project_name: Project name to filter by (defaults to LANGCHAIN_PROJECT)
        limit: Maximum number of runs to return
        
    Returns:
        List of run data dictionaries
    """
    client = get_langsmith_client()
    if not client:
        return []
    
    project = project_name or LANGCHAIN_PROJECT
    
    # Calculate the start time
    start_time = datetime.now() - timedelta(days=days)
    
    try:
        runs = client.list_runs(
            project_name=project,
            start_time=start_time,
            limit=limit
        )
        return list(runs)
    except Exception as e:
        logger.error(f"Error fetching runs from LangSmith: {e}")
        return []


def get_run_details(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific run.
    
    Args:
        run_id: The LangSmith run ID
        
    Returns:
        Run details dictionary or None if not found
    """
    client = get_langsmith_client()
    if not client:
        return None
    
    try:
        return client.read_run(run_id)
    except Exception as e:
        logger.error(f"Error fetching run details from LangSmith: {e}")
        return None


def get_run_children(run_id: str) -> List[Dict[str, Any]]:
    """
    Get child runs for a parent run.
    
    Args:
        run_id: The parent run ID
        
    Returns:
        List of child run dictionaries
    """
    client = get_langsmith_client()
    if not client:
        return []
    
    try:
        return list(client.list_runs(parent_run_id=run_id))
    except Exception as e:
        logger.error(f"Error fetching child runs from LangSmith: {e}")
        return []


def get_project_stats(
    project_name: Optional[str] = None,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get aggregated statistics for a project.
    
    Args:
        project_name: Project name (defaults to LANGCHAIN_PROJECT)
        days: Number of days to include in stats
        
    Returns:
        Dictionary with project statistics
    """
    runs = get_recent_runs(days=days, project_name=project_name)
    
    if not runs:
        return {
            "total_runs": 0,
            "avg_latency": 0,
            "success_rate": 0,
            "error_count": 0
        }
    
    total_runs = len(runs)
    total_latency = 0
    error_count = 0
    
    for run in runs:
        # Sum up latencies
        start_time = run.get("start_time")
        end_time = run.get("end_time")
        
        if start_time and end_time:
            latency = (end_time - start_time).total_seconds()
            total_latency += latency
        
        # Count errors
        if run.get("error"):
            error_count += 1
    
    avg_latency = total_latency / total_runs if total_runs > 0 else 0
    success_rate = (total_runs - error_count) / total_runs * 100 if total_runs > 0 else 0
    
    return {
        "total_runs": total_runs,
        "avg_latency": round(avg_latency, 2),
        "success_rate": round(success_rate, 2),
        "error_count": error_count
    } 