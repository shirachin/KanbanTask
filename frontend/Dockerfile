FROM node:20-alpine

# プロキシ設定をビルド引数として受け取る
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# ホスト側のユーザーID/グループIDをビルド引数として受け取る
ARG USER_ID=1000
ARG GROUP_ID=1000

# プロキシ環境変数を設定（空の場合は設定しない）
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV no_proxy=${NO_PROXY}
ENV NO_PROXY=${NO_PROXY}

WORKDIR /app

# パッケージファイルをコピーしてインストール
COPY package*.json ./
RUN npm install

# ファイルをコピー
COPY . .

# entrypointスクリプトをコピーして実行可能にする
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
