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
        <template #columns='{item}'>
          <Column title='Act'>
            <i class='icon' :style='`--img:url(/static/img/icons/${item.account.name.toLowerCase()}.svg)`' />
          </Column>
          <Column title='Date'>{{utils.formatDate(item.date, 'MMM DD, YYYY')}}</Column>
          <Column title='Category'>{{item.category?.name}}</Column>
          <Column title='Payee'>{{item.payee}}</Column>
          <Column title='Amount'>{{utils.usd(item.amount)}}</Column>
          <Column title='X'>{{item.approved}}</Column>
          <Column title='Comment'>{{item.comment}}</Column>
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

  var cancelctrl = null                 // Cancel controller
  const loading = ref(false)            // True to show loading indicator
  const search = ref('')                // Search string
  const _search = ref(search.value)     // Temp search before enter
  const transactions = ref(null)        // Transactions list

  onBeforeMount(async function() {
    updateTransactions()
  })
  watchEffect(() => _search.value = search.value)

  // Watch Search
  // Fetches new transactions list
  watch(search, function() { updateTransactions() })

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
