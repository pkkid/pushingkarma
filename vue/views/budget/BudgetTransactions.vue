<template>
  <LayoutPaper id='transactions' width='1000px'>
    <template #content>
      <!-- Search -->
      <div class='searchwrap'>
        <input type='text' v-model='_search' placeholder='Search Transactions'
          class='searchinput' @keydown.enter='search=_search'>
        <transition name='fade'>
          <i v-if='_search?.length' class='mdi mdi-close' @click='search=""; _search=""'/>
        </transition>
      </div>
      <!-- Header -->
      <h1>
        Budget Transactions
        <div class='subtext'>Showing X of Y Transactions</div>
      </h1>
      <!-- Transactions Table -->
      <DataTable v-if='trxs' ref='trxstable' :items='trxs?.items' keyattr='id'>
        <template #columns='{item, row}'>
          <template v-for='(column, col) in COLUMNS' :key='col'>
            <!-- Editable Column -->
            <Column v-if='column.editable' :name='column.name' :title='column.title' :data-row='row' :data-colnum='col'
              class='editable' :class='{selected:isSelected(row, col), editing:isEditing(row, col)}'
              @click='onItemClick(row, col)' @dblclick='onItemDblClick(row, col)'>
              <template v-if='isEditing(row, col)'>
                <input :value='column.text(item)' spellcheck='false' autocomplete='off' autocorrect='off' autocapitalize='off'
                  @keydown='onItemKeyDown($event, row, col)'/>
              </template>
              <template v-else>
                <span v-if='column.html' class='fakeinput' v-html='column.html(item)'/>
                <span v-else class='fakeinput'>{{column.text(item)}}</span>
              </template>
            </Column>
            <!-- Non-Editable Column -->
            <Column v-else :name='column.name' :title='column.title' :data-row='row' :data-col='col'>
              <span v-if='column.html' class='fakeinput' v-html='column.html(item)'/>
              <span v-else class='fakeinput'>{{column.text(item)}}</span>
            </Column>
          </template>
        </template>
      </DataTable>
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {nextTick, onBeforeUnmount, onMounted, ref, watch, watchEffect} from 'vue'
  import {LayoutPaper} from '@/components'
  import {DataTable, DataTableColumn as Column} from '@/components'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  var COLUMNS = [
    {name:'account', title:'Act', editable:false, html:trx => `<i class='icon' style='--mask:url(${iconpath(trx.account)})'/>`},
    {name:'date', title:'Date', editable:true, text:trx => utils.formatDate(trx.date, 'MMM DD, YYYY')},
    {name:'category', title:'Category', editable:true, text:trx => trx.category?.name},
    {name:'payee', title:'Payee', editable:true, text:trx => trx.payee},
    {name:'amount', title:'Amount', editable:true, text:trx => utils.usd(trx.amount)},
    {name:'approved', title:'X', editable:true, type:Boolean, html:trx => `<i class='mdi mdi-check'/>`},
    {name:'comment', title:'Comment', editable:true, text:trx => trx.comment},
  ]

  var cancelctrl = null                 // Cancel controller
  var prevscope = null                  // Previous hotkeys-js scope
  const loading = ref(false)            // True to show loading indicator
  const search = ref('')                // Search string
  const _search = ref(search.value)     // Temp search before enter
  const trxs = ref(null)                // Transactions list
  const trxstable = ref(null)           // Ref to transactions table
  const selected = ref({row:null, colnum:null, editing:false})   // Selected cell and edit mode

  // On Mounted
  // Update transactions and initialize hotkeys
  onMounted(function() {
    updateTransactions()
    prevscope = hotkeys.getScope()
    hotkeys('esc', 'trxs', function(event) { deselect(event) })
    hotkeys('up', 'trxs', function(event) { selectUp(event) })
    hotkeys('down', 'trxs', function(event) { selectDown(event) })
    hotkeys('left', 'trxs', function(event) { selectLeft(event) })
    hotkeys('shift+tab', 'trxs', function(event) { selectLeft(event) })
    hotkeys('right', 'trxs', function(event) { selectRight(event) })
    hotkeys('tab', 'trxs', function(event) { selectRight(event) })
    hotkeys('enter', 'trxs', function(event) { startEditing(event) })
    hotkeys.setScope('trxs')
  })

  // On Before Unmount
  // Stop watching hotkeys and reset scope
  onBeforeUnmount(function() {
    hotkeys.setScope(prevscope)
    hotkeys.deleteScope('trxs')
  })

  watch(search, function() { updateTransactions() })
  watchEffect(() => _search.value = search.value)

  // Icon Path
  // Return icon path for the given account
  const iconpath = function(account) {
    return `/static/img/icons/${account.name.toLowerCase()}.svg`
  }

  // Is Editing
  // Return true if the given row and column is currently being edited
  const isEditing = function(row, col) {
    return selected.value.row == row && selected.value.col == col && selected.value.editing
  }

  // Is Selected
  // Return true if the given row and column is currently selected
  const isSelected = function(row, col) {
    return selected.value.row == row && selected.value.col == col
  }

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
    if (row < trxs.value.items.length-1) { setSelected(row+1, col, editing) }
  }

  // Select Left
  // Select the cell to the left of the current cell
  const selectLeft = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    var editable = []
    for (var i=0; i<COLUMNS.length; i++) {
      if (COLUMNS[i].editable) { editable.push(i) }
    }
    var {row, col, editing} = selected.value
    var index = editable.indexOf(col)
    if (index > 0) {
      var newcol = editable[index-1]
      editing = COLUMNS[newcol].type == Boolean ? false : editing
      setSelected(row, newcol, editing)
    }
  }

  // Select Right
  // Select the cell to the right of the current cell
  const selectRight = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    var editable = []
    for (var i=0; i<COLUMNS.length; i++) {
      if (COLUMNS[i].editable) { editable.push(i) }
    }
    var {row, col, editing} = selected.value
    var index = editable.indexOf(col)
    if (index < editable.length-1) {
      var newcol = editable[index+1]
      editing = COLUMNS[newcol].type == Boolean ? false : editing
      setSelected(row, newcol, editing)
    }
  }

  // Select None
  // Deselect the current cell
  const deselect = function(event) {
    event.preventDefault()
    if (selected.value.row == null) { return }
    if (selected.value.editing) { selected.value.editing = false }
    else { selected.value = {row:null, colnum:null, editing:false} }
  }

  // Set Selected
  // Set the selected cell and focus the input element
  const setSelected = async function(row, col, editing) {
    console.log(`setSelected(${row}, ${col}, ${editing})`)
    selected.value = {row:row, col:col, editing:editing}
    await nextTick()
    const input = trxstable.value.$el.querySelector('input')
    if (input) {
      input.focus()
      const len = input.value.length
      input.setSelectionRange(len, len)
    }
  }

  // Start Editing
  // Start editing the current cell
  const startEditing = function(event) {
    if (selected.value.row == null) { return }
    event.preventDefault()
    selected.value.editing = true
  }

  // On Item Click
  // Select the current cell
  const onItemClick = function(row, col) {
    if (isEditing(row, col)) { return }
    console.log(`onItemClick(${row}, ${col})`)
    selected.value = {row:row, col:col, editing:false}
  }

  // On Item DblClick
  // Start editing the current cell
  const onItemDblClick = async function(row, col) {
    console.log(`onItemClick(${row}, ${col})`)
    selected.value = {row:row, col:col, editing:true}
    await nextTick()
    document.querySelector(`.datatable input`).focus()
  }

  // On Item KeyDown
  // Handle key events when cell is selected or editing
  const onItemKeyDown = function(event, row, col) {
    console.log(`onItemClick(event, ${row}, ${col})`)
    if (event.key == 'ArrowDown') { selectDown(event) }
    else if (event.key == 'ArrowUp') { selectUp(event) }
    else if (event.key == 'Tab' && event.shiftKey) { selectLeft(event) }
    else if (event.key == 'Tab' && !event.shiftKey) { selectRight(event) }
    else if (event.key == 'Escape' && !event.shiftKey) { deselect(event) }
    else if (event.key == 'Enter') { event.preventDefault() }
  }

  // Update Transactions
  // Fetch transactions from the server
  const updateTransactions = async function() {
    if (search.value == null) { return }
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search:search.value}
      var {data} = await api.Budget.listTransactions(params, cancelctrl.signal)
      trxs.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }
