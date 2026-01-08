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
      <AgGridVue
        ref="gridRef"
        :rowModelType="'infinite'"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :cacheBlockSize="25"
        :maxBlocksInCache="10"
        @gridReady="onGridReady"
        class="ag-theme-quartz todo-grid"
        style="width: 100%; height: 100%;"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h, nextTick } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ICellRendererParams, IDatasource, IGetRowsParams, IFilterComp, IFilterParams, FilterModel } from 'ag-grid-community'
import { useTodos } from '../composables/useTodos'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// API composableを使用
const { fetchAllTodos, updateTodo } = useTodos()

// AG Gridの参照
const gridRef = ref<InstanceType<typeof AgGridVue> | null>(null)

// フィルタテンプレートの定義
interface FilterTemplate {
  id: string
  name: string
  sortModel: Array<{ colId: string; sort: 'asc' | 'desc' }>
  filterModel?: FilterModel
  tooltip: string[] // 複数行対応のため配列に変更
}

const filterTemplates: FilterTemplate[] = [
  {
    id: 'default',
    name: 'デフォルト',
    sortModel: [
      { colId: 'completed', sort: 'asc' },
      { colId: 'scheduled_date', sort: 'asc' },
    ],
    tooltip: [
      'ソート:',
      '1. 完了（昇順）',
      '2. 予定日（昇順）',
    ],
  },
  {
    id: 'incomplete',
    name: '未完了',
    sortModel: [
      { colId: 'scheduled_date', sort: 'asc' },
    ],
    filterModel: {
      completed: {
        value: false,
        filterType: 'custom',
      },
    },
    tooltip: [
      'フィルタ:',
      '- 完了 = 未完了',
      'ソート:',
      '1. 予定日（昇順）',
    ],
  },
  {
    id: 'reset',
    name: 'リセット',
    sortModel: [],
    filterModel: {},
    tooltip: [
      'フィルタ・ソートをすべてリセットします',
    ],
  },
]

// カラム名のマッピング（colId -> headerName）
const columnNameMapForDisplay: Record<string, string> = {
  'completed': '完了',
  'title': 'タイトル',
  'task_name': 'タスク',
  'project_name': 'プロジェクト',
  'scheduled_date': '予定日',
  'completed_date': '完了日',
}

// ツールチップ表示用の状態
const hoveredTemplate = ref<FilterTemplate | null>(null)
const tooltipText = ref<string>('')

// ツールチップを表示
const showTooltip = (template: FilterTemplate) => {
  hoveredTemplate.value = template
  tooltipText.value = template.tooltip.join('\n')
}

// ツールチップを非表示
const hideTooltip = () => {
  hoveredTemplate.value = null
  tooltipText.value = ''
}

// フィルタテンプレートを適用する関数（Infinite Scroll対応）
// AG GridのSorting APIとFilter APIを使用
// https://www.ag-grid.com/vue-data-grid/row-sorting/#sorting-api
// https://www.ag-grid.com/vue-data-grid/filter-api/
const applyFilterTemplate = async (template: FilterTemplate) => {
  if (!gridRef.value?.api) {
    console.error('Grid API not available')
    return
  }
  
  try {
    console.log('Applying filter template:', template)
    
    // ソートモデルとフィルタモデルを準備
    const sortModel = template.sortModel && template.sortModel.length > 0 
      ? template.sortModel 
      : []
    const filterModel = template.filterModel && Object.keys(template.filterModel).length > 0
      ? template.filterModel
      : {}
    
    console.log('Setting sort model:', sortModel)
    console.log('Setting filter model:', filterModel)
    
    // AG GridのapplyColumnStateを使用してソートを設定
    // https://www.ag-grid.com/vue-data-grid/row-sorting/#sorting-api
    // この方法により、Infinite Scrollモデルでも確実にソートが反映される
    if (sortModel.length > 0) {
      const columnState = sortModel.map((sort, index) => ({
        colId: sort.colId,
        sort: sort.sort,
        sortIndex: index,
      }))
      
      console.log('Applying column state for sort:', columnState)
      if (typeof gridRef.value.api.applyColumnState === 'function') {
        gridRef.value.api.applyColumnState({
          state: columnState,
          defaultState: { sort: null },
        })
      } else if (typeof gridRef.value.api.setSortModel === 'function') {
        gridRef.value.api.setSortModel(sortModel)
      }
    } else {
      // ソートをクリア
      console.log('Clearing sort')
      if (typeof gridRef.value.api.applyColumnState === 'function') {
        gridRef.value.api.applyColumnState({
          defaultState: { sort: null },
        })
      } else if (typeof gridRef.value.api.setSortModel === 'function') {
        gridRef.value.api.setSortModel([])
      }
    }
    
    // フィルタを設定
    if (typeof gridRef.value.api.setFilterModel === 'function') {
      gridRef.value.api.setFilterModel(filterModel)
    }
    
    // Vueの更新サイクルを待つ
    await nextTick()
    
    // Infinite Scrollモデルでは、refreshInfiniteCache()を呼び出すことで、
    // ソートとフィルタの状態が反映される
    console.log('Refreshing infinite cache')
    if (typeof gridRef.value.api.refreshInfiniteCache === 'function') {
      gridRef.value.api.refreshInfiniteCache()
    }
    
  } catch (e) {
    console.error('Error applying filter template:', e)
  }
}

