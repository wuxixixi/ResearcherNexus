# Copyright (c) 2025 SASS and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import json
import logging
import os
from typing import List, Dict, Optional, cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.types import Command

from src.graph.builder import build_graph_with_memory
from src.podcast.graph.builder import build_graph as build_podcast_graph
from src.ppt.graph.builder import build_graph as build_ppt_graph
from src.prose.graph.builder import build_graph as build_prose_graph
from src.server.chat_request import (
    ChatMessage,
    ChatRequest,
    GeneratePodcastRequest,
    GeneratePPTRequest,
    GenerateProseRequest,
    TTSRequest,
)
from src.server.mcp_request import MCPServerMetadataRequest, MCPServerMetadataResponse
from src.server.mcp_utils import load_mcp_tools
from src.tools import VolcengineTTS
from src.server.user_manager import (
    authenticate_user, 
    create_user, 
    update_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user_usage,
    get_user_remaining_usage
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResearcherNexus API",
    description="API for ResearcherNexus",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

graph = build_graph_with_memory()

# 用户模型
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    daily_limit: Optional[int] = None

class UserPassword(BaseModel):
    current_password: str
    new_password: str

# 获取当前用户的依赖项
async def get_current_user(researchernexus_current_user: Optional[str] = Cookie(None)):
    if not researchernexus_current_user:
        raise HTTPException(status_code=401, detail="未认证")
    
    try:
        # 解析Cookie中的用户数据
        user_data = json.loads(researchernexus_current_user)
        # 从数据库中获取最新的用户数据
        user = get_user_by_id(user_data.get('id'))
        
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        return {k: v for k, v in user.items() if k != 'password'}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")

# 检查管理员权限的依赖项
async def check_admin(user: Dict = Depends(get_current_user)):
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user

# 用户认证路由
@app.post("/api/auth/login")
async def login(user_data: UserLogin, response: Response):
    """用户登录"""
    user = authenticate_user(user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 将用户信息设置到Cookie中
    response.set_cookie(
        key="researchernexus_current_user",
        value=json.dumps(user),
        max_age=7 * 24 * 60 * 60,  # 7天过期
        httponly=True,
        secure=os.getenv("APP_ENV") == "production",
        samesite="lax"
    )
    
    return user

@app.post("/api/auth/register")
async def register(user_data: UserRegister, response: Response):
    """用户注册"""
    try:
        # user_manager.create_user 返回包含 id, username, email, role, daily_limit, usage_data, created_at 的字典
        newly_created_user_info = create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )

        # 获取新用户的详细使用情况 {used, limit, remaining}
        # get_user_remaining_usage 会使用 newly_created_user_info 中的 daily_limit
        usage_details = get_user_remaining_usage(newly_created_user_info['id'])

        # 构建返回给前端并设置到 Cookie 的用户对象
        user_for_frontend = {
            "id": newly_created_user_info['id'],
            "username": newly_created_user_info['username'],
            "email": newly_created_user_info['email'],
            "role": newly_created_user_info['role'],
            "created_at": newly_created_user_info['created_at'],
            "usage": usage_details, # {used, limit, remaining}
            # daily_limit 和 usage_data 不需要直接暴露给前端，因为 usage 对象已包含相关信息
        }

        # 将用户信息设置到Cookie中
        response.set_cookie(
            key="researchernexus_current_user",
            value=json.dumps(user_for_frontend),
            max_age=7 * 24 * 60 * 60,  # 7天过期
            httponly=True, # 防止客户端JS访问，更安全
            secure=os.getenv("APP_ENV") == "production", # 仅在HTTPS下发送
            samesite="Lax" # CSRF保护
        )
        
        return user_for_frontend
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/logout")
async def logout(response: Response):
    """用户登出"""
    response.delete_cookie(key="researchernexus_current_user")
    return {"message": "已登出"}

@app.get("/api/users/me")
async def read_users_me(user: Dict = Depends(get_current_user)):
    """获取当前用户信息"""
    # 获取最新的使用情况
    usage = get_user_remaining_usage(user['id'])
    user['usage'] = usage
    return user

@app.post("/api/users/usage")
async def increment_usage(user: Dict = Depends(get_current_user)):
    """增加用户使用次数"""
    result = update_user_usage(user['id'])
    return result

@app.post("/api/users/password")
async def change_password(
    password_data: UserPassword,
    user: Dict = Depends(get_current_user)
):
    """修改用户密码"""
    # 获取完整用户数据，包含密码
    full_user = get_user_by_id(user['id'])
    
    if not full_user or full_user.get('password') != password_data.current_password:
        raise HTTPException(status_code=400, detail="当前密码错误")
    
    try:
        update_user(user['id'], {"password": password_data.new_password})
        return {"message": "密码已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新密码失败: {str(e)}")

# 管理员路由
@app.get("/api/admin/users")
async def admin_get_users(admin: Dict = Depends(check_admin)):
    """管理员获取所有用户"""
    return get_all_users()

@app.put("/api/admin/users/{user_id}")
async def admin_update_user(
    user_id: str,
    user_data: UserUpdate,
    admin: Dict = Depends(check_admin)
):
    """管理员更新用户信息"""
    try:
        updated_user = update_user(user_id, user_data.dict(exclude_unset=True))
        if not updated_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    admin: Dict = Depends(check_admin)
):
    """管理员删除用户"""
    try:
        if admin['id'] == user_id:
            raise HTTPException(status_code=400, detail="不能删除自己的账号")
        
        success = delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {"message": "用户已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 确保在修改chat/stream API之前调用update_user_usage
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, user: Dict = Depends(get_current_user)):
    # 增加使用次数并检查限制
    usage_result = update_user_usage(user['id'])
    if not usage_result['success']:
        # 如果超出使用限制，返回错误消息
        raise HTTPException(status_code=429, detail=usage_result.get('message'))
    
    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())
    return StreamingResponse(
        _astream_workflow_generator(
            request.model_dump()["messages"],
            thread_id,
            request.max_plan_iterations,
            request.max_step_num,
            request.auto_accepted_plan,
            request.interrupt_feedback,
            request.mcp_settings,
            request.enable_background_investigation,
        ),
        media_type="text/event-stream",
    )


