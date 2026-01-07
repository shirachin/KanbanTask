#!/bin/sh

# node_modulesが存在しない、または空の場合、またはviteが存在しない場合はインストール
if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules 2>/dev/null)" ] || [ ! -f "node_modules/.bin/vite" ]; then
  echo "Installing dependencies..."
  npm install || echo "npm install failed, continuing..."
fi

# 所有権をホスト側のユーザーに変更（UID/GIDは環境変数から取得、デフォルトは1000）
chown -R ${USER_ID:-1000}:${GROUP_ID:-1000} /app/node_modules 2>/dev/null || true

# 元のコマンドを実行
exec "$@"