</script>

<style>
  #transactions {
    .searchwrap {
      text-align: right;
      display: flex;
      justify-content: flex-end;
      margin-top: -10px;
      align-items: center;
      padding-top: 22px;
      float: right;
      width: 550px;
      input {
        width: 100%;
        border-radius: 20px;
        padding: 5px 15px;
      }
      .mdi-close {
        position: absolute;
        right: 40px;
        font-size: 14px;
      }
    }

    .datatable {
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
            min-height: 32px;
            overflow: hidden;
            padding: 0px;
            white-space: nowrap;
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
            input { color: #111; }
          }
          &.editable .tdwrap:hover { background-color: #8882; }
          &.selected .tdwrap {
            border: 2px solid var(--accent);
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
      .tdwrap.date { width:100px; }
      .tdwrap.category { width:140px; }
      .tdwrap.payee { width:290px; }
      .tdwrap.amount { width:90px; text-align:right; }
      .tdwrap.approved { width:28px; text-align:center; }
      .tdwrap.comment { width:255px; }
      .tdwrap.account {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 33px;
        .icon {
          background-color: var(--lightbg-fg4);
          display: inline-block;
          height: 16px;
          mask: var(--mask) no-repeat center / contain;
          position: relative;
          top: 3px;
          width: 16px;
        }
      }
    }
  }
</style>
