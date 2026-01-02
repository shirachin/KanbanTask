<template>
  <div class="color-palette">
    <div class="palette-header">
      <h2>カラーパレット</h2>
      <p>アプリケーションで使用されている色の一覧です</p>
    </div>

    <div class="palette-content">
      <!-- 設定値表示 -->
      <section class="color-section">
        <h3>カラー設定値</h3>
        <div class="config-grid">
          <div 
            v-for="config in colorConfigs" 
            :key="config.name"
            class="config-card"
          >
            <div class="config-header">{{ config.label }}</div>
            <div class="config-content">
              <div class="config-item">
                <span class="config-label">色相 (Hue):</span>
                <span class="config-value">{{ config.hueRaw }}</span>
              </div>
              <div class="config-item">
                <span class="config-label">彩度 (Chroma):</span>
                <span class="config-value">{{ config.chromaRaw }}</span>
              </div>
              <div class="config-item">
                <span class="config-label">明度段階:</span>
                <span class="config-value">0.0 ～ 1.0 (0.1刻み)</span>
              </div>
              <div class="config-item">
                <span class="config-label">SCSS変数:</span>
                <span class="config-value code">$hue-{{ config.name }}: {{ config.hueRaw }};<br>$chroma-{{ config.name }}: {{ config.chromaRaw }};</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 11段階の色スケール（5色相を横並び） -->
      <section class="color-section">
        <h3>カラースケール（11段階）</h3>
        <div class="color-scale-grid">
          <!-- 行ヘッダー列 -->
          <div class="scale-row-header-column">
            <div class="scale-column-header"></div>
            <div 
              v-for="i in 11" 
              :key="`row-header-${i - 1}`"
              class="scale-row-header"
            >
              {{ i - 1 }}
            </div>
          </div>

          <!-- プライマリカラー列 -->
          <div class="scale-column">
            <div class="scale-column-header">プライマリ</div>
            <div 
              v-for="i in 11" 
              :key="`primary-${i - 1}`"
              class="scale-cell"
            >
              <div 
                class="scale-swatch" 
                :style="{ background: $primaryScale[i - 1] }"
              ></div>
            </div>
          </div>

          <!-- セカンダリカラー列 -->
          <div class="scale-column">
            <div class="scale-column-header">セカンダリ</div>
            <div 
              v-for="i in 11" 
              :key="`secondary-${i - 1}`"
              class="scale-cell"
            >
              <div 
                class="scale-swatch" 
                :style="{ background: $secondaryScale[i - 1] }"
              ></div>
            </div>
          </div>

          <!-- 成功カラー列 -->
          <div class="scale-column">
            <div class="scale-column-header">成功</div>
            <div 
              v-for="i in 11" 
              :key="`success-${i - 1}`"
              class="scale-cell"
            >
              <div 
                class="scale-swatch" 
                :style="{ background: $successScale[i - 1] }"
              ></div>
            </div>
          </div>

          <!-- 危険カラー列 -->
          <div class="scale-column">
            <div class="scale-column-header">危険</div>
            <div 
              v-for="i in 11" 
              :key="`danger-${i - 1}`"
              class="scale-cell"
            >
              <div 
                class="scale-swatch" 
                :style="{ background: $dangerScale[i - 1] }"
              ></div>
            </div>
          </div>

          <!-- ニュートラルカラー列 -->
          <div class="scale-column">
            <div class="scale-column-header">ニュートラル</div>
            <div 
              v-for="i in 11" 
              :key="`neutral-${i - 1}`"
              class="scale-cell"
            >
              <div 
                class="scale-swatch" 
                :style="{ background: $neutralScale[i - 1], border: i === 11 ? `1px solid ${$borderColor}` : 'none' }"
              ></div>
            </div>
          </div>
        </div>
      </section>

      <!-- プライマリカラー -->
      <section class="color-section">
        <h3>プライマリカラー</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $primaryColor }"></div>
            <div class="color-info">
              <div class="color-name">primary-color</div>
              <div class="color-value">{{ $primaryColor }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $primaryHover }"></div>
            <div class="color-info">
              <div class="color-name">primary-hover</div>
              <div class="color-value">{{ $primaryHover }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch gradient" :style="{ background: `linear-gradient(135deg, ${$primaryGradientStart} 0%, ${$primaryGradientEnd} 100%)` }"></div>
            <div class="color-info">
              <div class="color-name">primary-gradient</div>
              <div class="color-value">{{ $primaryGradientStart }} → {{ $primaryGradientEnd }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- セカンダリカラー -->
      <section class="color-section">
        <h3>セカンダリカラー</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $secondaryColor }"></div>
            <div class="color-info">
              <div class="color-name">secondary-color</div>
              <div class="color-value">{{ $secondaryColor }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $secondaryHover }"></div>
            <div class="color-info">
              <div class="color-name">secondary-hover</div>
              <div class="color-value">{{ $secondaryHover }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 成功カラー -->
      <section class="color-section">
        <h3>成功カラー</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $successColor }"></div>
            <div class="color-info">
              <div class="color-name">success-color</div>
              <div class="color-value">{{ $successColor }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $successHover }"></div>
            <div class="color-info">
              <div class="color-name">success-hover</div>
              <div class="color-value">{{ $successHover }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 危険カラー -->
      <section class="color-section">
        <h3>危険カラー</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $dangerColor }"></div>
            <div class="color-info">
              <div class="color-name">danger-color</div>
              <div class="color-value">{{ $dangerColor }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $dangerHover }"></div>
            <div class="color-info">
              <div class="color-name">danger-hover</div>
              <div class="color-value">{{ $dangerHover }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 背景色 -->
      <section class="color-section">
        <h3>背景色</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $backgroundDark }"></div>
            <div class="color-info">
              <div class="color-name">background-dark</div>
              <div class="color-value">{{ $backgroundDark }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $backgroundLight, border: `1px solid ${$borderColor}` }"></div>
            <div class="color-info">
              <div class="color-name">background-light</div>
              <div class="color-value">{{ $backgroundLight }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $backgroundGray }"></div>
            <div class="color-info">
              <div class="color-name">background-gray</div>
              <div class="color-value">{{ $backgroundGray }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $backgroundGrayHover }"></div>
            <div class="color-info">
              <div class="color-name">background-gray-hover</div>
              <div class="color-value">{{ $backgroundGrayHover }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- テキスト色 -->
      <section class="color-section">
        <h3>テキスト色</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $textPrimary }"></div>
            <div class="color-info">
              <div class="color-name">text-primary</div>
              <div class="color-value">{{ $textPrimary }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $textSecondary }"></div>
            <div class="color-info">
              <div class="color-name">text-secondary</div>
              <div class="color-value">{{ $textSecondary }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $textTertiary }"></div>
            <div class="color-info">
              <div class="color-name">text-tertiary</div>
              <div class="color-value">{{ $textTertiary }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $textWhite }"></div>
            <div class="color-info">
              <div class="color-name">text-white</div>
              <div class="color-value">{{ $textWhite }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- ボーダー色 -->
      <section class="color-section">
        <h3>ボーダー色</h3>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $borderColor }"></div>
            <div class="color-info">
              <div class="color-name">border-color</div>
              <div class="color-value">{{ $borderColor }}</div>
            </div>
          </div>
          <div class="color-item">
            <div class="color-swatch" :style="{ background: $borderLight }"></div>
            <div class="color-info">
              <div class="color-name">border-light</div>
              <div class="color-value">{{ $borderLight }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- シャドウ -->
      <section class="color-section">
        <h3>シャドウ</h3>
        <div class="shadow-grid">
          <div class="shadow-item">
            <div class="shadow-demo" :style="{ boxShadow: $shadowSm }">
              <div class="shadow-label">shadow-sm</div>
            </div>
            <div class="shadow-value">{{ $shadowSm }}</div>
          </div>
          <div class="shadow-item">
            <div class="shadow-demo" :style="{ boxShadow: $shadowMd }">
              <div class="shadow-label">shadow-md</div>
            </div>
            <div class="shadow-value">{{ $shadowMd }}</div>
          </div>
          <div class="shadow-item">
            <div class="shadow-demo" :style="{ boxShadow: $shadowLg }">
              <div class="shadow-label">shadow-lg</div>
            </div>
            <div class="shadow-value">{{ $shadowLg }}</div>
          </div>
          <div class="shadow-item">
            <div class="shadow-demo" :style="{ boxShadow: $shadowPrimary }">
              <div class="shadow-label">shadow-primary</div>
            </div>
            <div class="shadow-value">{{ $shadowPrimary }}</div>
          </div>
          <div class="shadow-item">
            <div class="shadow-demo" :style="{ boxShadow: $shadowPrimarySm }">
              <div class="shadow-label">shadow-primary-sm</div>
            </div>
            <div class="shadow-value">{{ $shadowPrimarySm }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// CSS変数から値を取得
const getCSSVariable = (name: string) => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

// 数値として取得（degや単位を除去）
const getCSSVariableNumber = (name: string) => {
  const value = getCSSVariable(name)
  return parseFloat(value.replace(/deg|%|px/g, ''))
}

// プライマリカラー
const $primaryColor = computed(() => getCSSVariable('--primary-color'))
const $primaryHover = computed(() => getCSSVariable('--primary-hover'))
const $primaryGradientStart = computed(() => getCSSVariable('--primary-gradient-start'))
const $primaryGradientEnd = computed(() => getCSSVariable('--primary-gradient-end'))

// セカンダリカラー
const $secondaryColor = computed(() => getCSSVariable('--secondary-color'))
const $secondaryHover = computed(() => getCSSVariable('--secondary-hover'))

// 成功カラー
const $successColor = computed(() => getCSSVariable('--success-color'))
const $successHover = computed(() => getCSSVariable('--success-hover'))

// 危険カラー
const $dangerColor = computed(() => getCSSVariable('--danger-color'))
const $dangerHover = computed(() => getCSSVariable('--danger-hover'))

// 背景色
const $backgroundDark = computed(() => getCSSVariable('--background-dark'))
const $backgroundLight = computed(() => getCSSVariable('--background-light'))
const $backgroundGray = computed(() => getCSSVariable('--background-gray'))
const $backgroundGrayHover = computed(() => getCSSVariable('--background-gray-hover'))

// テキスト色
const $textPrimary = computed(() => getCSSVariable('--text-primary'))
const $textSecondary = computed(() => getCSSVariable('--text-secondary'))
const $textTertiary = computed(() => getCSSVariable('--text-tertiary'))
const $textWhite = computed(() => getCSSVariable('--text-white'))

// ボーダー色
const $borderColor = computed(() => getCSSVariable('--border-color'))
const $borderLight = computed(() => getCSSVariable('--border-light'))

// シャドウ
const $shadowSm = computed(() => getCSSVariable('--shadow-sm'))
const $shadowMd = computed(() => getCSSVariable('--shadow-md'))
const $shadowLg = computed(() => getCSSVariable('--shadow-lg'))
const $shadowPrimary = computed(() => getCSSVariable('--shadow-primary'))
const $shadowPrimarySm = computed(() => getCSSVariable('--shadow-primary-sm'))

// 11段階の色スケール
const $primaryScale = computed(() => [
  getCSSVariable('--primary-0'),
  getCSSVariable('--primary-1'),
  getCSSVariable('--primary-2'),
  getCSSVariable('--primary-3'),
  getCSSVariable('--primary-4'),
  getCSSVariable('--primary-5'),
  getCSSVariable('--primary-6'),
  getCSSVariable('--primary-7'),
  getCSSVariable('--primary-8'),
  getCSSVariable('--primary-9'),
  getCSSVariable('--primary-10'),
])

const $secondaryScale = computed(() => [
  getCSSVariable('--secondary-0'),
  getCSSVariable('--secondary-1'),
  getCSSVariable('--secondary-2'),
  getCSSVariable('--secondary-3'),
  getCSSVariable('--secondary-4'),
  getCSSVariable('--secondary-5'),
  getCSSVariable('--secondary-6'),
  getCSSVariable('--secondary-7'),
  getCSSVariable('--secondary-8'),
  getCSSVariable('--secondary-9'),
  getCSSVariable('--secondary-10'),
])

const $successScale = computed(() => [
  getCSSVariable('--success-0'),
  getCSSVariable('--success-1'),
  getCSSVariable('--success-2'),
  getCSSVariable('--success-3'),
  getCSSVariable('--success-4'),
  getCSSVariable('--success-5'),
  getCSSVariable('--success-6'),
  getCSSVariable('--success-7'),
  getCSSVariable('--success-8'),
  getCSSVariable('--success-9'),
  getCSSVariable('--success-10'),
])

const $dangerScale = computed(() => [
  getCSSVariable('--danger-0'),
  getCSSVariable('--danger-1'),
  getCSSVariable('--danger-2'),
  getCSSVariable('--danger-3'),
  getCSSVariable('--danger-4'),
  getCSSVariable('--danger-5'),
  getCSSVariable('--danger-6'),
  getCSSVariable('--danger-7'),
  getCSSVariable('--danger-8'),
  getCSSVariable('--danger-9'),
  getCSSVariable('--danger-10'),
])

const $neutralScale = computed(() => [
  getCSSVariable('--neutral-0'),
  getCSSVariable('--neutral-1'),
  getCSSVariable('--neutral-2'),
  getCSSVariable('--neutral-3'),
  getCSSVariable('--neutral-4'),
  getCSSVariable('--neutral-5'),
  getCSSVariable('--neutral-6'),
  getCSSVariable('--neutral-7'),
  getCSSVariable('--neutral-8'),
  getCSSVariable('--neutral-9'),
  getCSSVariable('--neutral-10'),
])

// 設定値表示用（SCSS変数からCSS変数を経由して取得）
const colorConfigs = computed(() => [
  {
    name: 'primary',
    label: 'プライマリ',
    hue: getCSSVariableNumber('--hue-primary'),
    chroma: getCSSVariableNumber('--chroma-primary'),
    hueRaw: getCSSVariable('--hue-primary'),
    chromaRaw: getCSSVariable('--chroma-primary'),
  },
  {
    name: 'secondary',
    label: 'セカンダリ',
    hue: getCSSVariableNumber('--hue-secondary'),
    chroma: getCSSVariableNumber('--chroma-secondary'),
    hueRaw: getCSSVariable('--hue-secondary'),
    chromaRaw: getCSSVariable('--chroma-secondary'),
  },
  {
    name: 'success',
    label: '成功',
    hue: getCSSVariableNumber('--hue-success'),
    chroma: getCSSVariableNumber('--chroma-success'),
    hueRaw: getCSSVariable('--hue-success'),
    chromaRaw: getCSSVariable('--chroma-success'),
  },
  {
    name: 'danger',
    label: '危険',
    hue: getCSSVariableNumber('--hue-danger'),
    chroma: getCSSVariableNumber('--chroma-danger'),
    hueRaw: getCSSVariable('--hue-danger'),
    chromaRaw: getCSSVariable('--chroma-danger'),
  },
  {
    name: 'neutral',
    label: 'ニュートラル',
    hue: getCSSVariableNumber('--hue-neutral'),
    chroma: getCSSVariableNumber('--chroma-neutral'),
    hueRaw: getCSSVariable('--hue-neutral'),
    chromaRaw: getCSSVariable('--chroma-neutral'),
  },
])
</script>

<style lang="scss" scoped>
@import '../styles/_color';

.color-palette {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.palette-header {
  margin-bottom: 3rem;

  h2 {
    margin: 0 0 0.5rem 0;
    color: $text-primary;
    font-size: 2rem;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: $text-secondary;
    font-size: 1rem;
  }
}

.palette-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.color-section {
  background: $background-light;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: $shadow-md;

  h3 {
    margin: 0 0 1.5rem 0;
    color: $text-primary;
    font-size: 1.5rem;
    font-weight: 600;
    border-bottom: 2px solid $border-color;
    padding-bottom: 0.75rem;
  }
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.color-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.color-swatch {
  width: 100%;
  height: 120px;
  border-radius: 8px;
  box-shadow: $shadow-sm;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.02);
  }
}

.color-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.color-name {
  font-weight: 600;
  color: $text-primary;
  font-size: 0.9rem;
}

.color-value {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: $text-secondary;
  word-break: break-all;
}

.shadow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

.shadow-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: center;
}

.shadow-demo {
  width: 120px;
  height: 120px;
  background: $background-light;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.05);
  }
}

