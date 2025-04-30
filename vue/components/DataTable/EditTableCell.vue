<template>
  <Column ref='root' :name='column.name' :title='column.title'
    :class='{selected, editing, editable:column.editable}'>
    <!-- Editing -->
    <template v-if='editing'>
      <slot name='editing' :column='column' :item='item'>
        <SelectInput v-if='column.choices' :choices='column.choices()'
          v-model='value' @keydown='emit("keydown", $event, row, col)'/>
        <input v-else v-model='value' spellcheck='false' autocomplete='off'
          @keydown='emit("keydown", $event)'/>
      </slot>
    </template>
    <!-- Not Editing -->
    <template v-else>
      <slot name='viewing' :column='column' :item='item'>
        <Tooltip :text='tooltip' :width='tooltipWidth'>
          <span v-if='column.html' class='fakeinput' v-html='column.html(item)'/>
          <span v-else class='fakeinput'>{{value}}</span>
        </Tooltip>
      </slot>
    </template>
  </Column>
</template>

<script setup>
  import {nextTick, ref, watch} from 'vue'
  import {DataTableColumn as Column} from '@/components'
  import {SelectInput, Tooltip} from '@/components'

  const props = defineProps({
    column: {type:Object},                  // Column object
    item: {type:Object},                    // Transaction object
    tooltip: {type:String},                 // Tooltip text
    tooltipWidth: {type:String},            // Tooltip width
  })
  const root = ref(null)                    // Reference to root elem
  const selected = ref(false)               // True if cell is selected
  const editing = ref(false)                // True if editing this cell
  const value = ref(props.column.text?.(props.item))  // Value of the cell
  const errmsg = ref(null)                  // Error message for this cell
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
    setValue: (newval) => value.value = newval,
    setErrMsg: (errmsg) => errmsg.value = errmsg,
  })
</script>
