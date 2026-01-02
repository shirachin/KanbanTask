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
@import '../styles/_color';

.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: $text-primary;
    font-size: 2rem;
  }
}

.dashboard-content {
  background: $background-light;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: $shadow-md;
}
</style>
