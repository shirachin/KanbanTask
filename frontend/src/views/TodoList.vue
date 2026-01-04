<template>
  <div class="todo-list">
    <div class="todo-header">
      <h2>TODOリスト</h2>
      <div class="filter-templates">
        <span class="filter-templates-label">フィルタテンプレート:</span>
        <div
          v-for="template in filterTemplates"
          :key="template.id"
          class="filter-template-wrapper"
        >
          <button
            class="filter-template-button"
            @click="applyFilterTemplate(template)"
            @mouseenter="showTooltip(template)"
            @mouseleave="hideTooltip"
          >
            {{ template.name }}
          </button>
          <div
            v-if="hoveredTemplate?.id === template.id && tooltipText"
            class="filter-template-tooltip"
          >
            {{ tooltipText }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="todo-content">
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div class="todo-section">
        <div v-if="loading && todoListData.length === 0" class="loading-message">
          読み込み中...
        </div>
        <AgGridVue
          v-else
          ref="gridRef"
          :rowData="todoListData"
          :columnDefs="columnDefs"
          :defaultColDef="defaultColDef"
          :context="gridContext"
          :pagination="true"
          :paginationPageSize="paginationPageSize"
          :paginationPageSizeSelector="[25, 50, 100, 200]"
          @columnStateChanged="onColumnStateChanged"
          @filterChanged="onFilterChanged"
          @paginationChanged="onPaginationChanged"
          @sortChanged="onSortChanged"
          @firstDataRendered="onFirstDataRendered"
          @gridReady="onGridReady"
          class="ag-theme-quartz"
          style="height: 600px; width: 100%;"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, defineComponent, h, nextTick } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ICellRendererParams, ColumnState, FilterModel } from 'ag-grid-community'
import { useTodos, type Todo } from '../composables/useTodos'
import { useTasks, type Task } from '../composables/useTasks'
import { useProjects, type Project } from '../composables/useProjects'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// LocalStorage管理
import { getLocalStorage, setLocalStorage, STORAGE_KEYS } from '../composables/useLocalStorage'

// Composables
const { todos, loading, error, fetchTodos, fetchAllTodos, updateTodo, getTodos } = useTodos()
const { tasks, fetchTasks } = useTasks()
const { projects, fetchProjects } = useProjects()

// AG Gridの参照
const gridRef = ref<InstanceType<typeof AgGridVue> | null>(null)

// ページネーションサイズ
import { DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS, MAX_RETRY_COUNT, RESTORE_STATE_TIMEOUTS } from '../constants/grid'

const savedPageSize = getLocalStorage<number>(STORAGE_KEYS.TODO_LIST_PAGE_SIZE, DEFAULT_PAGE_SIZE)
const paginationPageSize = ref<number>(PAGE_SIZE_OPTIONS.includes(savedPageSize as typeof PAGE_SIZE_OPTIONS[number]) ? savedPageSize : DEFAULT_PAGE_SIZE)

// 初期化フラグ（初期化時のイベントを無視するため）
const isInitializing = ref(true)

// カラム状態（ソート、表示/非表示、幅など）
const savedColumnState = getLocalStorage<ColumnState[]>(STORAGE_KEYS.TODO_LIST_COLUMN_STATE, [])
const columnState = ref<ColumnState[]>(savedColumnState)

// ソートモデル（ソート状態を保存するため）
interface SortModel {
  colId: string
  sort: 'asc' | 'desc'
}
const savedSortModel = getLocalStorage<SortModel[]>(STORAGE_KEYS.TODO_LIST_SORT_MODEL, [])
const sortModel = ref<SortModel[]>(savedSortModel)

// フィルタモデル
const savedFilterModel = getLocalStorage<FilterModel>(STORAGE_KEYS.TODO_LIST_FILTER_MODEL, {})
const filterModel = ref<FilterModel>(savedFilterModel)

// フィルタテンプレートの定義
interface FilterTemplate {
  id: string
  name: string
  sortModel: Array<{ colId: string; sort: 'asc' | 'desc' }>
  filterModel?: FilterModel
}

const filterTemplates: FilterTemplate[] = [
  {
    id: 'default',
    name: 'デフォルト',
    sortModel: [
      { colId: 'completed', sort: 'asc' },
      { colId: 'scheduled_date', sort: 'asc' },
    ],
  },
]