// カラム名のマッピング（フロントエンド → バックエンド）
const columnNameMap: Record<string, string> = {
  'id': 'id',
  'title': 'title',
  'completed': 'completed',
  'order': 'order',
  'scheduled_date': 'scheduled_date',
  'completed_date': 'completed_date',
  'created_at': 'created_at',
  'updated_at': 'updated_at',
  'task_name': 'task_name',
  'project_name': 'project_name',
}

// Infinite Scroll用のdatasource（ソート・フィルタ対応）
const createDatasource = (): IDatasource => {
  return {
    getRows: async (params: IGetRowsParams) => {
      console.log('getRows', { startRow: params.startRow, endRow: params.endRow, sortModel: params.sortModel, filterModel: params.filterModel })
      
      try {
        // ソート情報を取得
        let sortBy: string | undefined = undefined
        let sortOrder: 'asc' | 'desc' = 'asc'
        
        if (params.sortModel && params.sortModel.length > 0) {
          const firstSort = params.sortModel[0]
          sortBy = columnNameMap[firstSort.colId] || firstSort.colId
          sortOrder = firstSort.sort
          console.log('getRows: Using sort', { colId: firstSort.colId, sortBy, sortOrder })
        } else {
          // デフォルトのソート（order asc）
          sortBy = 'order'
          sortOrder = 'asc'
        }
        
        // フィルタ情報を取得
        const filters: { title?: string; completed?: boolean; taskName?: string; projectName?: string } = {}
        if (params.filterModel) {
          // titleフィルタ
          if (params.filterModel.title) {
            const titleFilter = params.filterModel.title
            if (titleFilter.filterType === 'text' && titleFilter.type === 'contains') {
              filters.title = titleFilter.filter
            }
          }
          // completedフィルタ（カスタムフィルタから）
          if (params.filterModel.completed) {
            const completedFilter = params.filterModel.completed
            // カスタムフィルタのモデル形式: { value: boolean }
            if (completedFilter.value !== undefined) {
              filters.completed = completedFilter.value === true || completedFilter.value === 'true'
            }
          }
          // task_nameフィルタ
          if (params.filterModel.task_name) {
            const taskNameFilter = params.filterModel.task_name
            if (taskNameFilter.filterType === 'text' && taskNameFilter.type === 'contains') {
              filters.taskName = taskNameFilter.filter
            }
          }
          // project_nameフィルタ
          if (params.filterModel.project_name) {
            const projectNameFilter = params.filterModel.project_name
            if (projectNameFilter.filterType === 'set' && projectNameFilter.values && projectNameFilter.values.length > 0) {
              filters.projectName = projectNameFilter.values[0]
            } else if (projectNameFilter.filterType === 'text' && projectNameFilter.type === 'contains') {
              filters.projectName = projectNameFilter.filter
            }
          }
        }
        
        const skip = params.startRow
        const limit = params.endRow - params.startRow
        
        const result = await fetchAllTodos(skip, limit, sortBy, sortOrder, filters)
        
        const rowData = result.items.map((item: any) => ({
          id: item.id,
          title: item.title,
          completed: item.completed,
          order: item.order,
          scheduled_date: item.scheduled_date || null,
          completed_date: item.completed_date || null,
          task_name: item.task_name || null,
          project_name: item.project_name || null,
        }))
        
        const lastRow = result.items.length < limit 
          ? skip + result.items.length
          : undefined
        
        params.successCallback(rowData, lastRow)
      } catch (e) {
        console.error('getRows error', e)
        params.failCallback()
      }
    },
  }
}

// 日付をフォーマット
const formatDateForDisplay = (dateString: string | null | undefined): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 完了カラム用のカスタムフィルタ（Community版対応）
const CompletedFilter = defineComponent({
  props: {
    params: {
      type: Object as () => IFilterParams,
      required: true,
    },
  },
  setup(props: { params: IFilterParams }) {
    const selectedValue = ref<boolean | null>(null)
    
    const doesFilterPass = (node: any): boolean => {
      if (selectedValue.value === null) {
        return true
      }
      const isCompleted = !!node.data?.completed_date
      return isCompleted === selectedValue.value
    }
    
    const isFilterActive = (): boolean => {
      return selectedValue.value !== null
    }
    
    const getModel = (): any => {
      if (selectedValue.value === null) {
        return null
      }
      return { value: selectedValue.value }
    }
    
    const setModel = (model: any): void => {
      if (model && model.value !== undefined) {
        selectedValue.value = model.value
      } else {
        selectedValue.value = null
      }
    }
    
    const onChange = (e: Event) => {
      const target = e.target as HTMLSelectElement
      if (target.value === '') {
        selectedValue.value = null
      } else {
        selectedValue.value = target.value === 'true'
      }
      props.params.filterChangedCallback()
    }
    
    // フィルタインターフェースのメソッドを公開
    return {
      selectedValue,
      onChange,
      // フィルタインターフェースのメソッドを公開
      doesFilterPass,
      isFilterActive,
      getModel,
      setModel,
    }
  },
  render() {
    return h('div', { class: 'completed-filter' }, [
      h('div', { class: 'filter-label' }, '完了状態:'),
      h('select', {
        class: 'filter-select',
        value: (this as any).selectedValue === null ? '' : (this as any).selectedValue.toString(),
        onChange: (this as any).onChange,
      }, [
        h('option', { value: '' }, 'すべて'),
        h('option', { value: 'true' }, '完了'),
        h('option', { value: 'false' }, '未完了'),
      ]),
    ])
  },
})

