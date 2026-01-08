<template>
  <v-app class="app-no-scroll">
    <Login v-if="!hasUser" />
    <div v-else class="layout" :class="{ 'nav-collapsed': !navOpen }">
      <header class="header">
        <v-toolbar density="compact" color="primary" flat>
          <v-btn
            :icon="navOpen ? 'mdi-menu-open' : 'mdi-menu'"
            variant="text"
            @click="toggleNav"
          />
          <v-toolbar-title>
            <div class="d-flex align-center">
              <div class="header-icon mr-2" v-html="iconSvg"></div>
              <span>タスク管理アプリ</span>
            </div>
          </v-toolbar-title>
          <v-spacer />
          <ThemeSelector />
        </v-toolbar>
      </header>

      <aside class="nav">
        <div class="pane">
          <v-list density="compact" nav>
            <v-list-item
              prepend-icon="mdi-view-dashboard"
              title="ダッシュボード"
              :active="currentView === 'dashboard'"
              @click="switchView('dashboard')"
            />
            <v-list-item
              prepend-icon="mdi-view-column"
              title="カンバンボード"
              :active="currentView === 'kanban'"
              @click="switchView('kanban')"
            />
            <v-list-item
              prepend-icon="mdi-format-list-checks"
              title="TODOリスト"
              :active="currentView === 'todo'"
              @click="switchView('todo')"
            />
            <v-list-item
              prepend-icon="mdi-chart-gantt"
              title="ガントチャート"
              :active="currentView === 'gantt'"
              disabled
              @click="switchView('gantt')"
            >
              <template v-slot:append>
                <v-chip size="x-small" color="grey">未実装</v-chip>
              </template>
            </v-list-item>
            <v-list-item
              prepend-icon="mdi-folder-multiple"
              title="プロジェクト管理"
              :active="currentView === 'project'"
              @click="switchView('project')"
            />
            <v-list-item
              prepend-icon="mdi-help-circle"
              title="使い方"
              :active="currentView === 'help'"
              @click="switchView('help')"
            />
          </v-list>

          <div class="nav-footer">
            <v-divider />
            <v-menu location="top">
              <template v-slot:activator="{ props }">
                <v-list-item
                  v-bind="props"
                  prepend-icon="mdi-account-circle"
                  :title="currentUser || 'ユーザー'"
                  class="user-menu-item"
                />
              </template>
              <v-list>
                <v-list-item
                  prepend-icon="mdi-logout"
                  title="ログアウト"
                  @click="handleLogout"
                />
              </v-list>
            </v-menu>
          </div>
        </div>
      </aside>

      <main class="main">
        <div class="pane">
          <Dashboard v-if="currentView === 'dashboard'" />
          <KanbanBoard v-else-if="currentView === 'kanban'" />
          <TodoList v-else-if="currentView === 'todo'" />
          <GanttChart v-else-if="currentView === 'gantt'" />
          <ProjectManagement v-else-if="currentView === 'project'" />
          <Changelog v-else-if="currentView === 'changelog'" />
          <Help v-else-if="currentView === 'help'" />
        </div>
      </main>

      <footer class="footer">
        <div class="status">
          <v-btn
            variant="text"
            size="small"
            density="compact"
            @click="switchView('changelog')"
            class="px-2 version-btn"
          >
            <span class="beta-char">β</span>0.1.5
          </v-btn>
          <v-spacer />
          <span class="text-caption font-monospace px-2">{{ currentTime }}</span>
        </div>
      </footer>
    </div>
  </v-app>
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

const handleLogout = () => {
  const url = new URL(window.location.href)
  url.searchParams.delete('user')
  url.searchParams.delete('view')
  window.location.href = url.toString()
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

    // 現在時刻を更新（初回）
    updateTime()
    // 1秒ごとに現在時刻を更新
    timeInterval = window.setInterval(updateTime, 1000)
  })

  onUnmounted(() => {
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
// VSCode風レイアウト（CSS Grid版）
.layout {
  height: 100%;
  width: 100%;
  display: grid;
  grid-template-areas:
    "header header"
    "nav    main"
    "footer footer";
  grid-template-columns: 200px 1fr;
  grid-template-rows: auto 1fr 22px;
  overflow: hidden; /* 全体はスクロールさせない */
  transition: grid-template-columns 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.layout.nav-collapsed {
  grid-template-columns: 0 1fr;
}

/* エリア割当 */
.header {
  grid-area: header;
  overflow: hidden;
  z-index: 100;
  background-color: var(--current-headerBackground);
  
  :deep(.v-toolbar) {
    background-color: var(--current-headerBackground) !important;
  }
}

.nav {
  grid-area: nav;
  border-right: 1px solid rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main {
  grid-area: main;
  overflow: hidden;
  position: relative;
  height: 100%;
}

.footer {
  grid-area: footer;
  overflow: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

/* nav/main だけスクロール */
.pane {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

.nav .pane {
  // ナビゲーションのフッターを下部に固定
  .nav-footer {
    margin-top: auto;
  }
}

.main .pane {
  padding: 1rem;
  box-sizing: border-box;
}

/* status bar っぽく */
.status {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0;
  width: 100%;
  justify-content: space-between;
}

.version-btn {
  min-width: auto !important;
  font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

.beta-char {
  font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  font-feature-settings: normal;
  font-variant: normal;
  unicode-bidi: normal;
}

.header-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: inherit;
  
  :deep(svg) {
    width: 100%;
    height: 100%;
  }
  
  :deep(.st0) {
    fill: currentColor;
  }
}

.user-menu-item {
  cursor: pointer;
}

// v-appがスクロールしないように
.app-no-scroll {
  overflow: hidden !important;
  height: 100% !important;
}
</style>
