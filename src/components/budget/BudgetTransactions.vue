<template>
  <div id='budgetmonth'>
    Budget Transactions {{account ? account.name : 'ALL'}}
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import * as api from '@/api';
  
  export default {
    name: 'BudgetTransactions',
    data: () => ({
      cancelSearch: null,  // Cancel search token
    }),
    computed: {
      account: pathify.sync('budget/account'),
      transactions: pathify.sync('budget/transactions'),
    },
    watch: {
      // Watch Account
      // update transactions
      account: {
        immediate: true,
        handler: async function(account) {
          this.cancelSearch = api.cancel(this.cancelSearch);
          var token = this.cancelSearch.token;
          try {
            var params = account ? {search:`bank:"${account.name}"`} : null;
            var {data} = await api.Budget.getTransactions(params, token);
            this.transactions = data.results;
          } catch(err) {
            if (!api.isCancel(err)) { throw(err); }
          }
        },
      }
    },
  };
</script>

<style lang='scss'>

</style>