// カラム名のマッピング（colId -> headerName）
const columnNameMap: Record<string, string> = {
  'completed': '完了',
  'title': 'TODO',
  'task_name': 'タスク名',
  'project_name': 'プロジェクト名',
  'scheduled_date': '実行予定日',
  'completed_date': '実行完了日',
}

// ツールチップ表示用の状態
const hoveredTemplate = ref<FilterTemplate | null>(null)
const tooltipText = ref<string>('')

// フィルタ設定を人間が読める形式に変換
const formatFilterSettings = (template: FilterTemplate): string => {
  const parts: string[] = []
  
  // ソート設定
  if (template.sortModel && template.sortModel.length > 0) {
    const sortParts = template.sortModel.map((sort, index) => {
      const columnName = columnNameMap[sort.colId] || sort.colId
      const sortDirection = sort.sort === 'asc' ? '昇順' : '降順'
      return index === 0 
        ? `${columnName}（${sortDirection}）`
        : ` → ${columnName}（${sortDirection}）`
    })
    parts.push(`ソート: ${sortParts.join('')}`)
  }
  
  // フィルタ設定
  if (template.filterModel && Object.keys(template.filterModel).length > 0) {
    const filterParts: string[] = []
    for (const [colId, filter] of Object.entries(template.filterModel)) {
      const columnName = columnNameMap[colId] || colId
      const filterType = (filter as any).filterType || 'text'
      
      if (filterType === 'set') {
        // Setフィルタ（複数選択）
        const values = (filter as any).values || []
        if (values.length > 0) {
          filterParts.push(`${columnName}: ${values.join(', ')}`)
        }
      } else if (filterType === 'text') {
        // テキストフィルタ
        const type = (filter as any).type || 'contains'
        const filterText = (filter as any).filter || ''
        if (filterText) {
          const typeMap: Record<string, string> = {
            'contains': 'を含む',
            'equals': 'と等しい',
            'notEqual': 'と等しくない',
            'startsWith': 'で始まる',
            'endsWith': 'で終わる',
          }
          filterParts.push(`${columnName}: "${filterText}"${typeMap[type] || ''}`)
        }
      } else if (filterType === 'date') {
        // 日付フィルタ
        const type = (filter as any).type || 'equals'
        const dateFrom = (filter as any).dateFrom
        const dateTo = (filter as any).dateTo
        const typeMap: Record<string, string> = {
          'equals': 'と等しい',
          'notEqual': 'と等しくない',
          'lessThan': 'より前',
          'greaterThan': 'より後',
          'inRange': 'の範囲内',
        }
        if (dateFrom && dateTo) {
          filterParts.push(`${columnName}: ${dateFrom} ～ ${dateTo}`)
        } else if (dateFrom) {
          filterParts.push(`${columnName}: ${dateFrom}${typeMap[type] || ''}`)
        } else if (dateTo) {
          filterParts.push(`${columnName}: ${dateTo}${typeMap[type] || ''}`)
        }
      }
    }
    if (filterParts.length > 0) {
      parts.push(`フィルタ: ${filterParts.join('、')}`)
    }
  }
  
  if (parts.length === 0) {
    return '設定なし'
  }
  
  return parts.join('\n')
}

// ツールチップを表示
const showTooltip = (template: FilterTemplate) => {
  hoveredTemplate.value = template
  tooltipText.value = formatFilterSettings(template)
}

// ツールチップを非表示
const hideTooltip = () => {
  hoveredTemplate.value = null
  tooltipText.value = ''
}

