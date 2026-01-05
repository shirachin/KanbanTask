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
        <div class="header-title">
          <div class="header-icon" v-html="iconSvg"></div>
        <h1>タスク管理アプリ</h1>
        </div>
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
            :class="{ active: currentView === 'todo' }"
            @click.prevent="switchView('todo')"
          >
            TODOリスト
          </a>
        </li>
        <li>
          <a 
            href="#" 
            class="nav-link nav-link-disabled" 
            :class="{ active: currentView === 'gantt' }"
            @click.prevent="switchView('gantt')"
          >
            ガントチャート
            <span class="nav-badge">未実装</span>
          </a>
        </li>
        <li>
          <a 
            href="#" 
            class="nav-link" 
            :class="{ active: currentView === 'project' }"
            @click.prevent="switchView('project')"
          >
            プロジェクト管理
          </a>
        </li>
        <li>
          <a 
            href="#" 
            class="nav-link" 
            :class="{ active: currentView === 'help' }"
            @click.prevent="switchView('help')"
          >
            使い方
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
      <KanbanBoard v-else-if="currentView === 'kanban'" />
      <TodoList v-else-if="currentView === 'todo'" />
      <GanttChart v-else-if="currentView === 'gantt'" />
      <ProjectManagement v-else-if="currentView === 'project'" />
      <Changelog v-else-if="currentView === 'changelog'" />
      <Help v-else-if="currentView === 'help'" />
    </main>
    <footer class="footer">
      <span class="version" @click="switchView('changelog')">β0.1.4</span>
      <span class="current-time">{{ currentTime }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import Dashboard from './views/Dashboard.vue'
import KanbanBoard from './views/KanbanBoard.vue'
import TodoList from './views/TodoList.vue'
import GanttChart from './views/GanttChart.vue'
import ProjectManagement from './views/ProjectManagement.vue'
import Changelog from './views/Changelog.vue'
import Help from './views/Help.vue'
import Login from './views/Login.vue'
import ThemeSelector from './components/ThemeSelector.vue'
import { getLocalStorage, setLocalStorage, STORAGE_KEYS } from './composables/useLocalStorage'

// SVGアイコンをインラインで埋め込む（currentColorを正しく機能させるため）
const iconSvg = `<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" xml:space="preserve" style="width: 32px; height: 32px;">
<style type="text/css">
	.st0{fill:currentColor;}
</style>
<g>
	<path class="st0" d="M444.51,253.4c-1.426-3.094-4.528-4.973-7.821-4.985c-0.012,0-0.023-0.008-0.031-0.008
		c-0.012,0-0.023,0.008-0.031,0.008c-2.004,0.004-4.043,0.629-5.762,2.203l-50.857,46.56V406.2c0,4.782-3.875,8.661-8.657,8.661
		H74.022c-4.782,0-8.661-3.879-8.661-8.661V264.377v-10.078v-86.244v-31.681V108.87c0-4.782,3.879-8.657,8.661-8.657h270.065
		c2.164,0,4.25-0.813,5.843-2.27l52.431-47.962c5.828-5.332,2.054-15.047-5.844-15.047H8.66c-4.781,0-8.66,3.875-8.66,8.657v427.97
		c0,4.786,3.879,8.661,8.66,8.661h428.053c4.782,0,8.657-3.875,8.657-8.661V257.006c0-1.328-0.352-2.489-0.84-3.562
		C444.526,253.428,444.518,253.416,444.51,253.4z"></path>
	<path class="st0" d="M494.64,33.34c-0.426-0.492-0.801-1.019-1.238-1.504l-0.003,0.004c-0.016-0.019-0.032-0.043-0.051-0.062
		L238.545,264.963l-47.962-51.333c-25.294-27.079-66.74-29.993-95.498-7.813c-1.774,1.355-3.492,2.805-5.145,4.336v0.004
		c-0.019,0.015-0.038,0.031-0.058,0.05l119.734,128.155c7.238,7.75,17.031,11.598,26.871,11.649c0.062,0,0.122,0.02,0.184,0.02
		h0.004c0.274,0,0.535-0.07,0.805-0.074c1.976-0.043,3.941-0.191,5.894-0.551c0.27-0.046,0.527-0.144,0.797-0.199
		c1.988-0.41,3.954-0.934,5.867-1.675c0.024-0.008,0.047-0.024,0.07-0.031c4.137-1.618,8.078-3.922,11.547-7.102L488.89,132.444
		C517.414,106.338,519.77,62.4,494.64,33.34z"></path>
</g>
</svg>`

type ViewType = 'dashboard' | 'kanban' | 'todo' | 'gantt' | 'project' | 'changelog' | 'help'

const currentView = ref<ViewType>(getLocalStorage<ViewType>(STORAGE_KEYS.APP_CURRENT_VIEW, 'dashboard'))
const navOpen = ref(true)
const showUserMenu = ref(false)

const currentUser = ref<string | null>(getLocalStorage<string | null>(STORAGE_KEYS.APP_CURRENT_USER, null))
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

// ビューを切り替え
const switchView = (view: ViewType) => {
  currentView.value = view
  setLocalStorage(STORAGE_KEYS.APP_CURRENT_VIEW, view)
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

  onMounted(() => {
    // LocalStorageから初期状態を復元
    const savedView = getLocalStorage<ViewType>(STORAGE_KEYS.APP_CURRENT_VIEW, 'dashboard')
    if (['dashboard', 'kanban', 'todo', 'gantt', 'project', 'changelog', 'help'].includes(savedView)) {
      currentView.value = savedView
    }
    
    const savedUser = getLocalStorage<string | null>(STORAGE_KEYS.APP_CURRENT_USER, null)
    if (savedUser) {
      currentUser.value = savedUser
      }

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

// ユーザー名が変更されたらLocalStorageを更新
watch(currentUser, (newUser: string | null) => {
  setLocalStorage(STORAGE_KEYS.APP_CURRENT_USER, newUser)
})

// ビューが変更されたらLocalStorageを更新
watch(currentView, (newView: ViewType) => {
  setLocalStorage(STORAGE_KEYS.APP_CURRENT_VIEW, newView)
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

  .header-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
  }

  .header-icon {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    // SVGの色をテーマカラーに合わせる
    color: var(--current-textWhite);
    transition: color 0.3s ease;
    
    :deep(svg) {
      width: 100%;
      height: 100%;
    }
    
    :deep(.st0) {
      fill: currentColor;
    }
  }

  h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 600;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
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

  &.nav-link-disabled {
    opacity: 0.7;
    cursor: default;
  }
}

.nav-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: var(--current-backgroundGrayLight);
  color: var(--current-textSecondary);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.5rem;
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
    background: var(--current-backgroundGrayLight);
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
  padding: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  height: 22px;
  line-height: 22px;

  .version {
    font-size: 0.875rem;
    color: var(--current-textSecondary);
    cursor: pointer;
    padding: 0 1rem;
    height: 100%;
    display: flex;
    align-items: center;
    transition: background-color 0.15s, color 0.15s;
    user-select: none;

    &:hover {
      background-color: var(--current-backgroundGrayMedium);
      color: var(--current-textPrimary);
    }

    &:active {
      background-color: var(--current-backgroundGrayDark);
    }
  }

  .current-time {
    font-size: 0.875rem;
    font-family: 'Courier New', monospace;
    opacity: 0.8;
    padding: 0 1rem;
    height: 100%;
    display: flex;
    align-items: center;
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
