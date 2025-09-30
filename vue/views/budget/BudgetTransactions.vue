<template>
  <LayoutPaper id='transactions' width='1000px'>
    <template #content>
      <!-- Search -->
      <div class='searchwrap'>
        <input type='text' v-model='_search' placeholder='Search Transactions'
          class='searchinput' @keydown.enter='search=_search || null'>
        <transition name='fade'>
          <i v-if='_search?.length' class='mdi mdi-close' @click='search=""; _search=""'/>
        </transition>
      </div>
      <!-- Header -->
      <h1>Budget Transactions
        <div v-if='trxs' class='subtext'>Showing {{utils.intComma(trxs.items.length)}}
          of {{utils.intComma(trxs.count)}} transactions</div>
        <div v-else class='subtext'>Loading transactions...</div>
      </h1>
      <!-- Transactions Table -->
      <EditTable v-if='trxs?.items?.length' ref='edittable' :columns='COLUMNS' :items='trxs?.items'
        infinite :nextpage='trxs?.next' @getNextPage='getNextPage' @itemSelected='onItemSelected'
        @itemUpdated='onItemUpdated'>
        <template #scrollwatch>
          <IconMessage icon='pk' animation='gelatine' text='Loading more transactions' ellipsis/>
        </template>
      </EditTable>
      <!-- Loading & Empty -->
      <IconMessage v-else-if='loading' icon='pk' iconsize='40px' animation='gelatine' text='Loading transactions' ellipsis/>
      <IconMessage v-else icon='mdi-robot-angry-outline' iconsize='40px' text='No transactions found.' />
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {computed, nextTick, onMounted, ref, watch} from 'vue'
  import {EditTable, IconMessage, LayoutPaper} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'
  import axios from 'axios'

  var COLUMNS = [{
      name:'account', title:'Act', editable:false,
      html: trx => accountIcon(trx),
      tooltip: trx => utils.tmpl(`{{account.name}}<div class='subtext'>ID: {{id}}</div>`, trx),
    },{
      name:'date', title:'Date', editable:true,
      format: text => utils.formatDate(text, 'YYYY-MM-DD'),
      class: trx => trx.date != trx.original_date ? 'modified' : '',
      default: trx => trx.original_date,
      clean: newval => utils.formatDate(newval, 'YYYY-MM-DD'),
      tooltip: trx => origTooltip(trx, 'date'),
    },{
      name:'category', title:'Category', editable:true,
      text: trx => trx.category?.name,
      choices: (trx) => categoryChoices(),
      clean: newval => newval == '<clear>' ? '' : newval,
      selectall: true,
    },{
      name:'payee', title:'Payee', editable:true,
      class: trx => trx.payee != trx.original_payee ? 'modified' : '',
      tooltip: trx => payeeTooltip(trx),
      tooltipWidth: '350px',
      default: trx => trx.original_payee,
    },{
      name:'amount', title:'Amount', editable:true,
      format: text => utils.usd(text),
      class: trx => trx.amount != trx.original_amount ? 'modified' : '',
      default: trx => trx.original_amount,
      clean: newval => newval.replace('$','').replace(',',''),
      tooltip: trx => origTooltip(trx, 'amount'),
    },{
      name:'approved', title:'X', editable:true,
      html: trx => trx.approved ? `<i class='mdi mdi-check'/>` : '',
    },{
      name:'comment', title:'Comment', editable:true,
  }]

  const props = defineProps({
    demo: {type:Boolean},                     // Enables demo mode
  })
  var cancelctrl = null                       // Cancel controller
  var updating = false                        // True if updating a transaction
  const loading = ref(false)                  // True to show loading indicator
  const {search} = useUrlParams({search:{}})  // Method & path url params
  const _search = ref(search.value)           // Temp search before enter
  const categories = ref(null)                // Categories list
  const trxs = ref(null)                      // Transactions list
  const summary = ref(null)                   // Transactions summary
  const edittable = ref(null)                 // Ref to EditTable component

  // Search String
  // Search string for the transactions
  const searchstr = computed(function() {
    var str = search.value || ''
    str += props.demo ? ` amount<100 AND amount>-100` : ''
    return str.trim()
  })

  // On Mounted
  // Update transactions and initialize hotkeys
  onMounted(function() {
    updateTransactions()
    updateCategories()
  })

  // Watch Search
  // Update transactions and _search.value
  watch(search, function() {
    _search.value = search.value
    updateTransactions()
  })

  // Category Choices
  // Return a list of category choices for SelectInput
  const categoryChoices = function(value) {
    if (!categories.value) { return [] }
    return [{id:-1, name:'<clear>'}].concat(
      categories.value.map(cat => ({id:cat.id, name:cat.name}))
    )
  }

  // Get Next Page
  // Fetch next page of transactions
  const getNextPage = async function(url) {
    if (!trxs.value?.next) { return }
    cancelctrl = api.cancel(cancelctrl)
    try {
      var {data} = await axios.get(url, {signal:cancelctrl.signal})
      data.items = trxs.value.items.concat(data.items)
      trxs.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    }
  }

  // Account Icon
  // Return html to display account icon
  const accountIcon = function(trx) {
    var actname = trx.account.name.toLowerCase()
    var path = `/static/img/icons/${actname}.svg`
    return utils.tmpl(`<i class='icon' style='--mask:url(${path})'/>`, {path})
  }

  // Original Tooltip
  // Tooltip shows the original value of the cell
  const origTooltip = function(trx, colname) {
    var column = COLUMNS.find(c => c.name == colname)
    var origval = utils.getItemValue(trx, column, trx[`original_${colname}`])
    var curval = utils.getItemValue(trx, column)
    if (origval == curval) { return null }
    return utils.tmpl(`Originally: {{origval}}<div class='subtext'>alt+backspace to reset</div>`, {origval})
  }

  // Payee Tooltip
  // Tooltip shows the original value of the cell
  const payeeTooltip = function(trx) {
    var tooltip = origTooltip(trx, 'payee')
    if (tooltip) { return tooltip }
    if (trx.payee.length > 35) { return utils.tmpl(`{{payee}}`, trx) }
    return null
  }

  // On Selected
  // Handle item selected event
  const onItemSelected = function(event, row, col, editing) {
    var column = COLUMNS[col]
    if (editing && column?.name == 'approved') {
      var trx = trxs.value.items[row]
      onItemUpdated(event, row, col, !trx.approved)
      edittable.value.addUndo(row, col, trx.approved, !trx.approved)
    }
  }

  // On Item Updated
  // Handle item updated event
  const onItemUpdated = async function(event, row, col, newval, isundo=false) {
    if (updating) { return } else { updating = true } 
    var column = COLUMNS[col]
    var trx = trxs.value.items[row]
    newval = column.clean?.(newval) ?? newval
    var params = {[column.name]: newval}
    try {
      // Update server if value changed
      var oldval = trx[column.name]
      if (newval != oldval) {
        var {data} = await api.Budget.updateTransaction(trx.id, params)
        trxs.value.items[row] = data
        edittable.value.getCell(row, col).animateBg(isundo ? '#8404':'#0a48')
      }
      // If saved from input enter key, select the next item
      if (event?.type === 'keydown' && event.key === 'Enter') {
        if (event.shiftKey) { edittable.value.selectUp(event) }
        else { edittable.value.selectDown(event) }
      }
    } catch (err) {
      // Set an error message on the cell
      var message = err.response?.data?.errors?.[column.name]
      edittable.value.getCell(row, col).setError(message)
      await nextTick()
      edittable.value.getCell(row, col).$el.querySelector('input').focus()
    } finally {
      updating = false
    }
  }

  // Update Categories
  // Fetch categories from the server
  const updateCategories = async function() {
    var {data} = await api.Budget.listCategories()
    categories.value = data.items
  }

  // Update Transactions
  // Fetch transactions from the server
  const updateTransactions = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search:searchstr.value}
      var [trxResponse, summaryResponse] = await Promise.all([
        api.Budget.listTransactions(params, cancelctrl.signal),
        api.Budget.summarizeTransactions(params, cancelctrl.signal)
      ])
      trxs.value = trxResponse.data
      summary.value = summaryResponse.data
      edittable.value?.deselect(null, false)
      edittable.value?.clearUndoRedoStack()
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }

  // Update Transactions Summary
  // Fetch transactions from the server
  const updateSummary = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search:searchstr.value}
      var {data} = await api.Budget.listTransactions(params, cancelctrl.signal)
      trxs.value = data
      edittable.value?.deselect(null, false)
      edittable.value?.clearUndoRedoStack()
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

    .edittable {
      .account { width:36px; text-align:center; }
      .date { width:100px; text-align:left; }
      .category { width:150px; text-align:left; }
      .payee { width:300px; text-align:left; .tdwrap { max-width:300px; }}
      .amount { width:100px; text-align:right; }
      .approved { width:36px; text-align:center; }
      .comment { width:214px; text-align:left; }
      
      .account .tdwrap {
        display: flex;
        align-items: center;
        justify-content: center;
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
