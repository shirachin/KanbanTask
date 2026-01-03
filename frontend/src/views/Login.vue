<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">タスク管理アプリ</h1>
      <p class="login-subtitle">ユーザー名を入力してください</p>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">ユーザー名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            placeholder="ユーザー名を入力（半角英数字のみ）"
            pattern="[a-zA-Z0-9]+"
            required
            autofocus
            @input="handleInput"
          />
        </div>
        <button type="submit" class="login-button">ログイン</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { setLocalStorage, STORAGE_KEYS } from '../composables/useLocalStorage'

const username = ref('')

// 半角英数字のみを許可
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  // 半角英数字以外の文字を削除
  const filteredValue = value.replace(/[^a-zA-Z0-9]/g, '')
  if (value !== filteredValue) {
    username.value = filteredValue
    target.value = filteredValue
  }
}

const handleLogin = () => {
  const trimmedUsername = username.value.trim()
  // 半角英数字のみで、かつ空でないことを確認
  if (trimmedUsername && /^[a-zA-Z0-9]+$/.test(trimmedUsername)) {
    // LocalStorageに保存
    setLocalStorage(STORAGE_KEYS.APP_CURRENT_USER, trimmedUsername)
    // ページをリロードしてApp.vueで状態を読み込む
    window.location.reload()
  }
}
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--current-mainBackground);
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--current-backgroundLight);
  border-radius: 12px;
  padding: 3rem 2.5rem;
  box-shadow: 0 4px 16px var(--current-shadowLg);
}

.login-title {
  margin: 0 0 0.5rem 0;
  color: var(--current-textPrimary);
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
}

.login-subtitle {
  margin: 0 0 2rem 0;
  color: var(--current-textSecondary);
  font-size: 1rem;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 6px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:focus {
    outline: none;
    border-color: var(--current-activeBackground);
    box-shadow: 0 0 0 3px var(--current-activeBackground)33;
  }

  &::placeholder {
    color: var(--current-textSecondary);
    opacity: 0.6;
  }
}

.login-button {
  width: 100%;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: var(--current-activeBackground);
  color: var(--current-textWhite);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;

  &:hover {
    background: var(--current-linkHoverColor);
  }

  &:active {
    transform: scale(0.98);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px var(--current-activeBackground)33;
  }
}
</style>
