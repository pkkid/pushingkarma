<template>
  <DataTable class='edittable' :items='items' :keyattr='keyattr' :infinite='infinite'
    @getNextPage='emit("getNextPage", $event)'>
    <template #columns='{item, row}'>
      <template v-for='(column, col) in columns' :key='col'>
        <slot name='cell' :row='row' :col='col' :column='column' :item='item'>
          <EditTableCell :ref='elem => setCellRef(elem, row, col)' :column='column' :item='item'
            :class='column.class?.(item)' :tooltip='column.tooltip?.(item)' :tooltipWidth='column.tooltipWidth'
            @click='onItemClick($event, row, col)' @dblclick='onItemDblClick($event, row, col)'
            @keydown='onItemKeyDown($event, row, col)'/>
        </slot>
      </template>
    </template>
  </DataTable>
</template>

<script setup>
  import {onBeforeUnmount, onMounted, ref} from 'vue'
  import {DataTable, EditTableCell} from '@/components'
  import {utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  // Columns is an array of column objects containing the following properties:
  //  name (req):   Column name (used as key in items)
  //  title (req):  Column title (displayed in header)
  //  editable:     If true, cell is editable (no input if using html option)
  //  text:         Func(item) to get text to display
  //  html:         Func(item) Optionally specify html to display instead of text (editing will be disabled)
  //  clean:        Func(newval) to clean user value before sending to server
  //  choices:      Func(item) should return all available choices for column (for select dropdown)
  //  class:        Func(item) to add additional classes to tr of the table
  //  default:      Func(item) to get default value for item (ctrl+backspace sets this value)
  //  selectall:    If true, select all input text when editing starts
  //  tooltip:      Func(item) to get tooltip html (if not defined, no tooltip is shown)
  //  tooltipWidth: (str) Set a static width for the tooltip (ex: 350px)
  var prevscope = null                            // Previous hotkeys-js scope
  var undostack = []                              // Undo stack {row, col, oldval, newval}
  var redostack = []                              // Redo stack {row, col, oldval, newval}
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
    'itemSelected',   // When cell is selected or deselected (args: row, col)
    'itemUpdated',    // When item is updated (args: row, col, newval)
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
    hotkeys('enter, shift+enter', 'edittable', function(event) { startEditing(event) })
    hotkeys('ctrl+z', 'edittable', function(event) { undo(event) })
    hotkeys('ctrl+y', 'edittable', function(event) { redo(event) })
    hotkeys('alt+backspace', 'edittable', function(event) { resetToDefault(event) })
    hotkeys.setScope('edittable')
  })

  // On Before Unmount
  // Stop watching hotkeys and reset scope
  onBeforeUnmount(function() {
    hotkeys.setScope(prevscope)
    hotkeys.deleteScope('edittable')
  })

  // Get Cell
  // Get cell ref for the given row and column
  const getCell = function(row, col) {
    return cells.value[row]?.[col]
  }

  // Select Up
  // Select the cell above the current cell
  const selectUp = async function(event) {
    if (selected.value.row == null) { return }
    event?.preventDefault()
    var {row, col, editing} = selected.value
    if (row > 0) { setSelected(event, row-1, col, editing) }
  }

  // Select Down
  // Select the cell below the current cell
  const selectDown = function(event) {
    if (selected.value.row == null) { return }
    event?.preventDefault()
    var {row, col, editing} = selected.value
    if (row < props.items.length-1) { setSelected(event, row+1, col, editing) }
  }

  // Select Left
  // Select the cell to the left of the current cell
  const selectLeft = function(event) {
    if (selected.value.row == null) { return }
    event?.preventDefault()
    var editable = []
    for (var i=0; i<props.columns.length; i++) {
      if (props.columns[i].editable) { editable.push(i) }
    }
    var {row, col, editing} = selected.value
    var index = editable.indexOf(col)
    if (index > 0) {
      var newcol = editable[index-1]
      editing = props.columns[newcol].html ? false : editing
      setSelected(event, row, newcol, editing)
    }
  }

  // Select Right
  // Select the cell to the right of the current cell
  const selectRight = function(event) {
    if (selected.value.row == null) { return }
    event?.preventDefault()
    var editable = []
    for (var i=0; i<props.columns.length; i++) {
      if (props.columns[i].editable) { editable.push(i) }
    }
    var {row, col, editing} = selected.value
    var index = editable.indexOf(col)
    if (index < editable.length-1) {
      var newcol = editable[index+1]
      editing = props.columns[newcol].text ? editing : false
      setSelected(event, row, newcol, editing)
    }
  }

  // Set Selected
  // Set the selected cell and focus the input element
  // NOTE: We don't allow editing if column.text is not defined, but the
  // event is still emitted in case you want to handle it upstream.
  const setSelected = async function(event, row, col, editing) {
    if (row == selected.value.row && col == selected.value.col && editing == selected.value.editing) { return }
    var column = props.columns[col]
    getCell(selected.value.row, selected.value.col)?.setSelected(false)
    getCell(selected.value.row, selected.value.col)?.setEditing(false)
    selected.value = {row:row, col:col, editing:column?.html ? false : editing}
    getCell(row, col)?.setSelected(row !== null ? true : false)
    getCell(row, col)?.setEditing(column?.html ? false : editing)
    emit('itemSelected', event, row, col, editing)
  }

  // Deselect
  // Deselect the current cell
  const deselect = function(event) {
    event.preventDefault()
    var newrow = selected.value.editing ? selected.value.row : null
    var newcol = selected.value.editing ? selected.value.col : null
    setSelected(event, newrow, newcol, false)
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
    setSelected(event, selected.value.row, selected.value.col, true)
  }

  // On Item Click
  // Select the current cell
  const onItemClick = function(event, row, col) {
    if (!props.columns[col].editable) { return }
    if (getCell(row, col)?.isEditing()) { return }
    setSelected(event, row, col, false)
  }

  // On Item DblClick
  // Start editing the current cell
  const onItemDblClick = async function(event, row, col) {
    if (!props.columns[col].editable) { return }
    setSelected(event, row, col, true)
  }

  // On Item KeyDown
  // Handle key events when cell is selected or editing
  const onItemKeyDown = function(event, row, col) {
    if (event.key == 'ArrowDown') { selectDown(event) }
    else if (event.key == 'ArrowUp') { selectUp(event) }
    else if (event.key == 'Escape') { deselect(event) }
    else if (event.key == 'Tab' && event.shiftKey) { selectLeft(event) }
    else if (event.key == 'Tab' && !event.shiftKey) { selectRight(event) }
    else if (event.key == 'z' && event.ctrlKey) { undo(event) }
    else if (event.key == 'y' && event.ctrlKey) { redo(event) }
    else if (event.key == 'Enter') {
      event.preventDefault()
      var column = props.columns[col]
      var oldval = utils.getItemValue(props.items[row], column)
      var newval = getCell(row, col).$el.querySelector('input').value
      if (oldval != newval) {
        getCell(row, col).setError(null)
        emit('itemUpdated', event, row, col, newval)
        addUndo(row, col, oldval, newval)
      } else {
        selectDown(event)
      }
    }
  }

  // Add Undo
  // Add an item to the undo stack
  const addUndo = function(row, col, oldval, newval) {
    undostack.push({row, col, oldval, newval})
    redostack = []
  }

  // Undo
  // Undo the last action
  const undo = function(event) {
    event.preventDefault()
    if (undostack.length == 0) { return }
    const {row, col, oldval, newval} = undostack.pop()
    redostack.push({row, col, oldval, newval})
    emit('itemUpdated', event, row, col, oldval, true)
    setSelected(event, row, col, false)
  }

  // Redo
  // Redo the previous action
  const redo = function(event) {
    event.preventDefault()
    if (redostack.length == 0) { return }
    const {row, col, oldval, newval} = redostack.pop()
    undostack.push({row, col, oldval, newval})
    emit('itemUpdated', event, row, col, newval, true)
    setSelected(event, row, col, false)
  }

  // Reset to Default
  // Reset the current cell to its default value
  const resetToDefault = function(event) {
    event.preventDefault()
    if (selected.value.row == null) { return }
    var {row, col} = selected.value
    var column = props.columns[col]
    if (!column.default) { return }
    var oldval = utils.getItemValue(props.items[row], column)
    var newval = column.default(props.items[row])
    if (oldval != newval) {
      emit('itemUpdated', event, row, col, newval)
      addUndo(row, col, oldval, newval)
    }
  }

  // Clear Undo Redo Stack
  // Resets the undo and redo stacks
  const clearUndoRedoStack = function() {
    undostack = []
    redostack = []
  } 

  // Define Exposed
  // Expose this function to the parent
  defineExpose({getCell, selectUp, selectDown, selectLeft, selectRight,
    setSelected, deselect, addUndo, clearUndoRedoStack})
</script>

<style>
  .edittable {
    table {
      --lineheight: 27px;
      width: 100%;
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
