<template>
  <DataTable v-if='trxs' ref='root' :items='trxs?.items' keyattr='id' :infinite='true' @getNextPage='getNextPage'>
    <template #columns='{item, row}'>
      <template v-for='(column, col) in columns' :key='col'>
        <BudgetTransactionsColumn :ref='elem => settdref(elem, row, col)' :column='column' :trx='item'
          :tooltip='tooltipText(row, col)' :tooltipWidth='tooltipWidth(row, col)'
          @click='onItemClick(row, col)' @dblclick='onItemDblClick(row, col)'
          @keydown='onItemKeyDown($event, row, col)'/>
      </template>
    </template>
  </DataTable>
</template>

<script setup>
  import {onBeforeUnmount, onMounted, ref, watch} from 'vue'
  import hotkeys from 'hotkeys-js'

  var prevscope = null                      // Previous hotkeys-js scope
  const props = defineProps({
    columns: {type:Array},                  // List of columns to display
    items: {type:Array},                    // List of items to display
  })
  const root = ref(null)                    // Ref to root component
  const cells = ref([])                     // Ref of cells; 2d-array colrefs[row][col]
  const selected = ref({row:null, col:null, editing:false})   // Selected cell and edit mode


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
    event.preventDefault()
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

  // Select None
  // Deselect the current cell
  const deselect = function(event) {
    event.preventDefault()
    setSelected(null, null, false)
  }

  // Set Selected
  // Set the selected cell and focus the input element
  const setSelected = async function(row, col, editing) {
    cells.value[selected.value.row]?.[selected.value.col]?.setSelected(false)
    cells.value[selected.value.row]?.[selected.value.col]?.setEditing(false)
    selected.value = {row:row, col:col, editing:editing}
    cells.value[row]?.[col].setSelected(row !== null ? true : false)
    cells.value[row]?.[col].setEditing(editing)
  }

  // Set Td Ref
  // Saves reference to td element
  function settdref(el, row, col) {
    if (!cells.value[row]) { cells.value[row] = [] }
    cells.value[row][col] = el
  }

  // Start Editing
  // Start editing the current cell
  const startEditing = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    var column = props.columns[selected.value.col]
    if (column.onEdit) { return column.onEdit(event, selected.value.row) }
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
      console.log('Save trx!')
      event.preventDefault()
    }
  }
</script>
