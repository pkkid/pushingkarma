<template>
  <Column ref='root' :name='column.name' :title='column.title' :key='animateBgKey'
    :class='{selected, editing, editable:column.editable, animatebg:animateBgColor}'>
    <!-- Editing -->
    <template v-if='editing'>
      <slot name='editing' :column='column' :item='item'>
        <SelectInput v-if='column.choices' :choices='column.choices()' v-model='value' @keydown='emit("keydown", $event, row, col)'/>
        <input v-else v-model='value' spellcheck='false' autocomplete='off' @keydown='emit("keydown", $event)'/>
      </slot>
    </template>
    <!-- Not Editing -->
    <template v-else>
      <slot name='viewing' :column='column' :item='item'>
        <Tooltip :html='tooltip' :width='tooltipWidth'>
          <span v-if='column.html' class='fakeinput' v-html='column.html(item)'/>
          <span v-else class='fakeinput'>{{value}}</span>
        </Tooltip>
      </slot>
    </template>
  </Column>
</template>

<script setup>
  import {nextTick, onBeforeMount, ref, watch} from 'vue'
  import {DataTableColumn as Column} from '@/components'
  import {SelectInput, Tooltip} from '@/components'
  import {utils} from '@/utils'

  const props = defineProps({
    item: {type:Object},                      // Transaction object
    column: {type:Object},                    // Column object
    tooltip: {type:String},                   // Tooltip text
    tooltipWidth: {type:String},              // Tooltip width
  })
  var animateBgTimeout = null                 // Timeout for success animation
  const animateBgColor = ref(null)            // True if cell successfully edited
  const animateBgKey = ref(0)                 // Incrementing key to force re-render
  const root = ref(null)                      // Reference to root elem
  const selected = ref(false)                 // True if cell is selected
  const editing = ref(false)                  // True if editing this cell
  // const value = ref(props.column.text?.(props.item))  // Value of the cell
  const errmsg = ref(null)                    // Error message for this cell
  const emit = defineEmits(['keydown'])       // Emit when closing the modal
  const value = ref(null)                     // Value of the cell

  // On Before Mount
  // Set the initial value
  onBeforeMount(function() {
    value.value = utils.getItemValue(props.item, props.column)
  })

  // Watch Item
  // Update the value when the item changes
  watch(() => props.item, function(newval) {
    value.value = utils.getItemValue(newval, props.column)
  })

  // Watch Editing
  // focus the input and select its text
  watch(editing, async function(newval) {
    if (!newval) { return }
    await nextTick()
    const input = root.value.$el.querySelector('input')
    const select_start = props.column.selectall ? 0 : input.value.length
    const select_end = input.value.length
    input?.focus()
    input?.setSelectionRange(select_start, select_end)
  })

  // Set Success
  // Set green background that fades out
  const animateBg = async function(color='#0a48') {
    clearTimeout(animateBgTimeout)
    animateBgColor.value = null
    animateBgKey.value += 1
    await nextTick()
    animateBgColor.value = color
    animateBgTimeout = setTimeout(() => {
      animateBgColor.value = null
    }, 2000)
  }
  
  // Define Exposed
  // Expose this function to the parent
  defineExpose({
    animateBg: animateBg,
    isEditing: () => editing.value,
    isSelected: () => selected.value,
    setEditing: (newval) => editing.value = newval,
    setError: (errmsg) => errmsg.value = errmsg,
    setSelected: (newval) => selected.value = newval,
    setValue: (newval) => value.value = newval,
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
    &.animatebg .tdwrap {
      --animatebg-start: v-bind(animateBgColor);
      --animatebg-end: transparent;
      animation: animatebg-fade 2s forwards;
    }
    &.editing .tdwrap {
      --animatebg-end: #f812;
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

  @keyframes animatebg-fade {
    0% { background-color: var(--animatebg-start); }
    20% { background-color: var(--animatebg-start); }
    100% { background-color: var(--animatebg-end); }
  }
</style>
