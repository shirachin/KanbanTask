# バックエンドリファクタリング完了

## 新しい構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーションのエントリーポイント
│   │
│   ├── core/                      # コア機能
│   │   ├── __init__.py
│   │   ├── config.py              # 設定管理
│   │   ├── database.py            # データベース接続
│   │   ├── constants.py           # 定数定義
│   │   ├── exceptions.py          # 例外ハンドラー
│   │   ├── middleware.py          # ミドルウェア設定
│   │   └── startup.py             # 起動時の処理
│   │
│   ├── models/                    # データモデル
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── schemas/                   # Pydanticスキーマ
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── project.py
│   │   ├── status.py
│   │   └── todo.py
│   │
│   ├── api/                       # APIルーター
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── tasks.py
│   │       ├── projects.py
│   │       ├── statuses.py
│   │       └── todos.py
│   │
│   └── migrations/               # データベースマイグレーション
│       ├── __init__.py
│       └── (マイグレーションファイル)
│
├── Dockerfile
└── requirements.txt
```

## 主な変更点

1. **モジュール化**: 機能ごとにディレクトリを分割
2. **設定の分離**: `config.py`で設定を一元管理
3. **APIルーターの分割**: 機能ごとにルーターを分離
4. **例外ハンドラーの分離**: `exceptions.py`に集約
5. **起動処理の分離**: `startup.py`に集約

## 後方互換性

- `/api`と`/api/v1`の両方のパスでアクセス可能
- 既存のエンドポイントはすべて動作

## 移行方法

1. 既存の`main.py`は`app/main.py`に移動
2. すべてのインポートパスを更新
3. Dockerfileとdocker-compose.ymlを更新
