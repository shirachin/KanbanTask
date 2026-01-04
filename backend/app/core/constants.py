"""
Application constants
"""

# デフォルトステータス定義
DEFAULT_STATUS_DEFINITIONS = [
    {"name": "considering", "display_name": "検討中", "order": 0, "color": "#9e9e9e"},
    {"name": "not_started", "display_name": "未実行", "order": 1, "color": "#667eea"},
    {"name": "in_progress", "display_name": "実行中", "order": 2, "color": "#ffa726"},
    {"name": "review_pending", "display_name": "レビュー待ち", "order": 3, "color": "#9c27b0"},
    {"name": "staging_deployed", "display_name": "検証環境反映済み", "order": 4, "color": "#ffeb3b"},
    {"name": "production_deployed", "display_name": "本番環境反映済み", "order": 5, "color": "#51cf66"},
    {"name": "cancelled", "display_name": "中止", "order": 6, "color": "#dc3545"},
]

# 個人タスク用のデフォルトステータス（project_id=-1）
DEFAULT_PERSONAL_STATUSES = [
    {"id": -1, "name": "considering", "display_name": "検討中", "order": 0, "color": "#9e9e9e", "project_id": -1},
    {"id": -2, "name": "not_started", "display_name": "未実行", "order": 1, "color": "#667eea", "project_id": -1},
    {"id": -3, "name": "in_progress", "display_name": "実行中", "order": 2, "color": "#ffa726", "project_id": -1},
    {"id": -4, "name": "review_pending", "display_name": "レビュー待ち", "order": 3, "color": "#9c27b0", "project_id": -1},
    {"id": -5, "name": "staging_deployed", "display_name": "検証環境反映済み", "order": 4, "color": "#ffeb3b", "project_id": -1},
    {"id": -6, "name": "production_deployed", "display_name": "本番環境反映済み", "order": 5, "color": "#51cf66", "project_id": -1},
    {"id": -7, "name": "cancelled", "display_name": "中止", "order": 6, "color": "#dc3545", "project_id": -1},
]
