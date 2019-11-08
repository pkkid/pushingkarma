<template>
  <div id='budgetmonth'>
    Budget Transactions {{viewAccount}}
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  
  export default {
    name: 'BudgetTransactions',
    computed: {
      viewAccount: pathify.sync('budget/viewAccount'),
    },
  };
</script>

<style lang='scss'>

</style>
