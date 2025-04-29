<template>
  <DataTable class='edittable' :items='items' :keyattr='keyattr' :infinite='infinite' @getNextPage='emit("getNextPage")'>
    <template #columns='{item, row}'>
      <template v-for='(column, col) in columns' :key='col'>
        <slot name='cell' :row='row' :col='col' :column='column' :item='item'>
          <EditTableCell :ref='elem => setCellRef(elem, row, col)' :column='column' :item='item'
            :tooltip='column.tooltip?.(item)' :tooltipWidth='column.tooltipWidth'
            @click='onItemClick(row, col)' @dblclick='onItemDblClick(row, col)'
            @keydown='onItemKeyDown($event, row, col)'/>
        </slot>
      </template>
    </template>
  </DataTable>
</template>

<script setup>
  import {onBeforeUnmount, onMounted, ref} from 'vue'
  import {DataTable, EditTableCell} from '@/components'
  import hotkeys from 'hotkeys-js'

  var prevscope = null                            // Previous hotkeys-js scope
  const props = defineProps({
    columns: {type:Array},                        // List of columns to display
    items: {type:Array},                          // List of items to display
    keyattr: {type:String, default:'id'},         // Key attribute for items
    infinite: {type:Boolean, default:false},      // Infinite scroll
  })
  const cells = ref([])                           // Ref of cells; 2d-array colrefs[row][col]
  const selected = ref({row:null, col:null, editing:false})  // Selected cell and edit mode
  const emit = defineEmits([
    'getNextPage',    // When requesting next page of items
    'itemUpdated',    // When item is updated (args: row, col, newval)
    'selected',       // When cell is selected or deselected (args: row, col)
  ])

  // On Mounted
  // Update transactions and initialize hotkeys
  onMounted(function() {
    prevscope = hotkeys.getScope()
    hotkeys('esc', 'edittable', function(event) { deselect(event) })
    hotkeys('up', 'edittable', function(event) { selectUp(event) })
    hotkeys('down', 'edittable', function(event) { selectDown(event) })
    hotkeys('left', 'edittable', function(event) { selectLeft(event) })
    hotkeys('shift+tab', 'edittable', function(event) { selectLeft(event) })
    hotkeys('right', 'edittable', function(event) { selectRight(event) })
    hotkeys('tab', 'edittable', function(event) { selectRight(event) })
    hotkeys('enter', 'edittable', function(event) { startEditing(event) })
    hotkeys.setScope('edittable')
  })

  // On Before Unmount
  // Stop watching hotkeys and reset scope
  onBeforeUnmount(function() {
    hotkeys.setScope(prevscope)
    hotkeys.deleteScope('edittable')
  })

  // Select Up
  // Select the cell above the current cell
  const selectUp = async function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    var {row, col, editing} = selected.value
    if (row > 0) { setSelected(row-1, col, editing) }
  }

  // Select Down
  // Select the cell below the current cell
  const selectDown = function(event) {
    if (selected.value.row == null) { return }
    event?.preventDefault()
    var {row, col, editing} = selected.value
    if (row < props.items.length-1) { setSelected(row+1, col, editing) }
  }

  // Select Left
  // Select the cell to the left of the current cell
  const selectLeft = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    var editable = []
    for (var i=0; i<props.columns.length; i++) {
      if (props.columns[i].editable) { editable.push(i) }
    }
    var {row, col, editing} = selected.value
    var index = editable.indexOf(col)
    if (index > 0) {
      var newcol = editable[index-1]
      editing = props.columns[newcol].text ? editing : false
      setSelected(row, newcol, editing)
    }
  }

  // Select Right
  // Select the cell to the right of the current cell
  const selectRight = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    var editable = []
    for (var i=0; i<props.columns.length; i++) {
      if (props.columns[i].editable) { editable.push(i) }
    }
    var {row, col, editing} = selected.value
    var index = editable.indexOf(col)
    if (index < editable.length-1) {
      var newcol = editable[index+1]
      editing = props.columns[newcol].text ? editing : false
      setSelected(row, newcol, editing)
    }
  }

  // Set Selected
  // Set the selected cell and focus the input element
  // NOTE: We don't allow editing if column.text is not defined, but the
  // event is still emitted in case you want to handle it upstream.
  const setSelected = async function(row, col, editing) {
    if (row == selected.value.row && col == selected.value.col && editing == selected.value.editing) { return }
    var column = props.columns[col]
    cells.value[selected.value.row]?.[selected.value.col]?.setSelected(false)
    cells.value[selected.value.row]?.[selected.value.col]?.setEditing(false)
    selected.value = {row:row, col:col, editing:column?.text ? editing : false}
    cells.value[row]?.[col].setSelected(row !== null ? true : false)
    cells.value[row]?.[col].setEditing(column?.text ? editing : false)
    emit('selected', row, col, editing)
  }

  // Deselect
  // Deselect the current cell
  const deselect = function(event) {
    event.preventDefault()
    if (selected.value.editing) {
      return setSelected(selected.value.row, selected.value.col, false)
    }
    setSelected(null, null, false)
  }

  // Set Td Ref
  // Saves reference to td element
  function setCellRef(elem, row, col) {
    if (!cells.value[row]) { cells.value[row] = [] }
    cells.value[row][col] = elem
  }

  // Start Editing
  // Start editing the current cell
  const startEditing = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    setSelected(selected.value.row, selected.value.col, true)
  }

  // On Item Click
  // Select the current cell
  const onItemClick = function(row, col) {
    if (!props.columns[col].editable) { return }
    if (cells[row]?.[col]?.isEditing()) { return }
    setSelected(row, col, false)
  }

  // On Item DblClick
  // Start editing the current cell
  const onItemDblClick = async function(row, col) {
    if (!props.columns[col].editable) { return }
    setSelected(row, col, true)
  }

  // On Item KeyDown
  // Handle key events when cell is selected or editing
  const onItemKeyDown = function(event, row, col) {
    if (event.key == 'ArrowDown') { selectDown(event) }
    else if (event.key == 'ArrowUp') { selectUp(event) }
    else if (event.key == 'Tab' && event.shiftKey) { selectLeft(event) }
    else if (event.key == 'Tab' && !event.shiftKey) { selectRight(event) }
    else if (event.key == 'Escape' && !event.shiftKey) { deselect(event) }
    else if (event.key == 'Enter') {
      event.preventDefault()
      var newval = cells.value[row][col].$el.querySelector('input').value
      emit('itemUpdated', row, col, newval)
    }
  }

  // Define Exposed
  // Expose this function to the parent
  defineExpose({selectUp, selectDown, selectLeft, selectRight, setSelected, deselect})
</script>

<style>
  .edittable {
    table {
      --lineheight: 28px;
      width: 100%;
      td {
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
        &.editable .tdwrap:hover { background-color: #ddd8; }
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
        &.editing .tdwrap {
          background-color: #f812 !important;
          box-shadow: inset 0px 1px 2px #0005;
        }
      }
    }

    /* Tooltip container */
    .tooltip-container {
      height: 100%;
      width: 100%;
      line-height: 16px;
    }

    /* FilterSelect */
    /* account for 2px borders */
    .selectinput-dropdown {
      left: -2px;
      top: calc(100% + 3px);
      width: calc(100% + 4px);
    }
  }
</style>
