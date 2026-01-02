<template>
  <div class="kanban-board">
    <div class="kanban-header">
      <h2>カンバンボード</h2>
    </div>
    
    <div class="kanban-content">
      <div class="kanban-columns">
        <div class="kanban-column">
          <h3 class="column-title">未着手</h3>
          <div class="task-list">
            <p class="empty-message">タスクがありません</p>
          </div>
        </div>
        <div class="kanban-column">
          <h3 class="column-title">進行中</h3>
          <div class="task-list">
            <p class="empty-message">タスクがありません</p>
          </div>
        </div>
        <div class="kanban-column">
          <h3 class="column-title">レビュー中</h3>
          <div class="task-list">
            <p class="empty-message">タスクがありません</p>
          </div>
        </div>
        <div class="kanban-column">
          <h3 class="column-title">完了</h3>
          <div class="task-list">
            <p class="empty-message">タスクがありません</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// カンバンボードのロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.kanban-board {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.kanban-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.kanban-content {
  overflow-x: auto;
}

.kanban-columns {
  display: flex;
  gap: 1.5rem;
  min-width: fit-content;
}

.kanban-column {
  flex: 1;
  min-width: 280px;
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.column-title {
  margin: 0 0 1rem 0;
  color: var(--current-textPrimary);
  font-size: 1.125rem;
  font-weight: 600;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--current-borderColor);
}

.task-list {
  min-height: 200px;
}

.empty-message {
  margin: 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  text-align: center;
  padding: 2rem 0;
}
</style>
