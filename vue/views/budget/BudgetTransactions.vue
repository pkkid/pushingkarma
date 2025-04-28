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
        <div v-if='trxs' class='subtext'>Showing {{utils.intComma(trxs.items.length)}}
          of {{utils.intComma(trxs.count)}} transactions</div>
        <div v-else class='subtext'>Loading transactions..</div>
      </h1>
      <!-- Transactions Table -->
      <EditTable v-if='trxs?.items' :columns='COLUMNS' :items='trxs?.items' @getNextPage='getNextPage'/>
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {onMounted, ref, watch, watchEffect} from 'vue'
  import {EditTable, LayoutPaper} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'
  import axios from 'axios'

  var COLUMNS = [{
      name:'account', title:'Act', editable:false,
      html: trx => `<i class='icon' style='--mask:url(${iconpath(trx.account)})'/>`,
      tooltip: trx => trx.account.name,
    },{
      name:'date', title:'Date', editable:true,
      text:trx => utils.formatDate(trx.date, 'MMM DD, YYYY'),
    },{
      name:'category', title:'Category', editable:true,
      text:trx => trx.category?.name,
      choices:() => categoryChoices(),
    },{
      name:'payee', title:'Payee', editable:true,
      text:trx => trx.payee,
      tooltip: trx => trx.payee.length > 35 ? trx.payee : null,
      tooltipWidth: '350px',
    },{
      name:'amount', title:'Amount', editable:true,
      text:trx => utils.usd(trx.amount),
    },{
      name:'approved', title:'X', editable:true,
      html:trx => `<i class='mdi mdi-check'/>`,
      onEdit:(event, row) => editApproved(event, row),
    },{
      name:'comment', title:'Comment', editable:true,
      text:trx => trx.comment,
  }]

  var cancelctrl = null                       // Cancel controller
  const loading = ref(false)                  // True to show loading indicator
  const {search} = useUrlParams({search:{}})  // Method & path url params
  const _search = ref(search.value)           // Temp search before enter
  const categories = ref(null)                // Categories list
  const trxs = ref(null)                      // Transactions list

  // On Mounted
  // Update transactions and initialize hotkeys
  onMounted(function() {
    updateTransactions()
    updateCategories()
  })

  // Watch Search
  // Update transactions and _search.value
  watch(search, function() { updateTransactions() })
  watchEffect(() => _search.value = search.value)

  // Category Choices
  // Return a list of category choices for FilterSelect
  const categoryChoices = function(value) {
    if (!categories.value) { return [] }
    return categories.value.map(cat => ({id:cat.id, name:cat.name}))
  }

  // Get Next Page
  // Fetch next page of transactions
  const getNextPage = async function() {
    if (!trxs.value?.next) { return }
    console.log('Loading Next Page')
    cancelctrl = api.cancel(cancelctrl)
    try {
      var {data} = await axios.get(trxs.value.next, {signal:cancelctrl.signal})
      data.items = trxs.value.items.concat(data.items)
      trxs.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    }
  }

  // Edit Approved
  // Handle editing approved column
  const editApproved = function(event, row) {
    event.preventDefault()
    var trx = trxs.value.items[row]
  }

  // Icon Path
  // Return icon path for the given account
  const iconpath = function(account) {
    return `/static/img/icons/${account.name.toLowerCase()}.svg`
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
      .tdwrap.date { width:100px; }
      .tdwrap.category { width:140px; }
      .tdwrap.payee { width:290px; }
      .tdwrap.amount { width:90px; text-align:right; }
      .tdwrap.approved { width:30px; text-align:center; }
      .tdwrap.comment { width:253px; }
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
    /* Tooltip container style */
    .tooltip-container {
      height: 100%;
      width: 100%;
      line-height: 16px;
    }
    /* Update fsdropdown to account for 2px borders */
    .fsdropdown {
      left: -2px;
      top: calc(100% + 3px);
      width: calc(100% + 4px);
    }
  }
</style>
