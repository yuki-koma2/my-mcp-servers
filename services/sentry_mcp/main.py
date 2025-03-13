import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

# 環境変数の読み込み
load_dotenv()
SENTRY_API_TOKEN = os.getenv("SENTRY_API_TOKEN")
SENTRY_ORG = os.getenv("SENTRY_ORG")

# Sentryの設定がない場合はエラーを出す
if not SENTRY_API_TOKEN or not SENTRY_ORG:
    raise ValueError("SENTRY_API_TOKEN and SENTRY_ORG must be set in .env file")

app = FastAPI(
    title="Sentry MCP Server",
    description="Model Context Protocol server for Sentry integration",
    version="0.1.0",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# レスポンスモデル
class ErrorResponse(BaseModel):
    id: str
    title: str
    project: str
    level: str
    count: int
    users_count: Optional[int] = None
    last_seen: str
    first_seen: str
    permalink: str

class ErrorsListResponse(BaseModel):
    errors: List[ErrorResponse]

# Sentryクライアントを依存性として注入
async def get_sentry_client():
    async with httpx.AsyncClient(
        base_url="https://sentry.io/api/0/",
        headers={
            "Authorization": f"Bearer {SENTRY_API_TOKEN}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    ) as client:
        yield client

@app.get("/", response_model=Dict[str, str])
async def root():
    return {"status": "ok", "service": "sentry-mcp"}

@app.get("/mcp/sentry/errors", response_model=ErrorsListResponse)
async def get_errors(
    client: httpx.AsyncClient = Depends(get_sentry_client),
    project: Optional[str] = None,
    limit: int = 10
):
    """
    最新のエラーログをSentryから取得します
    """
    try:
        # プロジェクト指定がある場合はURLを変更
        url = f"organizations/{SENTRY_ORG}/issues/"
        params = {"limit": limit}
        
        if project:
            params["project"] = project
            
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        errors = []
        for error in data:
            errors.append(
                ErrorResponse(
                    id=error["id"],
                    title=error["title"],
                    project=error["project"]["slug"],
                    level=error["level"],
                    count=error["count"],
                    users_count=error.get("userCount"),
                    last_seen=error["lastSeen"],
                    first_seen=error["firstSeen"],
                    permalink=error["permalink"],
                )
            )
        
        return {"errors": errors}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Sentry API: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 