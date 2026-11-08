import asyncio
import json
from typing import Any
from pydantic import BaseModel, Field
from fastapi import FastAPI
from async_demo.demo_function_call_async import function_call
from async_demo.demo_json_async import handle_request_with_timeout

app = FastAPI()
tool_semaphore = asyncio.Semaphore(2)


@app.get("/")
async def health():
    return {"message": "Health check passed"}

class ToolRequest(BaseModel):
    name: str = Field(min_length=1)
    arguments: dict[str, Any]

@app.post("/tools/preview")
async def preview_tool(request: ToolRequest):
    return {
        "status": "received",
        "name": request.name, 
        "arguments": request.arguments
    }

@app.post("/tools/execute")
async def execute_tool(request: ToolRequest):
    return await function_call(request.name, request.arguments)

@app.post("/tools/execute_with_timeout")
async def execute_tool_with_timeout(request: ToolRequest):
    return await handle_request_with_timeout(
        json.dumps(request.model_dump(), ensure_ascii=False),
        tool_semaphore,
    )
