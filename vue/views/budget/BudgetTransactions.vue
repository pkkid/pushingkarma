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
      <DataTable v-if='transactions' :items='transactions?.items' keyattr='id'>
        <template #columns='{item, rownum}'>
          <template v-for='(col, colnum) in COLUMNS' :key='colnum'>
            <Column :title='col.title' :data-rownum='rownum' :data-colnum='colnum'>
              <span v-if='col.html' v-html='col.html(item)'/>
              <span v-else-if='col.text'>{{col.text(item)}}</span>
              <span v-else>{{item[col.name]}}</span>
            </Column>
          </template>
        </template>
      </DataTable>
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {onBeforeMount, ref, watch, watchEffect} from 'vue'
  import {LayoutPaper} from '@/components'
  import {DataTable, DataTableColumn as Column} from '@/components'
  import {api, utils} from '@/utils'

  var COLUMNS = [
    {name:'account', title:'Act', editable:false, html:trx => `<i class='icon' style='--img:url(${iconpath(trx.account)})'/>`},
    {name:'date', title:'Date', editable:true, text:trx => utils.formatDate(trx.date, 'MMM DD, YYYY')},
    {name:'category', title:'Category', editable:true, text:trx => trx.category?.name},
    {name:'payee', title:'Payee', editable:true},
    {name:'amount', title:'Amount', editable:true, text:trx => utils.usd(trx.amount)},
    {name:'approved', title:'X', editable:true, html:trx => `<i class='mdi mdi-check'/>`},
    {name:'comment', title:'Comment', editable:true},
  ]

  var cancelctrl = null                 // Cancel controller
  const loading = ref(false)            // True to show loading indicator
  const search = ref('')                // Search string
  const _search = ref(search.value)     // Temp search before enter
  const transactions = ref(null)        // Transactions list
  const selected = ref({rownum:null, colnum:null, editing:false})   // Selected cell and edit mode

  onBeforeMount(async function() { updateTransactions()})
  watch(search, function() { updateTransactions() })
  watchEffect(() => _search.value = search.value)
  
  // Icon Path
  // Return icon path for the given account
  const iconpath = function(account) {
    return `/static/img/icons/${account.name.toLowerCase()}.svg`
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
      transactions.value = data
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
      /* margin-top: 20px; */
      table { width: 100%; }
      .tdwrap {
        white-space: nowrap;
        overflow: hidden;
        line-height: 26px;
      }
      .act { width:16px; }
      .date { width:90px; }
      .category { width:120px; }
      .payee { width:280px; }
      .amount { width:80px; text-align:right; }
      .x { width:15px; text-align:center; }
      .comment { width:252px; }

      .act .icon {
        background-color: var(--lightbg-fg4);
        display: inline-block;
        height: 16px;
        mask: var(--img) no-repeat center / contain;
        position: relative;
        top: 3px;
        width: 16px;
      }
    }
  }
</style>
