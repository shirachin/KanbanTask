#!/bin/bash
# 既存のタスクの担当者を h73440 に更新するスクリプト

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-taskapp_db}"
DB_USER="${DB_USER:-taskapp}"
DB_PASSWORD="${DB_PASSWORD:-taskapp_password}"

echo "既存のタスクの担当者を h73440 に更新します..."
echo "データベース: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""

# psqlが使える場合
if command -v psql &> /dev/null; then
    export PGPASSWORD="${DB_PASSWORD}"
    
    # 更新前の件数を確認
    COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM tasks WHERE assignee != 'h73440' OR assignee IS NULL;")
    COUNT=$(echo $COUNT | xargs)
    
    echo "更新対象: ${COUNT} 件のタスク"
    echo ""
    
    if [ "$COUNT" -eq 0 ]; then
        echo "更新するタスクがありません。"
        exit 0
    fi
    
    # 一括更新
    echo "タスクの担当者を更新中..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "UPDATE tasks SET assignee = 'h73440' WHERE assignee != 'h73440' OR assignee IS NULL;"
    
    echo ""
    echo "=================================================="
    echo "更新が完了しました！"
    echo "  更新: ${COUNT} 件"
else
    echo "psqlコマンドが見つかりません。"
    echo "PostgreSQLクライアントをインストールするか、別の方法で更新してください。"
    exit 1
fi
