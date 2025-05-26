# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import json
import logging
import os
import platform
import subprocess
from datetime import timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def load_mcp_tools_windows_compatible(
    server_type: str,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    url: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout_seconds: int = 60,
) -> List:
    """
    Windows兼容的MCP工具加载器
    
    当标准MCP客户端在Windows上失败时，使用此备用方法
    """
    try:
        if server_type == "stdio":
            if not command:
                raise HTTPException(
                    status_code=400, detail="Command is required for stdio type"
                )
            
            # 对于Windows环境，使用同步subprocess然后包装为异步
            return await _load_tools_subprocess_fallback(command, args, env, timeout_seconds)
        
        elif server_type == "sse":
            # SSE类型通常不受Windows subprocess限制影响
            raise HTTPException(
                status_code=400, detail="SSE type not implemented in Windows fallback"
            )
        
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported server type: {server_type}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Windows fallback MCP loader failed: {type(e).__name__}: {str(e)}")
        return []


async def _load_tools_subprocess_fallback(
    command: str, 
    args: Optional[List[str]], 
    env: Optional[Dict[str, str]], 
    timeout_seconds: int
) -> List:
    """
    使用同步subprocess作为Windows环境的备用方案
    """
    try:
        # 构建完整命令
        full_command = [command]
        if args:
            full_command.extend(args)
        
        logger.info(f"Windows fallback: Running command {' '.join(full_command)}")
        
        # 在线程池中运行同步subprocess
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            _run_mcp_server_sync, 
            full_command, 
            env, 
            timeout_seconds
        )
        
        if result:
            return result
        else:
            logger.warning("Windows fallback: No tools returned from MCP server")
            return []
            
    except Exception as e:
        logger.error(f"Windows fallback subprocess failed: {type(e).__name__}: {str(e)}")
        return []


def _run_mcp_server_sync(command_list: List[str], env: Optional[Dict[str, str]], timeout: int) -> List:
    """
    同步运行MCP服务器并尝试获取工具列表
    这是一个简化的实现，用于Windows兼容性
    """
    try:
        # 设置环境变量
        process_env = dict(os.environ) if env else None
        if env and process_env:
            process_env.update(env)
        
        # 运行命令并获取输出
        logger.info(f"Executing: {' '.join(command_list)}")
        
        # 对于MCP服务器，我们需要与其进行JSON-RPC通信
        # 这里实现一个简化版本
        process = subprocess.Popen(
            command_list,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=process_env,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "ResearcherNexus",
                    "version": "1.0.0"
                }
            }
        }
        
        # 发送请求
        request_str = json.dumps(init_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # 读取响应（简化版本）
        try:
            stdout, stderr = process.communicate(timeout=min(timeout, 30))
            
            if process.returncode == 0:
                # 尝试解析输出中的工具信息
                # 这是一个简化的解析，实际MCP协议更复杂
                logger.info(f"MCP server output: {stdout[:200]}...")
                
                # 返回一个模拟的工具列表，表示服务器可用
                return [{
                    "name": "mcp_tool_placeholder",
                    "description": f"MCP tool from {command_list[0]} (Windows compatibility mode)",
                    "inputSchema": {"type": "object", "properties": {}}
                }]
            else:
                logger.warning(f"MCP server failed with return code {process.returncode}: {stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            process.kill()
            logger.warning(f"MCP server timed out after {timeout} seconds")
            return []
            
    except Exception as e:
        logger.error(f"Sync MCP execution failed: {type(e).__name__}: {str(e)}")
        return []


# 检测是否需要使用Windows兼容模式
def should_use_windows_fallback() -> bool:
    """
    检测是否应该使用Windows兼容模式
    """
    return platform.system() == "Windows" 