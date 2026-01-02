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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 600;
  }
}

.nav {
  grid-area: nav;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
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
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;

  &:hover {
    background-color: #e9ecef;
  }

  &:active,
  &.active {
    background-color: #667eea;
    color: white;
  }
}

.main {
  grid-area: main;
  padding: 2rem;
  overflow-y: auto;
  background: #ffffff;
}

.footer {
  grid-area: footer;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  padding: 1rem 2rem;
  text-align: center;
  color: #666;
  font-size: 0.875rem;

  p {
    margin: 0;
  }
}
</style>