// フィルタテンプレートを適用する関数
const applyFilterTemplate = (template: FilterTemplate) => {
  if (!gridRef.value?.api) return
  
  isInitializing.value = true
  
  try {
    // ソートモデルを適用
    if (template.sortModel && template.sortModel.length > 0) {
      const sortColumnState = template.sortModel.map((sort, index) => ({
        colId: sort.colId,
        sort: sort.sort,
        sortIndex: index,
      }))
      
      if (typeof gridRef.value.api.applyColumnState === 'function') {
        gridRef.value.api.applyColumnState({ 
          state: sortColumnState,
          applyOrder: false
        })
      }
      
      // LocalStorageに保存（テンプレート適用時も確実に保存）
      sortModel.value = template.sortModel
      setLocalStorage(STORAGE_KEYS.TODO_LIST_SORT_MODEL, template.sortModel)
    } else {
      // ソートをクリア
      sortModel.value = []
      setLocalStorage(STORAGE_KEYS.TODO_LIST_SORT_MODEL, null)
    }
    
    // フィルタモデルを適用（指定されている場合）
    if (template.filterModel && Object.keys(template.filterModel).length > 0) {
      if (typeof gridRef.value.api.setFilterModel === 'function') {
        gridRef.value.api.setFilterModel(template.filterModel)
      }
      
      // LocalStorageに保存（テンプレート適用時も確実に保存）
      filterModel.value = template.filterModel
      setLocalStorage(STORAGE_KEYS.TODO_LIST_FILTER_MODEL, template.filterModel)
    } else {
      // フィルタをクリア
      if (typeof gridRef.value.api.setFilterModel === 'function') {
        gridRef.value.api.setFilterModel({})
      }
      
      // LocalStorageにも保存
      filterModel.value = {}
      setLocalStorage(STORAGE_KEYS.TODO_LIST_FILTER_MODEL, null)
    }
    
    // AG Gridに状態変更を通知して再描画を促す
    gridRef.value.api.onFilterChanged()
    gridRef.value.api.onSortChanged()
    
  } catch (e) {
    console.error('Error applying filter template:', e)
  } finally {
    // イベントハンドラーが動作するように、少し遅延させてからisInitializingをfalseにする
    setTimeout(() => {
      isInitializing.value = false
    }, 300)
  }
}

// カラム状態変更時の処理
const onColumnStateChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  const state = gridRef.value.api.getColumnState()
  // ソートや幅の変更のみを保存（hideなどの不要な情報は除外）
  const relevantState = state.map((col: any) => ({
    colId: col.colId,
    sort: col.sort,
    sortIndex: col.sortIndex,
    width: col.width,
    hide: col.hide,
  }))
  
  columnState.value = relevantState
  setLocalStorage(STORAGE_KEYS.TODO_LIST_COLUMN_STATE, relevantState.length > 0 ? relevantState : null)
  
  // ソートモデルも別途保存（getColumnStateからソート情報を取得）
  const columnState = gridRef.value.api.getColumnState()
  const sortFromState = columnState
    .filter((col: any) => col.sort)
    .sort((a: any, b: any) => (a.sortIndex || 0) - (b.sortIndex || 0))
    .map((col: any) => ({ colId: col.colId, sort: col.sort }))
  
  if (sortFromState.length > 0) {
    sortModel.value = sortFromState
    setLocalStorage(STORAGE_KEYS.TODO_LIST_SORT_MODEL, sortFromState)
  } else {
    sortModel.value = []
    setLocalStorage(STORAGE_KEYS.TODO_LIST_SORT_MODEL, null)
  }
}

// ソート変更時の処理（専用のイベントハンドラー）
const onSortChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  // getColumnStateからソート情報を取得
  const columnState = gridRef.value.api.getColumnState()
  const sortFromState = columnState
    .filter((col: any) => col.sort)
    .sort((a: any, b: any) => (a.sortIndex || 0) - (b.sortIndex || 0))
    .map((col: any) => ({ colId: col.colId, sort: col.sort }))
  
  if (sortFromState.length > 0) {
    sortModel.value = sortFromState
    setLocalStorage(STORAGE_KEYS.TODO_LIST_SORT_MODEL, sortFromState)
  } else {
    sortModel.value = []
    setLocalStorage(STORAGE_KEYS.TODO_LIST_SORT_MODEL, null)
  }
}

// フィルタ変更時の処理
const onFilterChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  const model = gridRef.value.api.getFilterModel()
  filterModel.value = model
  setLocalStorage(STORAGE_KEYS.TODO_LIST_FILTER_MODEL, Object.keys(model).length > 0 ? model : null)
}

// ページネーション変更時の処理
const onPaginationChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  // paginationGetPageSizeが存在しない場合は、getGridOptionを使用
  let pageSize: number
  if (typeof gridRef.value.api.paginationGetPageSize === 'function') {
    pageSize = gridRef.value.api.paginationGetPageSize()
  } else if (typeof gridRef.value.api.getGridOption === 'function') {
    pageSize = gridRef.value.api.getGridOption('paginationPageSize') || 50
  } else {
    return
  }
  
  // 初期値と異なる場合のみ保存（初期化時の自動設定を無視）
  if (paginationPageSize.value !== pageSize) {
    paginationPageSize.value = pageSize
    setLocalStorage(STORAGE_KEYS.TODO_LIST_PAGE_SIZE, pageSize)
  }
}

