import os
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

# 環境変数の読み込み
load_dotenv()
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")

# GitHubの設定がない場合はエラーを出す
if not GITHUB_API_TOKEN:
    raise ValueError("GITHUB_API_TOKEN must be set in .env file")

app = FastAPI(
    title="GitHub MCP Server",
    description="Model Context Protocol server for GitHub integration",
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
class PullRequest(BaseModel):
    id: int
    number: int
    title: str
    state: str
    html_url: str
    created_at: str
    updated_at: str
    user: Dict[str, Any]
    body: Optional[str] = None
    draft: bool
    
class PullRequestList(BaseModel):
    pull_requests: List[PullRequest]
    
class Issue(BaseModel):
    id: int
    number: int
    title: str
    state: str
    html_url: str
    created_at: str
    updated_at: str
    user: Dict[str, Any]
    body: Optional[str] = None
    
class IssueList(BaseModel):
    issues: List[Issue]

# GitHubクライアントを依存性として注入
async def get_github_client():
    async with httpx.AsyncClient(
        base_url="https://api.github.com/",
        headers={
            "Authorization": f"token {GITHUB_API_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=30.0,
    ) as client:
        yield client

@app.get("/", response_model=Dict[str, str])
async def root():
    return {"status": "ok", "service": "github-mcp"}

@app.get("/mcp/github/list_prs", response_model=PullRequestList)
async def list_pull_requests(
    client: httpx.AsyncClient = Depends(get_github_client),
    owner: str = Query(..., description="リポジトリのオーナー"),
    repo: str = Query(..., description="リポジトリ名"),
    state: str = Query("open", description="PRの状態 (open/closed/all)"),
    per_page: int = Query(30, description="1ページあたりの結果数", ge=1, le=100),
):
    """
    指定されたGitHubリポジトリからプルリクエストのリストを取得します
    """
    try:
        response = await client.get(
            f"repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": per_page}
        )
        response.raise_for_status()
        data = response.json()
        
        pull_requests = []
        for pr in data:
            pull_requests.append(
                PullRequest(
                    id=pr["id"],
                    number=pr["number"],
                    title=pr["title"],
                    state=pr["state"],
                    html_url=pr["html_url"],
                    created_at=pr["created_at"],
                    updated_at=pr["updated_at"],
                    user=pr["user"],
                    body=pr.get("body"),
                    draft=pr["draft"],
                )
            )
            
        return {"pull_requests": pull_requests}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to GitHub API: {str(e)}")

@app.get("/mcp/github/list_issues", response_model=IssueList)
async def list_issues(
    client: httpx.AsyncClient = Depends(get_github_client),
    owner: str = Query(..., description="リポジトリのオーナー"),
    repo: str = Query(..., description="リポジトリ名"),
    state: str = Query("open", description="イシューの状態 (open/closed/all)"),
    per_page: int = Query(30, description="1ページあたりの結果数", ge=1, le=100),
):
    """
    指定されたGitHubリポジトリからイシューのリストを取得します
    """
    try:
        response = await client.get(
            f"repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page}
        )
        response.raise_for_status()
        data = response.json()
        
        issues = []
        for issue in data:
            # PRはイシューとしても返されるので、PRでないものだけ追加
            if "pull_request" not in issue:
                issues.append(
                    Issue(
                        id=issue["id"],
                        number=issue["number"],
                        title=issue["title"],
                        state=issue["state"],
                        html_url=issue["html_url"],
                        created_at=issue["created_at"],
                        updated_at=issue["updated_at"],
                        user=issue["user"],
                        body=issue.get("body"),
                    )
                )
            
        return {"issues": issues}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to GitHub API: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 