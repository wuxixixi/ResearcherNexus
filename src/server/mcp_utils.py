# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


async def _get_tools_from_client_session(
    client_context_manager: Any, timeout_seconds: int = 10
) -> List:
    """
    Helper function to get tools from a client session.

    Args:
        client_context_manager: A context manager that returns (read, write) functions
        timeout_seconds: Timeout in seconds for the read operation

    Returns:
        List of available tools from the MCP server

    Raises:
        Exception: If there's an error during the process
    """
    async with client_context_manager as (read, write):
        async with ClientSession(
            read, write, read_timeout_seconds=timedelta(seconds=timeout_seconds)
        ) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            listed_tools = await session.list_tools()
            # Convert Tool objects to dictionaries
            return [tool.model_dump() for tool in listed_tools.tools]


async def load_mcp_tools(
    server_type: str,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    url: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout_seconds: int = 60,  # Longer default timeout for first-time executions
) -> List:
    """
    Load tools from an MCP server.

    Args:
        server_type: The type of MCP server connection (stdio or sse)
        command: The command to execute (for stdio type)
        args: Command arguments (for stdio type)
        url: The URL of the SSE server (for sse type)
        env: Environment variables
        timeout_seconds: Timeout in seconds (default: 60 for first-time executions)

    Returns:
        List of available tools from the MCP server, or empty list if loading fails

    Raises:
        HTTPException: If there's a configuration error (not a runtime error)
    """
    try:
        if server_type == "stdio":
            if not command:
                raise HTTPException(
                    status_code=400, detail="Command is required for stdio type"
                )

            server_params = StdioServerParameters(
                command=command,  # Executable
                args=args,  # Optional command line arguments
                env=env,  # Optional environment variables
            )

            return await _get_tools_from_client_session(
                stdio_client(server_params), timeout_seconds
            )

        elif server_type == "sse":
            if not url:
                raise HTTPException(
                    status_code=400, detail="URL is required for sse type"
                )

            return await _get_tools_from_client_session(
                sse_client(url=url), timeout_seconds
            )

        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported server type: {server_type}"
            )

    except HTTPException:
        # Re-raise configuration errors
        raise
    except NotImplementedError as e:
        # Windows subprocess limitation - try fallback
        logger.warning(f"MCP client failed with NotImplementedError (Windows limitation): {str(e)}")
        logger.info("Attempting Windows compatibility fallback...")
        
        try:
            from .mcp_utils_windows import load_mcp_tools_windows_compatible
            return await load_mcp_tools_windows_compatible(
                server_type, command, args, url, env, timeout_seconds
            )
        except Exception as fallback_error:
            logger.error(f"Windows fallback also failed: {type(fallback_error).__name__}: {str(fallback_error)}")
            return []
    except Exception as e:
        # Log the error with more details for debugging
        import traceback
        error_details = f"Exception type: {type(e).__name__}, Message: '{str(e)}', Traceback: {traceback.format_exc()}"
        logger.warning(f"Failed to load MCP tools: {error_details}. Returning empty tool list.")
        return []
