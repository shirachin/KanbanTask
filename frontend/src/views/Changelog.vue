<template>
  <div class="changelog">
    <div class="changelog-header">
      <h2>更新情報</h2>
    </div>
    
    <div class="changelog-content">
      <div class="tabs-container">
        <div class="tabs">
          <button
            v-for="version in versions"
            :key="version.id"
            class="tab-button"
            :class="{ active: selectedVersionId === version.id }"
            @click="selectedVersionId = version.id"
          >
            {{ version.version }}
          </button>
        </div>
      </div>
      
      <div class="version-section" v-for="version in versions" :key="version.id" v-show="selectedVersionId === version.id">
        <h3 class="version-title">{{ version.version }}</h3>
        <p class="version-date">{{ version.date }}</p>
        <div 
          v-for="category in version.categories" 
          :key="category.title" 
          class="changelog-category"
        >
          <h4 class="category-title">{{ category.title }}</h4>
        <ul class="changelog-list">
            <li v-for="(item, index) in category.items" :key="index" v-html="item"></li>
        </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface ChangelogCategory {
  title: string
  items: string[]
}

interface VersionData {
  id: string
  version: string
  date: string
  categories: ChangelogCategory[]
}

const versions: VersionData[] = [
  {
    id: '0.1.2',
    version: 'β0.1.2',
    date: '2026年1月4日',
    categories: [
      {
        title: 'フロントエンド機能',
        items: [
          '<strong>カンバンボード</strong>:<ul class="nested-list"><li>タスク編集モーダルに削除機能を追加（削除ボタン、確認ダイアログ付き）</li></ul>'
        ]
      },
      {
        title: 'バックエンド機能',
        items: [
          '<strong>ステータス管理</strong>:<ul class="nested-list"><li>ステータスをすべてのプロジェクト・個人タスクで共通化（7種類の共通ステータスのみ使用）</li><li>プロジェクト作成時にステータスを自動作成しない仕様に変更</li><li>ステータス取得APIを共通ステータスを返すように修正</li></ul>'
        ]
      }
    ]
  },
  {
    id: '0.1.1',
    version: 'β0.1.1',
    date: '2026年1月4日',
    categories: [
      {
        title: 'フロントエンド機能',
        items: [
          '<strong>カンバンボード</strong>:<ul class="nested-list"><li>タスク作成モーダルのプロジェクト選択をオートコンプリート形式に変更（検索機能、キーボードナビゲーション対応）</li></ul>',
          '<strong>TODOリスト</strong>:<ul class="nested-list"><li>フィルタテンプレートボタンにマウスオーバーで適用するフィルタ設定を表示するツールチップ機能を追加</li><li>フィルタテンプレートに「リセット」ボタンを追加（フィルタ・ソートをすべてリセット）</li></ul>'
        ]
      }
    ]
  },
  {
    id: '0.1.0',
    version: 'β0.1.0',
    date: '2026年1月4日',
    categories: [
          {
            title: 'フロントエンド機能',
            items: [
              '<strong>ログイン機能</strong>: ユーザー名によるログイン（半角英数字のみ）、ユーザー名の自動保存',
              '<strong>ダッシュボード</strong>: プロジェクト一覧とタスク統計情報の表示（簡易版）',
              '<strong>カンバンボード</strong>:<ul class="nested-list"><li>プロジェクトモード選択（すべてのプロジェクト+個人的タスク、プロジェクト検索、個人的タスク）</li><li>プロジェクト検索機能（Autocomplete風、キーボードナビゲーション対応）</li><li>担当者フィルタリング</li><li>タスクの作成・編集（モーダル）</li><li>ステータスごとのタスク表示</li><li>TODOの追加・削除</li><li>TODOの完了状態管理（実行完了日で自動管理）</li></ul>',
              '<strong>TODOリスト</strong>:<ul class="nested-list"><li>AG Gridを使用した表形式表示</li><li>フィルタテンプレート機能</li><li>カラムごとのフィルタ・ソート機能</li><li>ページネーション（25、50、100、200件）</li><li>カラム状態の保存（幅、表示/非表示）</li><li>チェックボックスによる完了状態の切り替え</li><li>設定の自動保存（LocalStorage）</li></ul>',
              '<strong>プロジェクト管理</strong>:<ul class="nested-list"><li>AG Gridを使用したプロジェクト一覧表示</li><li>プロジェクトの作成・編集・削除（モーダル）</li><li>担当者の管理（複数選択可能）</li><li>カラムごとのフィルタ・ソート機能</li><li>ページネーション（25、50、100、200件）</li><li>カラム状態の保存（幅、表示/非表示）</li><li>設定の自動保存（LocalStorage）</li></ul>',
              '<strong>ガントチャート</strong>: 未実装（今後実装予定）',
              '<strong>テーマ切り替え</strong>: ヘッダーからテーマを切り替え可能、設定の自動保存',
              '<strong>ナビゲーション</strong>: サイドバーナビゲーション、ユーザー情報表示、ログアウト機能',
              '<strong>使い方ページ</strong>: 各機能の使い方を説明',
              '<strong>状態管理</strong>: LocalStorageによる各種設定の自動保存（ユーザー名、表示ページ、テーマ、フィルタ・ソート設定など）'
            ]
          },
      {
        title: 'バックエンド機能',
        items: [
          '<strong>API v1</strong>: RESTful APIエンドポイント（/api/v1）',
          '<strong>タスク管理API</strong>: タスクのCRUD操作、TODO管理',
          '<strong>プロジェクト管理API</strong>: プロジェクトのCRUD操作、担当者管理',
          '<strong>ステータス管理API</strong>: ステータスのCRUD操作、プロジェクトごとのステータス管理',
          '<strong>TODO管理API</strong>: TODOのCRUD操作、タスクごとのTODO管理',
          '<strong>個人タスク対応</strong>: プロジェクトID=-1で個人タスクを管理',
          '<strong>エラーハンドリング</strong>: 適切なHTTPステータスコードとエラーメッセージの返却',
          '<strong>データベース制約エラー処理</strong>: IntegrityError、SQLAlchemyErrorの適切な処理',
          '<strong>CORS対応</strong>: フロントエンドからのアクセスを許可',
          '<strong>コード構造</strong>: モジュール化された構造（core、models、schemas、api）'
        ]
      },
      {
        title: '技術スタック',
        items: [
          '<strong>フロントエンド</strong>: Vue.js 3、Vite、AG Grid Vue 3、TypeScript',
          '<strong>バックエンド</strong>: FastAPI、Python 3.11、SQLAlchemy',
          '<strong>データベース</strong>: PostgreSQL 15',
          '<strong>コンテナ</strong>: Docker、Docker Compose'
        ]
      }
    ]
  }
]

