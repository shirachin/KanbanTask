<template>
  <div class="theme-selector">
    <v-menu location="bottom end" :close-on-content-click="false">
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon
          variant="text"
          size="small"
      :aria-label="`テーマを選択: ${selectedTheme}`"
    >
          <v-icon>mdi-palette</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item
        v-for="themeName in availableThemes"
        :key="themeName"
          :active="selectedTheme === themeName"
        @click="selectTheme(themeName)"
      >
          <template v-slot:prepend>
            <div
          class="theme-swatch"
          :style="{ background: getThemeColor(themeName) }"
            ></div>
          </template>
          <v-list-item-title>{{ getThemeDisplayName(themeName) }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

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

// テーマの表示名を取得（CSS変数からnameを取得）
const getThemeDisplayName = (themeName: string): string => {
  const root = document.documentElement
  const name = getComputedStyle(root).getPropertyValue(`--base-${themeName}-name`).trim()
  return name || themeName.charAt(0).toUpperCase() + themeName.slice(1)
}

const availableThemes = ref<string[]>([])
const selectedTheme = ref<string>('lightRed')

// テーマカラーを取得
const getThemeColor = (themeName: string): string => {
  const root = document.documentElement
  return getComputedStyle(root).getPropertyValue(`--${themeName}-50`).trim() || '#000000'
}

// テーマを適用
const applyTheme = () => {
  const root = document.documentElement
  const themeName = selectedTheme.value
  
  // 現在のテーマを設定
  root.style.setProperty('--current-theme', themeName)
  
  // headerBackgroundのみを取得して適用
  const headerBackgroundColor = getComputedStyle(root).getPropertyValue(`--${themeName}-headerBackground`).trim()
  
  console.log('Theme:', themeName, 'headerBackground:', headerBackgroundColor)
  
  if (headerBackgroundColor) {
    // headerBackgroundのみを更新
    root.style.setProperty('--current-headerBackground', headerBackgroundColor)
    console.log('Applied --current-headerBackground:', headerBackgroundColor)
  } else {
    console.warn('headerBackground color not found for theme:', themeName)
  }
  
  // ローカルストレージに保存
  localStorage.setItem('app-theme', themeName)
}

// テーマを選択
const selectTheme = (themeName: string) => {
  selectedTheme.value = themeName
  applyTheme()
}

onMounted(() => {
  availableThemes.value = getAvailableColorNames()
  // ローカルストレージから保存されたテーマを読み込む
  const savedTheme = localStorage.getItem('app-theme')
  if (savedTheme && availableThemes.value.includes(savedTheme)) {
    selectedTheme.value = savedTheme
  }
  applyTheme()
})
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.theme-selector {
  display: flex;
  align-items: center;
    }

    .theme-swatch {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      border: 1px solid var(--current-swatchBorderColor);
      flex-shrink: 0;
  margin-right: 8px;
}
</style>