// TODOリストデータ（タスク名とプロジェクト名を含む）
interface TodoListItem {
  id: number
  task_id: number
  title: string
  completed: boolean
  task_name: string
  project_name: string
  scheduled_date?: string | null
  completed_date?: string | null
}

const todoListData = ref<TodoListItem[]>([])

// プロジェクト名を取得
const getProjectName = (projectId: number): string => {
  if (projectId === -1) {
    return '個人タスク'
  }
  const project = projects.value.find((p: Project) => p.id === projectId)
  return project ? project.name : '不明'
}

// TODOリストデータを更新（サーバーサイドページネーションを使用）
const updateTodoListData = async () => {
  try {
    // プロジェクト情報を取得（プロジェクト名の取得用）
    await fetchProjects()
    
    // すべてのTODOを取得（サーバーサイドページネーション）
    // 注意: AG Gridがクライアントサイドページネーションを使用するため、
    // 一度にすべてのデータを取得する（大量データの場合はサーバーサイドページネーションに変更可能）
    const response = await fetchAllTodos(0, 10000) // 最大10000件まで取得
    
    // レスポンスデータをTodoListItem形式に変換
    const allTodos: TodoListItem[] = response.items.map((item: any) => ({
      id: item.id,
      task_id: item.task_id,
      title: item.title,
      completed: item.completed,
      task_name: item.task_name || '不明',
      project_name: item.project_name || (item.project_id === -1 ? '個人タスク' : '不明'),
      scheduled_date: item.scheduled_date,
      completed_date: item.completed_date,
    }))
    
    todoListData.value = allTodos
  } catch (e) {
    console.error('Error updating todo list data:', e)
    // エラー時は空配列を設定
    todoListData.value = []
  }
}

// グリッドコンテキスト（セルレンダラーからアクセス可能）
const gridContext = {
  updateTodoListData,
  updateTodo,
}

// チェックボックスセルレンダラー（読み取り専用：完了状態は実行完了日で自動管理）
const CheckboxCellRenderer = defineComponent({
  props: {
    params: {
      type: Object as () => ICellRendererParams,
      required: true,
    },
  },
  setup(props: { params: ICellRendererParams }) {
    // 完了状態は実行完了日で自動管理されるため、チェックボックスは読み取り専用
    return () => h('div', { class: 'checkbox-cell' }, [
      h('input', {
        type: 'checkbox',
        checked: props.params.data?.completed || false,
        disabled: true, // 読み取り専用
        class: 'todo-checkbox',
      }),
    ])
  },
})

// 日付セルレンダラー（編集可能）
const DateCellRenderer = defineComponent({
  props: {
    params: {
      type: Object as () => ICellRendererParams,
      required: true,
    },
  },
  setup(props: { params: ICellRendererParams }) {
    const handleChange = async (field: 'scheduled_date' | 'completed_date', value: string) => {
      const todoData = props.params.data as TodoListItem | undefined
      const context = props.params.context as typeof gridContext | undefined
      if (todoData && context) {
        try {
          // 実行完了日が設定された場合は自動的にcompletedをtrueに、削除された場合はfalseに
          const updateData: { scheduled_date?: string | null; completed_date?: string | null; completed?: boolean } = {}
          updateData[field] = value || null
          
          if (field === 'completed_date') {
            // 実行完了日が設定された場合はcompletedをtrue、削除された場合はfalseに
            updateData.completed = value ? true : false
          }
          
          await context.updateTodo(todoData.id, updateData)
          await context.updateTodoListData()
        } catch (e) {
          console.error('Error updating todo date:', e)
          alert('日付の更新に失敗しました')
        }
      }
    }

    const formatDateForInput = (dateString: string | null | undefined): string => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    return () => {
      const field = props.params.colDef?.field as 'scheduled_date' | 'completed_date' | undefined
      const value = props.params.data?.[field] || null
      
      return h('div', { class: 'date-cell' }, [
        h('input', {
          type: 'date',
          value: value ? formatDateForInput(value) : '',
          onChange: (e: Event) => {
            const target = e.target as HTMLInputElement
            if (field) {
              handleChange(field, target.value)
            }
          },
          class: 'date-input',
        }),
      ])
    }
  },
})

