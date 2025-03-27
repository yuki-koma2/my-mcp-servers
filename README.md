# Dockerized GitHub MCP Server

GitHubのAPIと連携し、リポジトリのファイル操作、リポジトリ管理、検索機能などを提供するModel Context Protocol（MCP）サーバーをDockerコンテナとして提供します。

## 機能

- **自動ブランチ作成**: ファイル作成/更新時やpush時に、存在しないブランチを自動的に作成
- **包括的なエラーハンドリング**: 一般的な問題に対する明確なエラーメッセージを提供
- **Gitヒストリー保持**: 操作は強制pushを使わず適切なGitヒストリーを維持
- **バッチ操作**: 単一ファイルと複数ファイルの両方の操作をサポート
- **高度な検索**: コード、イシュー/PR、ユーザーの検索をサポート

## セットアップ

### 1. GitHub Personal Access Tokenの準備

1. [GitHub Personal Access Token](https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)を作成します
   - GitHubの設定 > 開発者設定 > Personal access tokenに移動
   - このトークンがアクセスできるリポジトリを選択（Public、All、または特定のリポジトリ）
   - `repo`スコープ（「プライベートリポジトリの完全な制御」）を選択
     - または、公開リポジトリのみを操作する場合は`public_repo`スコープのみを選択
   - 生成されたトークンをコピー

2. `.env`ファイルにトークンを設定:
   ```
   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
   ```

### 2. Dockerによるビルドと起動

#### ビルド手順

```bash
# Dockerイメージのビルド
docker build -t mcp/github -f src/github/Dockerfile .
```

#### 起動手順（docker runの場合）

```bash
docker run -it --rm -e GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN -p 5000:5000 mcp/github
```

#### 複数コンテナ起動（docker-compose）

```bash
# .envファイルを作成してトークンを設定
cp .env.template .env
# 環境変数を編集
nano .env
# 起動
docker-compose up -d
```

これにより、2つの異なるポート（5002と5003）でGitHub MCPサーバーが起動します。
コンテナはttyモードで起動し、stdioインターフェースを通じて通信を待機します。

### 3. Cursorでの使用方法

MCPサーバーは標準入出力（stdio）を介して通信するように設計されています。Cursorと連携するには、`claude_desktop_config.json`に以下の設定を追加してください：

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

この設定により、Cursorが必要なときにだけMCPサーバーを起動し、処理が完了すると自動的に終了します。

## 使用方法

MCPサーバーは、ツール名とその入力パラメータを含むメッセージ形式でリクエストを受け付けます。

### リクエスト例（/respond エンドポイント）

#### ファイルの作成または更新

```bash
curl -X POST http://localhost:5002/respond \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": {
          "tool_name": "create_or_update_file",
          "input": {
            "owner": "your-username",
            "repo": "your-repo",
            "path": "example.txt",
            "content": "Hello, world!",
            "message": "Add example file",
            "branch": "main"
          }
        }
      }
    ]
  }'
```

#### リポジトリ検索

```bash
curl -X POST http://localhost:5002/respond \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": {
          "tool_name": "search_repositories",
          "input": {
            "query": "modelcontextprotocol"
          }
        }
      }
    ]
  }'
```

#### ファイル内容取得

```bash
curl -X POST http://localhost:5002/respond \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": {
          "tool_name": "get_file_contents",
          "input": {
            "owner": "octocat",
            "repo": "Hello-World",
            "path": "README.md"
          }
        }
      }
    ]
  }'
```

## サポートしているツール

GitHub MCPサーバーは以下の機能を提供します：

1. `create_or_update_file` - リポジトリに単一ファイルを作成/更新
2. `push_files` - 複数ファイルを一度のコミットでプッシュ
3. `search_repositories` - GitHubリポジトリを検索
4. `create_repository` - 新しいGitHubリポジトリを作成
5. `get_file_contents` - ファイルまたはディレクトリの内容を取得
6. `create_issue` - 新しいイシューを作成
7. `create_pull_request` - 新しいプルリクエストを作成
8. `fork_repository` - リポジトリをフォーク
9. `create_branch` - 新しいブランチを作成
10. `list_commits` - ブランチのコミット一覧を取得
11. `list_issues` - リポジトリのイシュー一覧を取得
12. `update_issue` - 既存のイシューを更新
13. `add_issue_comment` - イシューにコメントを追加
14. `search_code` - コードを検索
15. `search_issues` - イシューとプルリクエストを検索
16. `search_users` - GitHubユーザーを検索
17. `get_issue` - 特定のイシューの詳細を取得
18. `get_pull_request` - 特定のプルリクエストの詳細を取得
19. `list_pull_requests` - プルリクエスト一覧を取得
20. `create_pull_request_review` - プルリクエストのレビューを作成
21. `merge_pull_request` - プルリクエストをマージ
22. `get_pull_request_files` - プルリクエストの変更ファイル一覧を取得
23. `get_pull_request_status` - プルリクエストのステータスを取得
24. `update_pull_request_branch` - プルリクエストのブランチを更新
25. `get_pull_request_comments` - プルリクエストのコメントを取得
26. `get_pull_request_reviews` - プルリクエストのレビューを取得

詳細な各ツールの入力パラメータや使用方法については、[公式リポジトリのドキュメント](https://github.com/modelcontextprotocol/servers/tree/main/src/github)を参照してください。

## 注意事項

- **アクセストークン**: GitHub Personal Access Tokenは必要なスコープ（repoまたはpublic_repo）を持つものを使用してください。APIレート制限にも注意してください。
- **リクエスト形式**: MCPのプロトコルに準拠し、各メッセージはroleとcontent（中にtool_nameとinput）を含む必要があります。
- **stdioモード**: このMCPサーバーはHTTPサーバーではなく、標準入出力（stdio）を介して通信するよう設計されています。Cursorなどのツールから呼び出して使用するのが最適です。

## ライセンス

このプロジェクトは、元のMCP serverと同じMITライセンスのもとで提供されています。
