# 公式 Sentry MCP サーバー

このプロジェクトは、[Model Context Protocol](https://github.com/modelcontextprotocol/servers) の公式 Sentry MCP サーバーを Docker で実行するための設定です。

## セットアップ手順

### 前提条件

- Docker と docker-compose がインストールされていること
- Sentry のAPIトークンを取得済みであること

### インストール手順

1. 環境変数ファイルを設定する：
```bash
cp .env.template .env
# 編集して適切なAPIトークンと組織名を設定
```

2. Docker イメージをビルドして起動する：
```bash
docker-compose build
docker-compose up -d
```

3. サービスが正常に稼働していることを確認する：
```bash
docker-compose ps
```

## 使用方法

Sentry MCP サーバーは以下のURLで利用可能です：
- http://localhost:9000/

詳細なAPIドキュメントは以下で確認できます：
- http://localhost:9000/docs

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

## 公式リポジトリ

このプロジェクトは以下の公式リポジトリを使用しています：
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/sentry) 