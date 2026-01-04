<template>
  <div class="gantt-chart">
    <div class="gantt-header">
      <h2>ガントチャート</h2>
    </div>
    
    <div class="gantt-content">
      <div class="gantt-section">
        <div class="not-implemented-container">
          <div class="not-implemented-icon">
            <span class="material-symbols-outlined">construction</span>
          </div>
          <h3 class="not-implemented-title">未実装</h3>
          <p class="not-implemented-message">この機能は現在開発中です。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ガントチャートのロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.gantt-chart {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.gantt-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.gantt-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.gantt-section {
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  margin: 0 0 1rem 0;
  color: var(--current-textPrimary);
  font-size: 1.25rem;
  font-weight: 600;
}

.chart-container {
  min-height: 400px;
  overflow-x: auto;
}

.empty-message {
  margin: 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  text-align: center;
  padding: 2rem 0;
}

.not-implemented-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 3rem 2rem;
  text-align: center;
}

.not-implemented-icon {
  margin-bottom: 1.5rem;
  
  .material-symbols-outlined {
    font-size: 4rem;
    color: var(--current-textSecondary);
    opacity: 0.5;
    font-variation-settings:
      'FILL' 0,
      'wght' 400,
      'GRAD' 0,
      'opsz' 48;
  }
}

.not-implemented-title {
  margin: 0 0 1rem 0;
  color: var(--current-textPrimary);
  font-size: 1.5rem;
  font-weight: 600;
}

.not-implemented-message {
  margin: 0;
  color: var(--current-textSecondary);
  font-size: 1rem;
}
</style>