// 完了チェックボックスセルレンダラー（編集不能、completed_dateの有無で判断）
const CompletedCellRenderer = defineComponent({
  props: {
    params: {
      type: Object as () => ICellRendererParams,
      required: true,
    },
  },
  setup(props: { params: ICellRendererParams }) {
    // completed_dateの有無で完了状態を判断
    const isCompleted = !!props.params.data?.completed_date
    
    return () => h('div', { class: 'checkbox-cell' }, [
      h('input', {
        type: 'checkbox',
        checked: isCompleted,
        disabled: true,
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
      const todoData = props.params.data as any
      if (todoData) {
        try {
          const updateData: { scheduled_date?: string | null; completed_date?: string | null } = {}
          updateData[field] = value || null
          
          await updateTodo(todoData.id, updateData)
          
          // Infinite Scrollでは、データを再読み込みするためにキャッシュをリフレッシュ
          if (gridRef.value?.api && typeof gridRef.value.api.refreshInfiniteCache === 'function') {
            gridRef.value.api.refreshInfiniteCache()
          }
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
      const dateValue = props.params.data?.[field] || null
      
      return h('input', {
        type: 'date',
        value: formatDateForInput(dateValue),
        class: 'date-input',
        onInput: (e: Event) => {
          const target = e.target as HTMLInputElement
          handleChange(field!, target.value)
        },
      })
    }
  },
})

// Column Definitions
const columnDefs = ref([
  {
    headerName: '完了',
    field: 'completed',
    cellRenderer: CompletedCellRenderer,
    width: 100,
    sortable: true,
    resizable: false,
    // Community版対応: カスタムフィルタを使用
    filter: CompletedFilter,
    floatingFilter: false,
    cellStyle: { display: 'flex', alignItems: 'center', justifyContent: 'center' },
    valueGetter: (params: any) => {
      // completed_dateの有無で完了状態を返す（ソート・フィルタ用）
      return !!params.data?.completed_date
    },
  },
  { 
    field: 'title', 
    headerName: 'タイトル', 
    flex: 1,
    sortable: true,
    filter: 'agTextColumnFilter',
    floatingFilter: true,
  },
  { 
    field: 'task_name', 
    headerName: 'タスク', 
    flex: 1,
    sortable: true,
    filter: 'agTextColumnFilter',
    floatingFilter: true,
  },
  { 
    field: 'project_name', 
    headerName: 'プロジェクト', 
    flex: 1,
    sortable: true,
    filter: 'agTextColumnFilter',
    floatingFilter: true,
  },
  {
    field: 'scheduled_date',
    headerName: '予定日',
    cellRenderer: DateCellRenderer,
    width: 150,
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
    floatingFilter: true,
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
    headerName: '完了日',
    cellRenderer: DateCellRenderer,
    width: 150,
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
    floatingFilter: true,
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

// Default Column Definitions（フィルタ対応）
const defaultColDef = ref({
  sortable: true,
  resizable: true,
  filter: 'agTextColumnFilter',
  floatingFilter: true,
  // カラム定義で明示的に指定されたフィルタを優先
  suppressHeaderMenuButton: false,
})

// Grid Readyイベントハンドラー
const onGridReady = (params: any) => {
  console.log('onGridReady')
  params.api.setGridOption('datasource', createDatasource())
}
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.todo-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.todo-header {
  margin-bottom: 1rem;
  flex-shrink: 0;

  h2 {
    margin: 0 0 1rem 0;
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
  flex: 1;
  min-height: 0;
}

.todo-grid {
  height: 100%;
}

:deep(.checkbox-cell) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  
  .todo-checkbox {
    cursor: not-allowed;
  }
}

:deep(.date-input) {
  width: 100%;
  padding: 0.25rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.875rem;
}

:deep(.completed-filter) {
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  .filter-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--current-textPrimary);
  }
  
  .filter-select {
    padding: 0.375rem;
    border: 1px solid var(--current-borderColor);
    border-radius: 4px;
    background: var(--current-backgroundLight);
    color: var(--current-textPrimary);
    font-size: 0.875rem;
    cursor: pointer;
    
    &:hover {
      border-color: var(--current-linkColor);
    }
    
    &:focus {
      outline: none;
      border-color: var(--current-linkColor);
      box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
    }
  }
}
</style>
