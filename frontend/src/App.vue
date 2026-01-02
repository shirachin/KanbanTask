<template>
  <div class="app">
    <header class="header">
      <div class="header-content">
        <h1>タスク管理アプリ</h1>
        <ThemeSelector />
      </div>
    </header>
    <nav class="nav">
      <ul class="nav-list">
        <li>
          <a 
            href="#" 
            class="nav-link" 
            :class="{ active: currentView === 'dashboard' }"
            @click.prevent="switchView('dashboard')"
          >
            ダッシュボード
          </a>
        </li>
        <li>
          <a 
            href="#" 
            class="nav-link" 
            :class="{ active: currentView === 'kanban' }"
            @click.prevent="switchView('kanban')"
          >
            カンバンボード
          </a>
        </li>
        <li>
          <a 
            href="#" 
            class="nav-link" 
            :class="{ active: currentView === 'color-palette' }"
            @click.prevent="switchView('color-palette')"
          >
            色見本
          </a>
        </li>
      </ul>
    </nav>
    <main class="main">
      <Dashboard v-if="currentView === 'dashboard'" />
      <ColorPalette v-else-if="currentView === 'color-palette'" />
      <div v-else-if="currentView === 'kanban'" class="placeholder">
        <p>カンバンボード（準備中）</p>
      </div>
    </main>
    <footer class="footer">
      <p>&copy; 2024 タスク管理アプリ</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Dashboard from './views/Dashboard.vue'
import ColorPalette from './views/ColorPalette.vue'
import ThemeSelector from './components/ThemeSelector.vue'

type ViewType = 'dashboard' | 'kanban' | 'color-palette'

const currentView = ref<ViewType>('dashboard')

const switchView = (view: ViewType) => {
  currentView.value = view
}
</script>

<style lang="scss" scoped>
@import './styles/_color';
@import './styles/_theme';

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
  background: linear-gradient(135deg, var(--theme-gradient-start, $primary-gradient-start) 0%, var(--theme-gradient-end, $primary-gradient-end) 100%);
  color: $text-white;
  padding: 1.5rem 2rem;
  box-shadow: $shadow-sm;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;

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
    background-color: var(--theme-color, $primary-color);
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

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: $text-secondary;
  font-size: 1.2rem;
}
</style>