.shadow-label {
  font-weight: 600;
  color: $text-primary;
  font-size: 0.9rem;
}

.shadow-value {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  color: $text-secondary;
  text-align: center;
  word-break: break-all;
}

// 11段階の色スケール用スタイル（画像のようなレイアウト）
.color-scale-grid {
  display: grid;
  grid-template-columns: 60px repeat(5, 1fr);
  gap: 0.5rem;
  background: $background-light;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: $shadow-sm;
}

.scale-row-header-column {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.scale-row-header {
  font-weight: 700;
  color: $text-primary;
  font-size: 0.875rem;
  text-align: center;
  padding: 0.5rem;
  background: $background-gray;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.scale-column {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.scale-column-header {
  font-weight: 700;
  color: $text-primary;
  font-size: 1rem;
  text-align: center;
  padding: 0.5rem;
  background: $background-gray;
  border-radius: 6px;
  margin-bottom: 0.25rem;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scale-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background-color 0.2s;
  height: 40px;

  &:hover {
    background-color: $background-gray;
  }
}

.scale-swatch {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  box-shadow: $shadow-sm;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;

  &:hover {
    transform: scale(1.05);
    box-shadow: $shadow-md;
  }
}

// 設定値表示用スタイル
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.config-card {
  background: $background-light;
  border: 1px solid $border-color;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: $shadow-sm;
}

.config-header {
  font-weight: 700;
  color: $text-white;
  background: $primary-color;
  padding: 0.75rem 1rem;
  font-size: 1rem;
}

.config-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.config-label {
  font-weight: 600;
  color: $text-primary;
  font-size: 0.875rem;
}

.config-value {
  color: $text-secondary;
  font-size: 0.875rem;
  font-family: 'Courier New', monospace;

  &.code {
    background: $background-gray;
    padding: 0.5rem;
    border-radius: 4px;
    white-space: pre-wrap;
    line-height: 1.5;
  }
}
</style>
