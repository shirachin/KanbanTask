<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>ダッシュボード</h2>
    </div>
    
    <div class="dashboard-content">
      <p>ダッシュボードコンテンツ</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// ダッシュボードのロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
  }
}

.dashboard-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}
</style>