// 日付をフォーマット（表示用）
const formatDateForDisplay = (dateString: string | null | undefined): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Column Definitions
const columnDefs = ref([
  {
    headerName: '完了',
    field: 'completed',
    cellRenderer: CheckboxCellRenderer,
    width: 100,
    sortable: true,
    filter: 'agSetColumnFilter',
    filterParams: {
      values: [true, false],
      cellRenderer: (params: any) => {
        return params.value ? '完了' : '未完了'
      },
    },
    floatingFilter: false,  // チェックボックスカラムはフローティングフィルタを無効化
    resizable: false,
    cellStyle: { display: 'flex', alignItems: 'center', justifyContent: 'center' },
  },
  { 
    field: 'title', 
    headerName: 'TODO', 
    flex: 2,
    filter: 'agTextColumnFilter',
    cellStyle: (params: any) => {
      if (params.data?.completed) {
        return { textDecoration: 'line-through', opacity: 0.7 }
      }
      return {}
    },
  },
  { 
    field: 'task_name', 
    headerName: 'タスク名', 
    flex: 2,
    filter: 'agTextColumnFilter',
  },
  { 
    field: 'project_name', 
    headerName: 'プロジェクト名', 
    flex: 1,
    filter: 'agSetColumnFilter',
  },
  {
    field: 'scheduled_date',
    headerName: '実行予定日',
    cellRenderer: DateCellRenderer,
    width: 180,
    sortable: true,
    filter: 'agDateColumnFilter',
    filterParams: {
      comparator: (filterLocalDateAtMidnight: Date, cellValue: Date | null) => {
        if (!cellValue) return -1
        const cellDate = new Date(cellValue)
        cellDate.setHours(0, 0, 0, 0)
        if (cellDate < filterLocalDateAtMidnight) {
          return -1
        } else if (cellDate > filterLocalDateAtMidnight) {
          return 1
        } else {
          return 0
        }
      },
      browserDatePicker: true,
    },
    valueGetter: (params: any) => {
      const dateStr = params.data?.scheduled_date
      if (!dateStr) return null
      try {
        const date = new Date(dateStr)
        return isNaN(date.getTime()) ? null : date
      } catch {
        return null
      }
    },
    valueFormatter: (params: any) => {
      if (!params.value) return '-'
      const dateStr = params.value instanceof Date ? params.value.toISOString() : params.value
      return formatDateForDisplay(dateStr)
    },
  },
  {
    field: 'completed_date',
    headerName: '実行完了日',
    cellRenderer: DateCellRenderer,
    width: 180,
    sortable: true,
    filter: 'agDateColumnFilter',
    filterParams: {
      comparator: (filterLocalDateAtMidnight: Date, cellValue: Date | null) => {
        if (!cellValue) return -1
        const cellDate = new Date(cellValue)
        cellDate.setHours(0, 0, 0, 0)
        if (cellDate < filterLocalDateAtMidnight) {
          return -1
        } else if (cellDate > filterLocalDateAtMidnight) {
          return 1
        } else {
          return 0
        }
      },
      browserDatePicker: true,
    },
    valueGetter: (params: any) => {
      const dateStr = params.data?.completed_date
      if (!dateStr) return null
      try {
        const date = new Date(dateStr)
        return isNaN(date.getTime()) ? null : date
      } catch {
        return null
      }
    },
    valueFormatter: (params: any) => {
      if (!params.value) return '-'
      const dateStr = params.value instanceof Date ? params.value.toISOString() : params.value
      return formatDateForDisplay(dateStr)
    },
  },
])

// Default Column Definitions
const defaultColDef = ref({
  sortable: true,
  filter: 'agTextColumnFilter',  // デフォルトフィルタタイプをテキストフィルタに設定
  resizable: true,
  floatingFilter: false,  // フローティングフィルタを無効化（フィルタメニューを使用）
})

// 状態復元フラグ（重複復元を防ぐ）
let hasRestoredState = false
let retryCount = 0

