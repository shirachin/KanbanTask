<template>
  <div class="todo-list">
    <div class="todo-header">
      <h2>TODOリスト</h2>
    </div>
    
    <div class="todo-content">
      <div class="todo-section">
        <h3 class="section-title">タスク一覧</h3>
        <div class="task-list">
          <p class="empty-message">タスクがありません</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// TODOリストのロジックをここに追加
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.todo-list {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.todo-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.todo-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.todo-section {
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
