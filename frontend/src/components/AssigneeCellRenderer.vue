<template>
  <div class="assignee-cell" :title="assignees.join(', ')">
    <span v-if="assignees.length === 0">-</span>
    <span v-for="assignee in assignees" :key="assignee" class="assignee-badge" :title="assignee">
      {{ assignee }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ICellRendererParams } from 'ag-grid-community'

const props = defineProps<{
  params: ICellRendererParams
}>()

const assignees = computed(() => {
  const value = props.params.value ?? props.params.data?.assignee ?? []
  return Array.isArray(value) ? value : value ? [value] : []
})
</script>

<style lang="scss">
@import '../styles/_theme';

.assignee-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  align-items: center;
  padding: 0.25rem 0;
  width: 100%;
  height: 100%;

  .assignee-badge {
    display: inline-block;
    padding: 0.25rem 0.625rem;
    background: var(--current-activeBackground);
    color: var(--current-textWhite);
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
    line-height: 1.4;
  }
}
</style>