async def _astream_workflow_generator(
    messages: List[ChatMessage],
    thread_id: str,
    max_plan_iterations: int,
    max_step_num: int,
    auto_accepted_plan: bool,
    interrupt_feedback: str,
    mcp_settings: dict,
    enable_background_investigation,
):
    input_ = {
        "messages": messages,
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": auto_accepted_plan,
        "enable_background_investigation": enable_background_investigation,
    }
    if not auto_accepted_plan and interrupt_feedback:
        resume_msg = f"[{interrupt_feedback}]"
        # add the last message to the resume message
        if messages:
            resume_msg += f" {messages[-1]['content']}"
        input_ = Command(resume=resume_msg)
    async for agent, _, event_data in graph.astream(
        input_,
        config={
            "thread_id": thread_id,
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "mcp_settings": mcp_settings,
        },
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        if isinstance(event_data, dict):
            if "__interrupt__" in event_data:
                yield _make_event(
                    "interrupt",
                    {
                        "thread_id": thread_id,
                        "id": event_data["__interrupt__"][0].ns[0],
                        "role": "assistant",
                        "content": event_data["__interrupt__"][0].value,
                        "finish_reason": "interrupt",
                        "options": [
                            {"text": "Edit plan", "value": "edit_plan"},
                            {"text": "Start research", "value": "accepted"},
                        ],
                    },
                )
            continue
        message_chunk, message_metadata = cast(
            tuple[AIMessageChunk, dict[str, any]], event_data
        )
        event_stream_message: dict[str, any] = {
            "thread_id": thread_id,
            "agent": agent[0].split(":")[0],
            "id": message_chunk.id,
            "role": "assistant",
            "content": message_chunk.content,
        }
        if message_chunk.response_metadata.get("finish_reason"):
            event_stream_message["finish_reason"] = message_chunk.response_metadata.get(
                "finish_reason"
            )
        if isinstance(message_chunk, ToolMessage):
            # Tool Message - Return the result of the tool call
            event_stream_message["tool_call_id"] = message_chunk.tool_call_id
            yield _make_event("tool_call_result", event_stream_message)
        else:
            # AI Message - Raw message tokens
            if message_chunk.tool_calls:
                # AI Message - Tool Call
                event_stream_message["tool_calls"] = message_chunk.tool_calls
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks
                )
                yield _make_event("tool_calls", event_stream_message)
            elif message_chunk.tool_call_chunks:
                # AI Message - Tool Call Chunks
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks
                )
                yield _make_event("tool_call_chunks", event_stream_message)
            else:
                # AI Message - Raw message tokens
                yield _make_event("message_chunk", event_stream_message)


