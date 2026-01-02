<template>
  <div class="color-palette">
    <div class="palette-header">
      <h2>カラーパレット</h2>
      <p>基準色から生成されたグラデーションを表示します</p>
    </div>

    <div class="palette-content">
      <section class="color-section">
        <h3>カラーグラデーション</h3>
        <div 
          class="gradient-grid" 
          :style="{ gridTemplateColumns: `150px repeat(${colorNames.length}, 1fr)` }"
        >
          <!-- ヘッダー行 -->
          <div class="gradient-header">
            <div class="header-label">段階</div>
          </div>
          <div 
            v-for="colorName in colorNames" 
            :key="`header-${colorName}`"
            class="gradient-header"
          >
            <div class="header-label">{{ colorName.charAt(0).toUpperCase() + colorName.slice(1) }}色</div>
          </div>

          <!-- データ行 -->
          <template v-if="colorNames.length > 0 && colorScales[colorNames[0]]">
            <template v-for="(step, index) in colorScales[colorNames[0]]" :key="`row-${index}`">
              <!-- 段階番号 -->
              <div class="gradient-step-cell" :class="{ 'base-color': step.level === 50 }">
                <div class="step-number">{{ step.level }}</div>
              </div>
              <!-- 各色のスウォッチ -->
              <div 
                v-for="colorName in colorNames" 
                :key="`${colorName}-${index}`"
                class="gradient-swatch-cell"
              >
                <div 
                  v-if="colorScales[colorName] && colorScales[colorName][index]"
                  class="gradient-swatch" 
                  :class="{ 'base-color-swatch': colorScales[colorName][index]?.level === 50 }"
                  :style="{ background: colorScales[colorName][index]?.color }"
                  @mouseenter="showTooltip($event, colorScales[colorName][index])"
                  @mouseleave="hideTooltip"
                ></div>
              </div>
            </template>
          </template>
        </div>
      </section>
    </div>

    <!-- ツールチップ -->
    <div 
      v-if="tooltip.visible"
      class="tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-item">
          <span class="tooltip-label">oklch値:</span>
          <span class="tooltip-value code">{{ tooltip.oklch }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

// CSS変数から値を取得
const getCSSVariable = (name: string) => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

// 明度レベル範囲の設定（表示用）
const levelStart = 0
const levelStop = 100
const levelStep = 10

// oklch値からパラメータを抽出
const parseOklch = (oklchValue: string): { l: number; c: number; h: number } => {
  // oklch(0.81 0.135 260deg) の形式から値を抽出
  const match = oklchValue.match(/oklch\(([\d.]+)\s+([\d.]+)\s+([\d.]+)deg\)/)
  if (match) {
    return {
      l: parseFloat(match[1]),
      c: parseFloat(match[2]),
      h: parseFloat(match[3]),
    }
  }
  // フォールバック（パースに失敗した場合）
  return { l: 0, c: 0, h: 0 }
}

// CSS変数から利用可能な色名を動的に取得
const getAvailableColorNames = (): string[] => {
  const colorNameSet = new Set<string>()
  
  // すべてのCSS変数を取得
  Array.from(document.styleSheets).forEach(sheet => {
    try {
      Array.from(sheet.cssRules).forEach(rule => {
        if (rule instanceof CSSStyleRule && rule.selectorText === ':root') {
          Array.from(rule.style).forEach(prop => {
            // --base-{colorName}-hue のパターンを検索
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

// 色スケールを計算する共通関数
const calculateColorScale = (colorName: string) => {
  const steps = []
  
  // レベル範囲をループ（startからstopまで、step刻み）
  for (let level = levelStart; level <= levelStop; level += levelStep) {
    // レベル値をそのままCSS変数名に使用（0~100の範囲）
    const color = getCSSVariable(`--${colorName}-${level}`)
    
    // 空の場合はスキップ
    if (!color) continue
    
    // SCSSで計算されたoklch値からパラメータを抽出
    const { l, c, h } = parseOklch(color)
    
    steps.push({
      level,
      color,
      l,
      c,
      h,
    })
  }
  
  // 最後のステップがlevelStopに到達していない場合、明示的に追加
  const lastLevel = steps.length > 0 ? steps[steps.length - 1].level : levelStart
  if (lastLevel < levelStop) {
    const color = getCSSVariable(`--${colorName}-${levelStop}`)
    if (color) {
      const { l, c, h } = parseOklch(color)
      steps.push({
        level: levelStop,
        color,
        l,
        c,
        h,
      })
    }
  }
  
  return steps
}

// 利用可能な色名を取得
const colorNames = ref<string[]>([])

// すべての色のスケールを動的に計算
const colorScales = computed(() => {
  const scales: Record<string, ReturnType<typeof calculateColorScale>> = {}
  colorNames.value.forEach((colorName: string) => {
    scales[colorName] = calculateColorScale(colorName)
  })
  return scales
})

// コンポーネントマウント時に色名を取得
onMounted(() => {
  colorNames.value = getAvailableColorNames()
})

// ツールチップの状態
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  oklch: '',
})

// ツールチップを表示
const showTooltip = (event: MouseEvent, step: { level: number; color: string; l: number; c: number; h: number }) => {
  tooltip.value = {
    visible: true,
    x: event.clientX + 10,
    y: event.clientY + 10,
    oklch: step.color,
  }
}

// ツールチップを非表示
const hideTooltip = () => {
  tooltip.value.visible = false
}
</script>

<style lang="scss" scoped>
@import '../styles/_color';

$scale-cell-height: 50px;
$scale-gap: 0.25rem;

.color-palette {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.palette-header {
  margin-bottom: 3rem;

  h2 {
    margin: 0 0 0.5rem 0;
    color: oklch(0.25 0.01 0deg);
    font-size: 2rem;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: oklch(0.45 0.01 0deg);
    font-size: 1rem;
  }
}

.palette-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.color-section {
  background: oklch(1.0 0 0deg);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px oklch(0 0 0deg / 0.1);

  h3 {
    margin: 0 0 1.5rem 0;
    color: oklch(0.25 0.01 0deg);
    font-size: 1.5rem;
    font-weight: 600;
    border-bottom: 2px solid oklch(0.90 0.01 0deg);
    padding-bottom: 0.75rem;
  }
}

.gradient-grid {
  display: grid;
  grid-template-columns: 150px 1fr 1fr;
  grid-auto-rows: auto;
  gap: $scale-gap;
  background: oklch(1.0 0 0deg);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px oklch(0 0 0deg / 0.1);
}

.gradient-header {
  font-weight: 700;
  color: oklch(0.25 0.01 0deg);
  font-size: 0.875rem;
  text-align: center;
  padding: 0.5rem;
  background: oklch(0.97 0.005 0deg);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  box-sizing: border-box;
  min-height: 60px;
}

.header-label-sub {
  font-size: 0.75rem;
  font-weight: 400;
  color: oklch(0.45 0.01 0deg);
}

.gradient-step-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  color: oklch(0.25 0.01 0deg);
  background: oklch(0.97 0.005 0deg);
  box-sizing: border-box;
  min-height: $scale-cell-height;

  &.base-color {
    background: calc-color-primary(50);
    color: oklch(0.95 0 0deg);
  }
}

.step-number {
  font-weight: 700;
  font-size: 1rem;
}

.gradient-swatch-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 6px;
  box-sizing: border-box;
}

.gradient-swatch {
  width: 100%;
  height: 100%;
  min-height: $scale-cell-height;
  border-radius: 4px;
  box-shadow: 0 2px 4px oklch(0 0 0deg / 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px oklch(0 0 0deg / 0.1);
  }

  &.base-color-swatch {
    border: 2px solid calc-color-primary(50);
    // 基準色のoklch値に透明度を追加（hue: 260, chroma: 0.15, lightness: 0.9）
    box-shadow: 0 2px 8px oklch(0.9 0.15 260deg / 0.3);
  }
}

.gradient-param-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: oklch(0.25 0.01 0deg);
  box-sizing: border-box;
  min-height: $scale-cell-height;

  &.code {
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    color: oklch(0.45 0.01 0deg);
    word-break: break-all;
    text-align: center;
  }
}

// ツールチップ
.tooltip {
  position: fixed;
  z-index: 1000;
  pointer-events: none;
  background: oklch(0.20 0.01 0deg);
  border: 1px solid oklch(0.90 0.01 0deg);
  border-radius: 6px;
  padding: 0.75rem;
  box-shadow: 0 4px 16px oklch(0 0 0deg / 0.15);
  min-width: 200px;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tooltip-item {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: flex-start;
}

.tooltip-label {
  font-weight: 600;
  color: oklch(0.95 0 0deg);
  font-size: 0.875rem;
  white-space: nowrap;
}

.tooltip-value {
  color: oklch(0.95 0 0deg);
  font-size: 0.875rem;
  text-align: right;
  word-break: break-all;

  &.code {
    font-family: 'Courier New', monospace;
  }
}
</style>