// 状態を復元する関数
const restoreGridState = () => {
  if (!gridRef.value || hasRestoredState) return
  
  // 再試行回数の上限チェック
  if (retryCount >= MAX_RETRY_COUNT) {
    console.error('Failed to restore grid state: Max retry count reached')
    isInitializing.value = false
    return
  }
  
  // AG GridのAPIが準備できているか確認
  const api = gridRef.value.api
  if (!api) {
    retryCount++
    console.log(`AG Grid API not ready yet, retrying... (${retryCount}/${MAX_RETRY_COUNT})`)
    setTimeout(() => {
      if (!hasRestoredState && gridRef.value) {
        restoreGridState()
      }
    }, RESTORE_STATE_TIMEOUTS.INITIAL)
    return
  }
  
  // APIメソッドの存在確認（AG Gridのバージョンによってメソッド名が異なる可能性があるため、代替方法も試す）
  const hasPaginationMethod = typeof api.paginationSetPageSize === 'function' || 
                              typeof api.setGridOption === 'function'
  const hasColumnStateMethod = typeof api.applyColumnState === 'function' || 
                               typeof api.setGridOption === 'function'
  const hasFilterMethod = typeof api.setFilterModel === 'function' || 
                          typeof api.setGridOption === 'function'
  
  if (!hasPaginationMethod || !hasColumnStateMethod || !hasFilterMethod) {
    retryCount++
    setTimeout(() => {
      if (!hasRestoredState && gridRef.value) {
        restoreGridState()
      }
    }, RESTORE_STATE_TIMEOUTS.INITIAL)
    return
  }
  
  // 初期化中フラグを設定
  isInitializing.value = true
  retryCount = 0 // 成功したらリセット
  
  try {
    // ページサイズを明示的に設定（paginationSetPageSizeは存在しないため、setGridOptionを使用）
    const pageSizeValue = paginationPageSize.value
    if (typeof api.setGridOption === 'function') {
      api.setGridOption('paginationPageSize', pageSizeValue)
    }
    
    // ソートモデルを復元（優先的にソート状態を復元）
    // AG Gridのドキュメントによると、applyColumnStateを使用してソート状態を復元する
    if (sortModel.value.length > 0) {
      // sortModelをapplyColumnState用の形式に変換
      const sortColumnState = sortModel.value.map((sort: any, index: number) => ({
        colId: sort.colId,
        sort: sort.sort,
        sortIndex: index,
      }))
      
      if (typeof api.applyColumnState === 'function') {
        api.applyColumnState({ 
          state: sortColumnState,
          applyOrder: false  // ソートのみを適用、カラムの順序は変更しない
        })
      }
    } else if (columnState.value.length > 0) {
      // ソートモデルがない場合は、カラム状態からソートを復元
      const sortFromState = columnState.value
        .filter((col: any) => col.sort)
        .sort((a: any, b: any) => (a.sortIndex || 0) - (b.sortIndex || 0))
        .map((col: any) => ({ 
          colId: col.colId, 
          sort: col.sort,
          sortIndex: col.sortIndex || 0
        }))
      
      if (sortFromState.length > 0) {
        if (typeof api.applyColumnState === 'function') {
          api.applyColumnState({ 
            state: sortFromState,
            applyOrder: false  // ソートのみを適用、カラムの順序は変更しない
          })
          console.log('Sort model restored from column state via applyColumnState:', sortFromState)
        }
      }
    }
    
    // カラム状態を復元（幅や表示/非表示など、ソートは除外）
    if (columnState.value.length > 0) {
      if (typeof api.applyColumnState === 'function') {
        // ソート情報を除外してカラム状態を適用
        const stateWithoutSort = columnState.value.map((col: any) => ({
          ...col,
          sort: undefined,
          sortIndex: undefined,
        }))
        api.applyColumnState({ 
          state: stateWithoutSort,
          applyOrder: true
        })
      } else if (typeof api.setGridOption === 'function') {
        // 代替方法：各カラムの状態を個別に設定
        columnState.value.forEach((colState: any) => {
          const column = api.getColumn(colState.colId)
          if (column) {
            if (colState.width) column.setActualWidth(colState.width)
            if (colState.hide !== undefined) column.setVisible(!colState.hide)
          }
        })
      }
    }
    
    // フィルタモデルを復元
    if (Object.keys(filterModel.value).length > 0) {
      if (typeof api.setFilterModel === 'function') {
        api.setFilterModel(filterModel.value)
      } else if (typeof api.setGridOption === 'function') {
        api.setGridOption('filterModel', filterModel.value)
      }
    }
    
    hasRestoredState = true
  } catch (e) {
    console.error('Error restoring grid state:', e)
  } finally {
    // 初期化完了（少し遅延させてイベントが処理されるようにする）
    setTimeout(() => {
      isInitializing.value = false
    }, RESTORE_STATE_TIMEOUTS.COMPLETE)
  }
}

