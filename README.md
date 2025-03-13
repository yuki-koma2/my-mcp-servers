# MCPサーバープロジェクト

このプロジェクトは、Model Context Protocol (MCP) サーバーを複数のサービス（Sentry、GitHub、BrowserBase）に対して構築し、Docker で管理します。

## 概要

以下の MCP サーバーを FastAPI + Docker でセットアップしています：

- **Sentry MCP**
  - エラー情報を取得し解析します。
  - エンドポイント: `/mcp/sentry/errors`
  - ポート: 8000

- **GitHub MCP**
  - GitHubのPRやIssueの情報を取得します。
  - エンドポイント: `/mcp/github/list_prs`, `/mcp/github/list_issues`
  - ポート: 8001

- **BrowserBase MCP**
  - ブラウザをリモートで操作し、Webページをスクレイピング・操作します。
  - エンドポイント: `/mcp/browserbase/open_url`, `/mcp/browserbase/get_title`, `/mcp/browserbase/get_text`, `/mcp/browserbase/screenshot`
  - ポート: 8002

これらのMCPサーバーはそれぞれ独立したDockerコンテナで動作し、docker-composeを使用して一括管理します。

## プロジェクト構造

```
my-mcp-servers/
│── services/
│   ├── sentry_mcp/
│   │   ├── main.py            # FastAPI MCP Server for Sentry integration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.template      # 環境変数テンプレート
│   │   ├── .env               # 実際の環境変数（gitignore対象）
│   ├── github_mcp/
│   │   ├── main.py            # FastAPI MCP Server for GitHub integration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.template      # 環境変数テンプレート
│   │   ├── .env               # 実際の環境変数（gitignore対象）
│   ├── browserbase_mcp/
│   │   ├── main.py            # FastAPI MCP Server for BrowserBase integration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.template      # 環境変数テンプレート
│   │   ├── .env               # 実際の環境変数（gitignore対象）
│── docker-compose.yml
│── README.md
```

## セットアップ手順

### 前提条件

- Docker と docker-compose がインストールされていること
- 各サービス（Sentry、GitHub、BrowserBase）のAPIトークンを取得済みであること

### インストール手順

1. リポジトリをクローンする：
```bash
git clone https://github.com/yourusername/my-mcp-servers.git
cd my-mcp-servers
```

2. 各サービスの環境変数ファイルを設定する：
```bash
# Sentry MCP
cp services/sentry_mcp/.env.template services/sentry_mcp/.env
# 編集して適切なAPIトークンと組織名を設定

# GitHub MCP
cp services/github_mcp/.env.template services/github_mcp/.env
# 編集して適切なAPIトークンを設定

# BrowserBase MCP
cp services/browserbase_mcp/.env.template services/browserbase_mcp/.env
# 編集して適切なAPIトークンを設定
```

3. Docker イメージをビルドして起動する：
```bash
docker-compose build
docker-compose up -d
```

4. サービスが正常に稼働していることを確認する：
```bash
docker-compose ps
```

## APIエンドポイント

### Sentry MCP

- **ヘルスチェック**
  - `GET http://localhost:8000/`
  - レスポンス: `{"status": "ok", "service": "sentry-mcp"}`

- **エラーログの取得**
  - `GET http://localhost:8000/mcp/sentry/errors?project=your_project&limit=10`
  - パラメータ:
    - `project` (オプション): プロジェクト名
    - `limit` (オプション): 取得するエラーの最大数（デフォルト: 10）

### GitHub MCP

- **ヘルスチェック**
  - `GET http://localhost:8001/`
  - レスポンス: `{"status": "ok", "service": "github-mcp"}`

- **プルリクエストの一覧取得**
  - `GET http://localhost:8001/mcp/github/list_prs?owner=octocat&repo=hello-world&state=open`
  - パラメータ:
    - `owner` (必須): リポジトリのオーナー名
    - `repo` (必須): リポジトリ名
    - `state` (オプション): PRの状態（open/closed/all、デフォルト: open）
    - `per_page` (オプション): 1ページあたりの結果数（デフォルト: 30）

- **イシューの一覧取得**
  - `GET http://localhost:8001/mcp/github/list_issues?owner=octocat&repo=hello-world&state=open`
  - パラメータ:
    - `owner` (必須): リポジトリのオーナー名
    - `repo` (必須): リポジトリ名
    - `state` (オプション): イシューの状態（open/closed/all、デフォルト: open）
    - `per_page` (オプション): 1ページあたりの結果数（デフォルト: 30）

### BrowserBase MCP

- **ヘルスチェック**
  - `GET http://localhost:8002/`
  - レスポンス: `{"status": "ok", "service": "browserbase-mcp"}`

- **URLを開く**
  - `GET http://localhost:8002/mcp/browserbase/open_url?url=https://example.com`
  - パラメータ:
    - `url` (必須): 開くURL

- **ページタイトルの取得**
  - `GET http://localhost:8002/mcp/browserbase/get_title`
  - 注意: 先に `open_url` を呼び出してセッションを作成する必要があります

- **要素のテキスト抽出**
  - `GET http://localhost:8002/mcp/browserbase/get_text?selector=.headline`
  - パラメータ:
    - `selector` (必須): テキストを抽出するCSSセレクタ
  - 注意: 先に `open_url` を呼び出してセッションを作成する必要があります

- **スクリーンショット撮影**
  - `GET http://localhost:8002/mcp/browserbase/screenshot?selector=.main-content`
  - パラメータ:
    - `selector` (オプション): スクリーンショットを撮影する特定の要素のCSSセレクタ
  - 注意: 先に `open_url` を呼び出してセッションを作成する必要があります

## トラブルシューティング

- **サービスが起動しない場合**
  - ログを確認: `docker-compose logs sentry-mcp`
  - 環境変数が正しく設定されているか確認
  - ポートの競合がないか確認

- **API呼び出しがエラーを返す場合**
  - APIトークンが有効か確認
  - レート制限に達していないか確認
  - ネットワーク接続を確認

## メンテナンス

- **コンテナの停止**
  ```bash
  docker-compose down
  ```

- **コンテナの再起動**
  ```bash
  docker-compose restart
  ```

- **ログの確認**
  ```bash
  docker-compose logs -f
  ```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
