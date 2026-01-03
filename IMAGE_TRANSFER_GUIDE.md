# 画像転送ガイド

WindowsからLinuxへ画像を転送してアイコンとして使用する方法

## 画像の配置場所

画像ファイルは以下のディレクトリに配置してください：
```
/home/dockeruser/taskapp/frontend/src/assets/icons/
```

## 転送方法

### 方法1: SCPコマンド（推奨）

WindowsのコマンドプロンプトまたはPowerShellから以下のコマンドを実行：

```bash
scp /path/to/your/image.png dockeruser@192.168.2.191:/home/dockeruser/taskapp/frontend/src/assets/icons/
```

または、複数のファイルを転送する場合：

```bash
scp /path/to/your/*.png dockeruser@192.168.2.191:/home/dockeruser/taskapp/frontend/src/assets/icons/
```

### 方法2: WinSCP（GUIツール）

1. WinSCPをダウンロード・インストール
2. 以下の情報で接続：
   - ホスト名: `192.168.2.191`
   - ユーザー名: `dockeruser`
   - パスワード: （設定されているパスワード）
3. リモート側で `/home/dockeruser/taskapp/frontend/src/assets/icons/` に移動
4. ローカル側の画像ファイルをドラッグ&ドロップ

### 方法3: FileZilla（FTP/SFTPクライアント）

1. FileZillaをダウンロード・インストール
2. 以下の情報で接続：
   - ホスト: `sftp://192.168.2.191`
   - ユーザー名: `dockeruser`
   - パスワード: （設定されているパスワード）
   - ポート: `22`
3. リモート側で `/home/dockeruser/taskapp/frontend/src/assets/icons/` に移動
4. ローカル側の画像ファイルをドラッグ&ドロップ

### 方法4: Dockerコンテナに直接コピー

Dockerコンテナが起動している場合：

```bash
docker cp /path/to/your/image.png taskapp_frontend:/app/src/assets/icons/
```

## 画像ファイルの形式

推奨される形式：
- PNG（透明背景に対応）
- SVG（ベクター形式、拡大縮小に強い）
- ICO（Windowsアイコン形式）

推奨サイズ：
- 16x16px（小さいアイコン）
- 24x24px（標準アイコン）
- 32x32px（大きいアイコン）
- 48x48px（特大アイコン）

## 画像の使用方法

画像を配置した後、Vueコンポーネントで以下のように使用できます：

```vue
<template>
  <img src="@/assets/icons/your-icon.png" alt="アイコン" />
</template>
```

または、動的にインポートする場合：

```vue
<script setup>
import iconImage from '@/assets/icons/your-icon.png'
</script>

<template>
  <img :src="iconImage" alt="アイコン" />
</template>
```

## 注意事項

- ファイル名は英数字とハイフン、アンダースコアのみを使用してください
- 大文字小文字を区別するため、ファイル名は統一してください
- 画像を追加した後、フロントエンドのホットリロードで自動的に反映されます
