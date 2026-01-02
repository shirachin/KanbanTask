<template>
  <div class="app" :class="{ 'nav-collapsed': !navOpen }">
    <header class="header">
      <div class="header-content">
        <button 
          type="button"
          class="nav-toggle-button"
          @click="toggleNav"
          :aria-label="navOpen ? 'ナビゲーションを閉じる' : 'ナビゲーションを開く'"
        >
          <span class="material-symbols-outlined nav-toggle-icon">
            {{ navOpen ? 'menu_open' : 'menu' }}
          </span>
        </button>
        <h1>タスク管理アプリ</h1>
        <ThemeSelector />
      </div>
    </header>
    <nav class="nav" :class="{ 'nav-collapsed': !navOpen }">
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
      <span class="version">β0.1.0</span>
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
const navOpen = ref(true)

const switchView = (view: ViewType) => {
  currentView.value = view
}

const toggleNav = () => {
  navOpen.value = !navOpen.value
}
</script>

<style lang="scss" scoped>
@import './styles/_theme';

.app {
  height: 100vh;
  width: 100%;
  display: grid;
  grid-template-areas:
    "header header"
    "nav main"
    "footer footer";
  grid-template-columns: 200px 1fr;
  grid-template-rows: auto 1fr auto;
  transition: grid-template-columns 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.app.nav-collapsed {
  grid-template-columns: 0 1fr;
}

.header {
  grid-area: header;
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--current-headerBackground);
  color: var(--current-textWhite);
  padding: 0.75rem 1.5rem;
  box-shadow: 0 2px 4px var(--current-shadowSm);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;

  .nav-toggle-button {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    border: 1px solid var(--current-buttonBorderColor);
    border-radius: 6px;
    background: var(--current-buttonBackground);
    color: var(--current-textWhite);
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s, transform 0.1s;

    &:hover {
      background: var(--current-buttonHoverBackground);
      border-color: var(--current-buttonHoverBorderColor);
    }

    &:active {
      transform: scale(0.95);
    }

    &:focus {
      outline: none;
      border-color: var(--current-buttonFocusBorderColor);
      background: var(--current-buttonFocusBackground);
    }

    .nav-toggle-icon {
      font-variation-settings:
        'FILL' 0,
        'wght' 400,
        'GRAD' 0,
        'opsz' 24;
      font-size: 1.5rem;
      color: var(--current-textWhite);
      opacity: 0.9;
    }
  }

  h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 600;
    flex: 1;
  }
}

.nav {
  grid-area: nav;
  background: var(--current-navBackground);
  border-right: 1px solid var(--current-borderColor);
  padding: 1rem 0;
  overflow-y: auto;
  overflow-x: hidden;
  width: 200px;
  min-width: 200px;
  height: 100%;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(0);

  &.nav-collapsed {
    transform: translateX(-100%);
  }
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: block;
  padding: 0.75rem 1.5rem;
  color: var(--current-textPrimary);
  text-decoration: none;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--current-hoverBackground);
  }

  &:active,
  &.active {
    background-color: var(--current-activeBackground);
    color: $text-white;
  }
}

.main {
  grid-area: main;
  padding: 2rem;
  overflow-y: auto;
  overflow-x: hidden;
  height: 100%;
  background: var(--current-mainBackground);
}

.footer {
  grid-area: footer;
  background: var(--current-footerBackground);
  border-top: 1px solid var(--current-borderColor);
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--current-textSecondary);
  font-size: 0.875rem;

  p {
    margin: 0;
  }

  .version {
    font-size: 0.875rem;
    opacity: 0.7;
  }
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--current-textSecondary);
  font-size: 1.2rem;
}
</style>
