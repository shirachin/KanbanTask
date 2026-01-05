FROM node:20-alpine

# プロキシ設定をビルド引数として受け取る
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# プロキシ環境変数を設定（空の場合は設定しない）
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV no_proxy=${NO_PROXY}
ENV NO_PROXY=${NO_PROXY}

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
