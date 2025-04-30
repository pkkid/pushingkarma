<template>
  <Column ref='root' :name='column.name' :title='column.title' :key='successKey'
    :class='{selected, editing, editable:column.editable, success}'>
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

  var successTimeout = null                 // Timeout for success animation
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
  const success = ref(false)                // True if cell successfully edited
  const successKey = ref(0)                 // Incrementing key to force re-render
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

  // Set Success
  // Set green background that fades out
  const setSuccess = async function() {
    clearTimeout(successTimeout)
    success.value = false
    successKey.value += 1
    await nextTick()
    success.value = true
    successTimeout = setTimeout(() => {
      success.value = false
    }, 2000)
  }
  
  // Define Exposed
  // Expose this function to the parent
  defineExpose({
    isSelected: () => selected.value,
    isEditing: () => editing.value,
    setSelected: (newval) => selected.value = newval,
    setEditing: (newval) => editing.value = newval,
    setValue: (newval) => value.value = newval,
    setSuccess: setSuccess,
    setError: (errmsg) => errmsg.value = errmsg,
  })
</script>

<style>
  .edittable table td {
    position: relative;
    padding: 0px;
    border-top: 0px solid var(--lightbg-bg3);
    .tdwrap {
      border: 2px solid #f000;
      cursor: default;
      line-height: 28px;
      height: 32px;
      padding: 0px;
      z-index: 2;
      user-select: none;
      &::before {
        border-top: 1px solid var(--lightbg-bg3);
        content: ' ';
        display: block;
        left: 0px;
        position: absolute;
        top: 0px;
        width: 100%;
        z-index: 1;
      }
      input, .fakeinput {
        background-color: transparent;
        border-radius: 0px;
        border-width: 0px;
        box-shadow: none;
        font-family: inherit;
        font-size: inherit;
        height: calc(var(--lineheight) + 2px);
        line-height: calc(var(--lineheight) + 2px);
        outline: none;
        padding: 0px 6px;
        width: 100%;
        text-align: inherit;
      }
      .fakeinput {
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      input { color: #111; }
    }
    &.editable:not(.editing) .tdwrap:hover { background-color: #ddd8; }
    &.selected .tdwrap {
      border: 2px solid var(--accent);
      background-color: var(--lightbg-bg1);
      height: calc(100% + 1px);
      left: 0px;
      line-height: calc(var(--lineheight) + 1px);
      position: absolute;
      top: 0px;
      width: 100%;
      &::before { border-top: 0px solid #fff0; }
    }
    &.success .tdwrap {
      --success-fade-target: transparent;
      animation: success-fade 2s forwards;
    }
    &.editing .tdwrap {
      --success-fade-target: #f812;
      background-color: #f812;
      box-shadow: inset 0px 1px 2px #0005;
    }
    &.modified::before {
      content: '';
      position: absolute;
      top: 2px; left: 2px;
      width: 0px; height: 0px;
      border-top: 7px solid #5558;
      border-right: 7px solid transparent;
      z-index: 10;
    }
  }

  @keyframes success-fade {
    0% { background-color: #0a48; }
    20% { background-color: #0a48; }
    100% { background-color: var(--success-fade-target); }
  }
</style>
