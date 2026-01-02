<template>
  <div class="theme-selector">
    <button 
      type="button"
      class="theme-icon-button"
      @click="toggleThemeMenu"
      :aria-label="`テーマを選択: ${selectedTheme}`"
    >
      <span class="material-symbols-outlined theme-icon">colors</span>
    </button>
    <div v-if="showThemeMenu" class="theme-menu">
      <button
        v-for="themeName in availableThemes"
        :key="themeName"
        type="button"
        class="theme-option"
        :class="{ active: selectedTheme === themeName }"
        @click="selectTheme(themeName)"
      >
        <span 
          class="theme-swatch"
          :style="{ background: getThemeColor(themeName) }"
        ></span>
        <span class="theme-name">{{ themeName.charAt(0).toUpperCase() + themeName.slice(1) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// CSS変数から利用可能な色名を取得
const getAvailableColorNames = (): string[] => {
  const colorNameSet = new Set<string>()
  
  Array.from(document.styleSheets).forEach(sheet => {
    try {
      Array.from(sheet.cssRules).forEach(rule => {
        if (rule instanceof CSSStyleRule && rule.selectorText === ':root') {
          Array.from(rule.style).forEach(prop => {
            const match = prop.match(/^--base-([^-]+)-hue$/)
            if (match) {
              colorNameSet.add(match[1])
            }
          })
        }
      })
    } catch {
      // クロスオリジンのスタイルシートは無視
    }
  })
  
  return Array.from(colorNameSet).sort()
}

const availableThemes = ref<string[]>([])
const showThemeMenu = ref(false)
const selectedTheme = ref<string>('primary')

// テーマカラーを取得
const getThemeColor = (themeName: string): string => {
  const root = document.documentElement
  return getComputedStyle(root).getPropertyValue(`--${themeName}-50`).trim() || '#000000'
}

// テーマを適用
const applyTheme = () => {
  const root = document.documentElement
  const themeColor = getComputedStyle(root).getPropertyValue(`--${selectedTheme.value}-50`).trim()
  
  if (themeColor) {
    // CSS変数でテーマカラーを設定
    root.style.setProperty('--theme-color', themeColor)
    root.style.setProperty('--theme-hover', getComputedStyle(root).getPropertyValue(`--${selectedTheme.value}-49`).trim())
    root.style.setProperty('--theme-gradient-start', getComputedStyle(root).getPropertyValue(`--${selectedTheme.value}-52`).trim())
    root.style.setProperty('--theme-gradient-end', getComputedStyle(root).getPropertyValue(`--${selectedTheme.value}-48`).trim())
    
    // ローカルストレージに保存
    localStorage.setItem('app-theme', selectedTheme.value)
  }
}

// テーマメニューを開閉
const toggleThemeMenu = () => {
  showThemeMenu.value = !showThemeMenu.value
}

// テーマを選択
const selectTheme = (themeName: string) => {
  selectedTheme.value = themeName
  applyTheme()
  showThemeMenu.value = false
}

// メニュー外をクリックしたら閉じる
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.theme-selector')) {
    showThemeMenu.value = false
  }
}

onMounted(() => {
  availableThemes.value = getAvailableColorNames()
  // ローカルストレージから保存されたテーマを読み込む
  const savedTheme = localStorage.getItem('app-theme')
  if (savedTheme && availableThemes.value.includes(savedTheme)) {
    selectedTheme.value = savedTheme
  }
  applyTheme()
  
  // クリックイベントリスナーを追加
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="scss" scoped>
@import '../styles/_color';

.theme-selector {
  position: relative;
  display: flex;
  align-items: center;

  .theme-icon-button {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.1);
    color: $text-white;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s, transform 0.1s;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
      border-color: rgba(255, 255, 255, 0.4);
    }

    &:active {
      transform: scale(0.95);
    }

    &:focus {
      outline: none;
      border-color: rgba(255, 255, 255, 0.5);
      background: rgba(255, 255, 255, 0.2);
    }

    .theme-icon {
      font-variation-settings:
        'FILL' 0,
        'wght' 400,
        'GRAD' 0,
        'opsz' 24;
      font-size: 1.5rem;
      color: $text-white;
      opacity: 0.9;
    }
  }

  .theme-menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    background: $background-light;
    border: 1px solid $border-color;
    border-radius: 8px;
    box-shadow: $shadow-lg;
    padding: 0.5rem;
    min-width: 200px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .theme-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: $text-primary;
    cursor: pointer;
    transition: background-color 0.2s;
    text-align: left;
    width: 100%;

    &:hover {
      background: $background-gray-hover;
    }

    &.active {
      background: var(--theme-color, $primary-color);
      color: $text-white;
    }

    .theme-swatch {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      border: 1px solid rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
    }

    .theme-name {
      font-size: 0.875rem;
      font-weight: 500;
    }
  }
}
</style>
