<template>
  <div class="help">
    <div class="help-header">
      <h2>使い方</h2>
    </div>
    
    <div class="help-content">
      <section class="help-section">
        <h3 class="section-title">ログイン</h3>
        <p class="section-description">
          アプリを起動すると、ログイン画面が表示されます。半角英数字のみのユーザー名を入力してログインしてください。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">ダッシュボード</h3>
        <p class="section-description">
          ダッシュボードでは、プロジェクト一覧やタスクの統計情報を確認できます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">カンバンボード</h3>
        <p class="section-description">
          カンバンボードでは、タスクをステータスごとに管理できます。ドラッグ＆ドロップでタスクのステータスを変更できます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">色見本</h3>
        <p class="section-description">
          色見本ページでは、アプリケーションで使用されている色のパレットを確認できます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">テーマ切り替え</h3>
        <p class="section-description">
          ヘッダー右上のカラーアイコンをクリックすると、テーマを切り替えることができます。選択したテーマは自動的に保存されます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">ナビゲーション</h3>
        <p class="section-description">
          ヘッダー左上のメニューアイコンをクリックすると、ナビゲーションを開閉できます。ナビゲーションの最下部には、現在ログイン中のユーザー名が表示されます。
        </p>
      </section>

      <section class="help-section">
        <h3 class="section-title">ログアウト</h3>
        <p class="section-description">
          ナビゲーション最下部のユーザー情報をクリックすると、ログアウトメニューが表示されます。ログアウトボタンをクリックしてログアウトできます。
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// 使い方ページのロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.help {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.help-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.help-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.help-section {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.section-title {
  margin: 0 0 0.75rem 0;
  color: var(--current-textPrimary);
  font-size: 1.25rem;
  font-weight: 600;
}

.section-description {
  margin: 0;
  color: var(--current-textPrimary);
  line-height: 1.8;
}
</style>
