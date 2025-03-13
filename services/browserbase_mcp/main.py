import os
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, AnyUrl

# 環境変数の読み込み
load_dotenv()
BROWSERBASE_API_TOKEN = os.getenv("BROWSERBASE_API_TOKEN")

# BrowserBaseの設定がない場合はエラーを出す
if not BROWSERBASE_API_TOKEN:
    raise ValueError("BROWSERBASE_API_TOKEN must be set in .env file")

app = FastAPI(
    title="BrowserBase MCP Server",
    description="Model Context Protocol server for browser automation and web scraping",
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
class BrowserResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# BrowserBaseクライアントを依存性として注入
async def get_browserbase_client():
    async with httpx.AsyncClient(
        base_url="https://api.browserbase.com/",  # 仮のAPIエンドポイント
        headers={
            "Authorization": f"Bearer {BROWSERBASE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        timeout=60.0,  # ブラウザ操作は時間がかかることがあるため長めのタイムアウト
    ) as client:
        yield client

# セッション管理用の簡易的なクラス (実際の実装ではRedisやDBを使用)
class BrowserSessionManager:
    def __init__(self):
        self.current_session = None
        self.current_url = None
        
    def set_session(self, session_id):
        self.current_session = session_id
        
    def get_session(self):
        return self.current_session
        
    def set_url(self, url):
        self.current_url = url
        
    def get_url(self):
        return self.current_url

# グローバルなセッション管理インスタンス
browser_session = BrowserSessionManager()

@app.get("/", response_model=Dict[str, str])
async def root():
    return {"status": "ok", "service": "browserbase-mcp"}

@app.get("/mcp/browserbase/open_url", response_model=BrowserResponse)
async def open_url(
    url: AnyUrl = Query(..., description="開くURL"),
    client: httpx.AsyncClient = Depends(get_browserbase_client),
):
    """
    指定されたURLをブラウザで開きます
    """
    try:
        # 実際のAPIリクエストを送信（仮実装）
        response = await client.post(
            "browser/open",
            json={"url": str(url)}
        )
        response.raise_for_status()
        data = response.json()
        
        # セッション情報を保存
        if data.get("session_id"):
            browser_session.set_session(data["session_id"])
        browser_session.set_url(str(url))
        
        return {
            "success": True,
            "message": f"URLを開きました: {url}",
            "data": data
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ブラウザでURLを開く際にエラーが発生しました: {str(e)}")

@app.get("/mcp/browserbase/get_title", response_model=BrowserResponse)
async def get_title(
    client: httpx.AsyncClient = Depends(get_browserbase_client),
):
    """
    現在開いているページのタイトルを取得します
    """
    try:
        # セッションチェック
        session_id = browser_session.get_session()
        if not session_id:
            raise HTTPException(status_code=400, detail="アクティブなブラウザセッションがありません")
            
        # 実際のAPIリクエストを送信（仮実装）
        response = await client.get(
            "browser/title",
            params={"session_id": session_id}
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "message": "ページタイトルを取得しました",
            "data": {"title": data.get("title", "")}
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ページタイトルの取得中にエラーが発生しました: {str(e)}")

@app.get("/mcp/browserbase/get_text", response_model=BrowserResponse)
async def get_text(
    selector: str = Query(..., description="テキストを抽出するCSSセレクタ"),
    client: httpx.AsyncClient = Depends(get_browserbase_client),
):
    """
    指定されたセレクタに一致する要素からテキストを抽出します
    """
    try:
        # セッションチェック
        session_id = browser_session.get_session()
        if not session_id:
            raise HTTPException(status_code=400, detail="アクティブなブラウザセッションがありません")
            
        # 実際のAPIリクエストを送信（仮実装）
        response = await client.get(
            "browser/text",
            params={"session_id": session_id, "selector": selector}
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "message": f"セレクタ '{selector}' からテキストを抽出しました",
            "data": {"text": data.get("text", "")}
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テキスト抽出中にエラーが発生しました: {str(e)}")

@app.get("/mcp/browserbase/screenshot", response_model=BrowserResponse)
async def take_screenshot(
    client: httpx.AsyncClient = Depends(get_browserbase_client),
    selector: Optional[str] = Query(None, description="スクリーンショットを撮影する特定の要素のCSSセレクタ"),
):
    """
    現在のページのスクリーンショットを撮影します
    """
    try:
        # セッションチェック
        session_id = browser_session.get_session()
        if not session_id:
            raise HTTPException(status_code=400, detail="アクティブなブラウザセッションがありません")
            
        # 実際のAPIリクエストを送信（仮実装）
        params = {"session_id": session_id}
        if selector:
            params["selector"] = selector
            
        response = await client.get(
            "browser/screenshot",
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "message": "スクリーンショットを撮影しました",
            "data": {"image_url": data.get("image_url", "")}
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"スクリーンショット撮影中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 