def _make_event(event_type: str, data: dict[str, any]):
    if data.get("content") == "":
        data.pop("content")
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using volcengine TTS API."""
    try:
        app_id = os.getenv("VOLCENGINE_TTS_APPID", "")
        if not app_id:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_APPID is not set"
            )
        access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")
        if not access_token:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_ACCESS_TOKEN is not set"
            )
        cluster = os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")
        voice_type = os.getenv("VOLCENGINE_TTS_VOICE_TYPE", "BV700_V2_streaming")

        tts_client = VolcengineTTS(
            appid=app_id,
            access_token=access_token,
            cluster=cluster,
            voice_type=voice_type,
        )
        # Call the TTS API
        result = tts_client.text_to_speech(
            text=request.text[:1024],
            encoding=request.encoding,
            speed_ratio=request.speed_ratio,
            volume_ratio=request.volume_ratio,
            pitch_ratio=request.pitch_ratio,
            text_type=request.text_type,
            with_frontend=request.with_frontend,
            frontend_type=request.frontend_type,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=str(result["error"]))

        # Decode the base64 audio data
        audio_data = base64.b64decode(result["audio_data"])

        # Return the audio file
        return Response(
            content=audio_data,
            media_type=f"audio/{request.encoding}",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=tts_output.{request.encoding}"
                )
            },
        )
    except Exception as e:
        logger.exception(f"Error in TTS endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/podcast/generate")
async def generate_podcast(request: GeneratePodcastRequest):
    try:
        report_content = request.content
        print(report_content)
        workflow = build_podcast_graph()
        final_state = workflow.invoke({"input": report_content})
        audio_bytes = final_state["output"]
        return Response(content=audio_bytes, media_type="audio/mp3")
    except Exception as e:
        logger.exception(f"Error occurred during podcast generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ppt/generate")
async def generate_ppt(request: GeneratePPTRequest):
    try:
        report_content = request.content
        print(report_content)
        workflow = build_ppt_graph()
        final_state = workflow.invoke({"input": report_content})
        generated_file_path = final_state["generated_file_path"]
        with open(generated_file_path, "rb") as f:
            ppt_bytes = f.read()
        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    except Exception as e:
        logger.exception(f"Error occurred during ppt generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prose/generate")
async def generate_prose(request: GenerateProseRequest):
    try:
        logger.info(f"Generating prose for prompt: {request.prompt}")
        workflow = build_prose_graph()
        events = workflow.astream(
            {
                "content": request.prompt,
                "option": request.option,
                "command": request.command,
            },
            stream_mode="messages",
            subgraphs=True,
        )
        return StreamingResponse(
            (f"data: {event[0].content}\n\n" async for _, event in events),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.exception(f"Error occurred during prose generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/server/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """Get information about an MCP server."""
    try:
        # Set default timeout with a longer value for this endpoint
        timeout = 300  # Default to 300 seconds for this endpoint

        # Use custom timeout from request if provided
        if request.timeout_seconds is not None:
            timeout = request.timeout_seconds

        # Load tools from the MCP server using the utility function
        tools = await load_mcp_tools(
            server_type=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            timeout_seconds=timeout,
        )

        # Create the response with tools
        response = MCPServerMetadataResponse(
            transport=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            tools=tools,
        )

        return response
    except Exception as e:
        if not isinstance(e, HTTPException):
            logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        raise
