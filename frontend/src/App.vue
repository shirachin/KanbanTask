<template>
  <Login v-if="!hasUser" />
  <div v-else class="app" :class="{ 'nav-collapsed': !navOpen }">
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
      <div class="nav-user" @click="toggleUserMenu">
        <span class="material-symbols-outlined user-icon">account_circle</span>
        <span class="user-name">{{ currentUser }}</span>
        <div v-if="showUserMenu" class="user-menu">
          <button type="button" class="user-menu-item" @click="handleLogout">
            <span class="material-symbols-outlined user-menu-icon">logout</span>
            <span class="user-menu-text">ログアウト</span>
          </button>
        </div>
      </div>
    </nav>
    <main class="main">
      <Dashboard v-if="currentView === 'dashboard'" />
      <ColorPalette v-else-if="currentView === 'color-palette'" />
      <div v-else-if="currentView === 'kanban'" class="placeholder">
        <p>カンバンボード（準備中）</p>
      </div>
    </main>
    <footer class="footer">
      <span class="version">β0.1.0</span>
      <span class="current-time">{{ currentTime }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import Dashboard from './views/Dashboard.vue'
import ColorPalette from './views/ColorPalette.vue'
import Login from './views/Login.vue'
import ThemeSelector from './components/ThemeSelector.vue'

type ViewType = 'dashboard' | 'kanban' | 'color-palette'

const currentView = ref<ViewType>('dashboard')
const navOpen = ref(true)
const showUserMenu = ref(false)

// URLパラメータからユーザー名を取得
const getUrlUser = (): string | null => {
  const params = new URLSearchParams(window.location.search)
  return params.get('user')
}

const currentUser = ref<string | null>(getUrlUser())
const hasUser = computed(() => currentUser.value !== null)
const currentTime = ref<string>('')

// 現在時刻を更新
const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
}

let timeInterval: number | null = null

// URLパラメータを維持しながらビューを切り替え
const switchView = (view: ViewType) => {
  currentView.value = view
  // URLパラメータを維持
  if (currentUser.value) {
    const url = new URL(window.location.href)
    url.searchParams.set('user', currentUser.value)
    url.searchParams.set('view', view)
    window.history.pushState({}, '', url.toString())
  }
}

const toggleNav = () => {
  navOpen.value = !navOpen.value
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleLogout = () => {
  const url = new URL(window.location.href)
  url.searchParams.delete('user')
  url.searchParams.delete('view')
  window.location.href = url.toString()
}

// メニュー外をクリックしたら閉じる
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.nav-user') && !target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

  // URLパラメータの変更を監視
  onMounted(() => {
    // 初期ビューをURLパラメータから取得
    const params = new URLSearchParams(window.location.search)
    const viewParam = params.get('view') as ViewType | null
    if (viewParam && ['dashboard', 'kanban', 'color-palette'].includes(viewParam)) {
      currentView.value = viewParam
    }

    // URLパラメータの変更を監視（ブラウザの戻る/進むボタン対応）
    window.addEventListener('popstate', () => {
      const user = getUrlUser()
      if (user) {
        currentUser.value = user
        const params = new URLSearchParams(window.location.search)
        const viewParam = params.get('view') as ViewType | null
        if (viewParam && ['dashboard', 'kanban', 'color-palette'].includes(viewParam)) {
          currentView.value = viewParam
        }
      } else {
        currentUser.value = null
      }
    })

    // クリックイベントリスナーを追加
    document.addEventListener('click', handleClickOutside)

    // 現在時刻を更新（初回）
    updateTime()
    // 1秒ごとに現在時刻を更新
    timeInterval = window.setInterval(updateTime, 1000)
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
    if (timeInterval !== null) {
      clearInterval(timeInterval)
    }
  })

// ユーザー名が変更されたらURLを更新
watch(currentUser, (newUser: string | null) => {
  if (newUser) {
    const url = new URL(window.location.href)
    url.searchParams.set('user', newUser)
    if (currentView.value) {
      url.searchParams.set('view', currentView.value)
    }
    window.history.replaceState({}, '', url.toString())
  }
})
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
  padding: 0;
  overflow: hidden;
  width: 200px;
  min-width: 200px;
  height: 100%;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(0);
  display: flex;
  flex-direction: column;
  position: relative;

  &.nav-collapsed {
    transform: translateX(-100%);
  }
}

.nav-list {
  list-style: none;
  padding: 1rem 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
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
    color: var(--current-textWhite);
  }
}

.nav-user {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--current-borderColor);
  background: var(--current-navBackground);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;

  &:hover {
    background-color: var(--current-hoverBackground);
  }

  .user-icon {
    font-variation-settings:
      'FILL' 0,
      'wght' 400,
      'GRAD' 0,
      'opsz' 24;
    font-size: 1.5rem;
    color: var(--current-textPrimary);
    flex-shrink: 0;
  }

  .user-name {
    color: var(--current-textPrimary);
    font-size: 0.875rem;
    font-weight: 500;
    flex: 1;
    padding: 0.5rem 0.75rem;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 6px;
    text-align: center;
    word-break: break-word;
  }
}

.user-menu {
  position: absolute;
  bottom: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  background: var(--current-backgroundLight);
  border: 1px solid var(--current-borderColor);
  border-radius: 8px;
  box-shadow: 0 4px 16px var(--current-shadowLg);
  padding: 0.5rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--current-textPrimary);
  cursor: pointer;
  transition: background-color 0.2s;
  text-align: left;
  width: 100%;

  &:hover {
    background: var(--current-hoverBackground);
  }

  .user-menu-icon {
    font-variation-settings:
      'FILL' 0,
      'wght' 400,
      'GRAD' 0,
      'opsz' 24;
    font-size: 1.25rem;
    color: var(--current-textPrimary);
    flex-shrink: 0;
  }

  .user-menu-text {
    font-size: 0.875rem;
    font-weight: 500;
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

  .version {
    font-size: 0.875rem;
    opacity: 0.7;
  }

  .current-time {
    font-size: 0.875rem;
    font-family: 'Courier New', monospace;
    opacity: 0.8;
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
