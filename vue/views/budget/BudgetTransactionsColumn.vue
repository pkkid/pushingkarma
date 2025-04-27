<template>
  <Column ref='root' :name='column.name' :title='column.title' :class='{selected, editing, editable:column.editable}'>
    <!-- Editing -->
    <template v-if='editing'>
      <FilterSelect v-if='column.choices' :choices='column.choices()'
        :value='column.text(trx)' @keydown='emit("keydown", $event, row, col)'/>
      <input v-else :value='column.text(trx)' spellcheck='false' autocomplete='off'
        @keydown='emit("keydown", $event)'/>
    </template>
    <!-- Not Editing -->
    <template v-else>
      <Tooltip :text='tooltip' :width='tooltipWidth'>
        <span v-if='column.html' class='fakeinput' v-html='column.html(trx)'/>
        <span v-else class='fakeinput'>{{column.text(trx)}}</span>
      </Tooltip>
    </template>
  </Column>
</template>

<script setup>
  import {nextTick, ref, watch} from 'vue'
  import {DataTableColumn as Column} from '@/components'
  import {FilterSelect, Tooltip} from '@/components'

  const props = defineProps({
    column: {type:Object},                  // Column object
    trx: {type:Object},                     // Transaction object
    tooltip: {type:String},                 // Tooltip text
    tooltipWidth: {type:String},            // Tooltip width
  })
  const root = ref(null)                    // Reference to root elem
  const selected = ref(false)               // True if cell is selected
  const editing = ref(false)                // True if editing this cell
  const emit = defineEmits(['keydown'])     // Emit when closing the modal

  // Watch Editing
  // focus the input and select its text
  watch(editing, async function() {
    await nextTick()
    const input = root.value.$el.querySelector('input')
    input?.focus()
    input?.setSelectionRange(input.value.length, input.value.length)
  })
  
  // Define Exposed
  // Expose this function to the parent
  defineExpose({
    isSelected: () => selected.value,
    isEditing: () => editing.value,
    setSelected: (newval) => selected.value = newval,
    setEditing: (newval) => editing.value = newval,
  })
</script>
