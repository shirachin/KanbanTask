<template>
  <div class="changelog">
    <div class="changelog-header">
      <h2>更新情報</h2>
    </div>
    
    <div class="changelog-content">
      <div class="version-section">
        <h3 class="version-title">β0.1.0</h3>
        <p class="version-date">2024年</p>
        <ul class="changelog-list">
          <li>初回リリース</li>
          <li>ダッシュボード機能</li>
          <li>カラーパレット機能</li>
          <li>テーマ切り替え機能</li>
          <li>ログイン機能（ユーザー名のみ）</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 更新情報のロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.changelog {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.changelog-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.changelog-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.version-section {
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.version-title {
  margin: 0 0 0.5rem 0;
  color: var(--current-textPrimary);
  font-size: 1.5rem;
  font-weight: 600;
}

.version-date {
  margin: 0 0 1rem 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
}

.changelog-list {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--current-textPrimary);
  line-height: 1.8;

  li {
    margin-bottom: 0.5rem;

    &:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