// Grid Readyイベントハンドラー
const onGridReady = () => {
  // グリッドが準備できたら状態を復元（少し待ってから）
  if (!hasRestoredState && todoListData.value.length > 0) {
    setTimeout(() => {
      if (!hasRestoredState) {
        restoreGridState()
      }
    }, RESTORE_STATE_TIMEOUTS.GRID_READY)
  }
}

// 最初のデータレンダリング後の処理
const onFirstDataRendered = () => {
  // データがレンダリングされた後に状態を復元（まだ復元されていない場合）
  // AG GridのAPIが完全に初期化されるまで少し待つ
  if (!hasRestoredState) {
    setTimeout(() => {
      if (!hasRestoredState) {
        restoreGridState()
      }
    }, RESTORE_STATE_TIMEOUTS.FIRST_DATA_RENDERED)
  }
}

// データが更新された時に状態を復元（初回のみ）
watch(todoListData, async (newData) => {
  if (newData.length > 0 && !hasRestoredState && gridRef.value?.api) {
    await nextTick()
    restoreGridState()
  }
}, { immediate: false })

// 初期データを読み込む
onMounted(async () => {
  await fetchProjects()
  await updateTodoListData()
  // データが読み込まれた後に状態を復元
  await nextTick()
  // 状態復元はonFirstDataRenderedで行うため、ここでは何もしない
})
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.todo-list {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.todo-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0 0 1rem 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.filter-templates {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-templates-label {
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  font-weight: 500;
}

.filter-template-wrapper {
  position: relative;
}

.filter-template-button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s, color 0.2s;

  &:hover {
    background: var(--current-activeBackground);
    border-color: var(--current-activeBackground);
    color: var(--current-textWhite);
  }

  &:active {
    transform: scale(0.98);
  }
}

.filter-template-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.75rem;
  line-height: 1.5;
  white-space: pre-line;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  box-shadow: 0 4px 12px var(--current-shadowMd);
  z-index: 1000;
  min-width: 200px;
  max-width: 400px;
  pointer-events: none;

  &::before {
    content: '';
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-bottom-color: var(--current-backgroundLight);
  }
}

.todo-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.todo-section {
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.loading-message {
  text-align: center;
  padding: 2rem;
  color: var(--current-textSecondary);
  font-size: 1rem;
}

.error-message {
  background: var(--current-errorBackground);
  color: var(--current-errorText);
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid var(--current-errorBorder);
}

:deep(.checkbox-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  
  .todo-checkbox {
    cursor: pointer;
    width: 1.25rem;
    height: 1.25rem;
  }
}

:deep(.date-cell) {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0.25rem 0;
  
  .date-input {
    width: 100%;
    padding: 0.375rem 0.5rem;
    border: 1px solid var(--current-borderColor);
    border-radius: 4px;
    background: var(--current-backgroundLight);
    color: var(--current-textPrimary);
  font-size: 0.875rem;
    transition: border-color 0.2s;
    
    &:focus {
      outline: none;
      border-color: var(--current-linkColor);
    }
  }
}

// AG Gridのテーマカスタマイズ
:deep(.ag-theme-quartz) {
  --ag-background-color: var(--current-backgroundLight);
  --ag-header-background-color: var(--current-navBackground);
  --ag-header-foreground-color: var(--current-textPrimary);
  --ag-odd-row-background-color: var(--current-backgroundLight);
  --ag-row-hover-color: var(--current-hoverBackground);
  --ag-border-color: var(--current-borderColor);
  --ag-font-family: inherit;
  --ag-font-size: 0.875rem;
  --ag-foreground-color: var(--current-textPrimary);
  --ag-selected-row-background-color: var(--current-activeBackground);
}
</style>