const selectedVersionId = ref<string>(versions[0].id)

const selectedVersion = computed(() => {
  return versions.find(v => v.id === selectedVersionId.value) || versions[0]
})
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.changelog {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.changelog-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.changelog-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.tabs-container {
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--current-borderColor);
}

.tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
  position: relative;

  &:hover {
    color: var(--current-textPrimary);
  }

  &.active {
    color: var(--current-textPrimary);
    border-bottom-color: var(--current-activeBackground);
    font-weight: 600;
  }
}

.version-section {
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.version-title {
  margin: 0 0 0.5rem 0;
  color: var(--current-textPrimary);
  font-size: 1.5rem;
  font-weight: 600;
}

.version-date {
  margin: 0 0 1rem 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
}

.changelog-category {
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.category-title {
  margin: 0 0 1rem 0;
  color: var(--current-textPrimary);
  font-size: 1.125rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--current-borderColor);
}

.changelog-list {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--current-textPrimary);
  line-height: 1.8;

  li {
    margin-bottom: 0.75rem;

    &:last-child {
      margin-bottom: 0;
    }

    strong {
      font-weight: 600;
    }
  }
}

.nested-list {
  margin: 0.5rem 0 0 1.5rem;
  padding-left: 1rem;
  list-style-type: disc;

  li {
    margin-bottom: 0.5rem;
    line-height: 1.6;
  }
}
</style>
