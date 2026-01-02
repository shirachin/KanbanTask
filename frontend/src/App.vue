<template>
  <div class="app">
    <header class="header">
      <h1>タスク管理アプリ</h1>
    </header>
    <nav class="nav">
      <ul class="nav-list">
        <li><a href="#" class="nav-link">ダッシュボード</a></li>
        <li><a href="#" class="nav-link">カンバンボード</a></li>
      </ul>
    </nav>
    <main class="main">
      <Dashboard />
    </main>
    <footer class="footer">
      <p>&copy; 2024 タスク管理アプリ</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import Dashboard from './views/Dashboard.vue'
</script>

<style lang="scss" scoped>
@import './styles/_color';

.app {
  min-height: 100vh;
  width: 100%;
  display: grid;
  grid-template-areas:
    "header header"
    "nav main"
    "footer footer";
  grid-template-columns: 200px 1fr;
  grid-template-rows: auto 1fr auto;
}

.header {
  grid-area: header;
  background: linear-gradient(135deg, $primary-gradient-start 0%, $primary-gradient-end 100%);
  color: $text-white;
  padding: 1.5rem 2rem;
  box-shadow: $shadow-sm;

  h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 600;
  }
}

.nav {
  grid-area: nav;
  background: $background-gray;
  border-right: 1px solid $border-color;
  padding: 1rem 0;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: block;
  padding: 0.75rem 1.5rem;
  color: $text-primary;
  text-decoration: none;
  transition: background-color 0.2s;

  &:hover {
    background-color: $background-gray-hover;
  }

  &:active,
  &.active {
    background-color: $primary-color;
    color: $text-white;
  }
}

.main {
  grid-area: main;
  padding: 2rem;
  overflow-y: auto;
  background: $background-light;
}

.footer {
  grid-area: footer;
  background: $background-gray;
  border-top: 1px solid $border-color;
  padding: 1rem 2rem;
  text-align: center;
  color: $text-secondary;
  font-size: 0.875rem;

  p {
    margin: 0;
  }
}
</style>
