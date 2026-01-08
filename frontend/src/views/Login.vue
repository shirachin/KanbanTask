<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-6">
          <v-card-title class="text-h4 text-center mb-2">
            タスク管理アプリ
          </v-card-title>
          <v-card-subtitle class="text-center mb-4">
            ユーザー名を入力してください
          </v-card-subtitle>
          <v-form @submit.prevent="handleLogin">
            <v-text-field
              v-model="username"
              label="ユーザー名"
              placeholder="ユーザー名を入力（半角英数字のみ）"
              :rules="[rules.required, rules.alphanumeric]"
              autofocus
              @input="handleInput"
              class="mb-4"
            />
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
            >
              ログイン
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { setLocalStorage, STORAGE_KEYS } from '../composables/useLocalStorage'

const username = ref('')

const rules = {
  required: (value: string) => !!value || 'ユーザー名は必須です',
  alphanumeric: (value: string) => {
    if (!value) return true
    return /^[a-zA-Z0-9]+$/.test(value) || '半角英数字のみ入力可能です'
  },
}

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

