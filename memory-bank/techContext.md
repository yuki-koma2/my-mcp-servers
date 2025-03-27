# 技術コンテキスト

## 使用技術スタック

### フロントエンド
- **フレームワーク**: Next.js 14（App Routerを使用）
- **UI**: React, Tailwind CSS, Shadcn UI
- **状態管理**: Zustand
- **データフェッチング**: TanStack Query（React Query）
- **フォーム管理**: React Hook Form + Zod

### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **DB**: PostgreSQL 15
- **キャッシュ**: Redis

### インフラストラクチャ
- **コンテナ化**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **モニタリング**: Prometheus, Grafana
- **ロギング**: ELK Stack (Elasticsearch, Logstash, Kibana)

### Minecraftサーバー
- **サーバーソフトウェア**: 
  - Java Edition: Paper, Spigot, Vanilla
  - Bedrock Edition: Bedrock Dedicated Server
- **バージョン管理**: 複数バージョンをサポート（1.16〜最新）

## 開発環境セットアップ
- **必要条件**:
  - Docker と Docker Compose
  - Node.js 18+
  - Python 3.11+
  - Javaランタイム（Minecraft Java Edition用）

- **セットアップ手順**:
  1. リポジトリのクローン
  2. `docker-compose up -d` で開発環境を起動
  3. フロントエンド開発: `cd frontend && npm install && npm run dev`
  4. バックエンド開発: `cd services/api && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload`

## 技術的制約
- サーバーインスタンスごとに最小限のリソース要件あり（RAM: 1GB以上推奨）
- Java Edition用とBedrock Edition用で別々のサーバー管理が必要
- プラグイン互換性はMinecraftバージョンに依存

## 外部依存関係
- Minecraft公式ダウンロードAPIとの連携
- プラグインリポジトリとの連携（Spigot, Bukkit, CurseForge等）
- バックアップストレージ（ローカルまたはクラウド）

## セキュリティに関する考慮事項
- サーバー管理用の認証と認可
- Minecraftサーバーへのアクセス制御
- プラグインのセキュリティ検証
- データバックアップの暗号化
- サーバーインスタンスの分離 