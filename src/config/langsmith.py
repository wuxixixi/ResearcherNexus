"""
LangSmith configuration module for the ResearcherNexus project.
This module provides utilities for initializing and managing LangSmith tracing.
"""

import os
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# LangSmith configuration
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "ResearchNexus")
LANGCHAIN_TRACING = os.getenv("LANGCHAIN_TRACING", "true").lower() == "true"
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# Additional optional settings
LANGCHAIN_TAGS = os.getenv("LANGCHAIN_TAGS", "").split(",") if os.getenv("LANGCHAIN_TAGS") else []


def init_langsmith():
    """
    Initialize LangSmith tracing.
    This function should be called at the application startup.
    """
    if not LANGCHAIN_API_KEY:
        logger.warning("LANGCHAIN_API_KEY not set. LangSmith tracing will be disabled.")
        return False
    
    # Set environment variables for LangChain/LangGraph to use
    os.environ["LANGCHAIN_TRACING"] = str(LANGCHAIN_TRACING).lower()
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
    
    # Only set API key in environment if it's available
    if LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    
    logger.info(f"LangSmith tracing {'enabled' if LANGCHAIN_TRACING else 'disabled'} for project: {LANGCHAIN_PROJECT}")
    return LANGCHAIN_TRACING


def create_run_tags(additional_tags: Optional[list] = None) -> list:
    """
    Create a list of tags for a LangSmith run.
    
    Args:
        additional_tags: Additional tags to include in the run
        
    Returns:
        List of tags for the run
    """
    tags = LANGCHAIN_TAGS.copy()
    if additional_tags:
        tags.extend(additional_tags)
    return tags


def create_run_metadata(metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create metadata for a LangSmith run.
    
    Args:
        metadata: Additional metadata to include in the run
        
    Returns:
        Dictionary of metadata for the run
    """
    base_metadata = {
        "environment": os.getenv("APP_ENV", "development"),
    }
    
    if metadata:
        base_metadata.update(metadata)
    
    return base_metadata 