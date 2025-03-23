<template>
  <LayoutPaper id='transactions' width='900px'>
    <template #content>
      <!-- Header -->
      <h1>
        Budget Transactions
        <div class='subtext'>Showing X of Y Transactions</div>
      </h1>
      <!-- Search -->
      <div class='searchwrap'>
        <input type='text' v-model='_search' placeholder='Search Transactions'
          class='searchinput' @keydown.enter='search=_search'>
        <transition name='fade'>
          <i v-if='_search?.length' class='mdi mdi-close' @click='search=""'/>
        </transition>
      </div>
      <!-- Transactions Table -->
      <DataTable v-if='transactions' :items='transactions?.results' keyattr='id'>
        <template #columns='{item}'>
          <Column title='Act'>--</Column>
          <Column title='Date'>
            {{utils.formatDate(item.date, 'MMM DD, YYYY')}}
          </Column>
          <Column title='Category'>
            {{item.category?.name}}
          </Column>
          <Column title='Payee'>
            {{item.payee}}
          </Column>
          <Column title='Amount'>
            {{utils.usd(item.amount)}}
          </Column>
          <Column title='X'>
            {{item.approved}}
          </Column>
          <Column title='Comment'>
            {{item.comment}}
          </Column>
        </template>
      </DataTable>
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {onBeforeMount, ref, watch, watchEffect} from 'vue'
  import {api, utils} from '@/utils'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import Column from '@/components/Column.vue'
  import DataTable from '@/components/DataTable.vue'

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
      var {data} = await api.Budget.getTransactions(params, cancelctrl.signal)
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
      input {
        width: 60%;
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
      margin-top: 20px;
      .tdwrap {
        white-space: nowrap;
        overflow: hidden;
        line-height: 26px;
      }
      .act { width:14px; }
      .date { width:88px; }
      .category { width:118px; }
      .payee { width:268px; }
      .amount { width:78px; text-align:right; }
      .x { width:14px; text-align:center; }
      .comment { width:172px; }
    }
  }
</style>
