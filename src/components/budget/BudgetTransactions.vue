<template>
  <div id='budgetmonth'>
    Budget Transactions {{account ? account.name : 'ALL'}}
    <table cellpadding='0' cellspacing='0'>
      <thead><tr>
        <th class='account'>Bank</th>
        <th class='date'>Date</th>
        <th class='payee'>Payee</th>
        <th class='category'>Category</th>
        <th class='amount'>Amount</th>
        <th class='approved'>X</th>
        <th class='comment'>Comment</th>
      </tr></thead>
      <tbody>
        <tr v-for='trx in transactions' :key='trx.id'>
          <td class='account'><div>{{trx.account.name}}</div></td>
          <td class='date editable'><div>{{trx.date}}</div></td>
          <td class='payee editable selectall'><div>{{trx.payee}}</div></td>
          <td class='category editable selectall'><div>{{trx.category ? trx.category.name : ''}}</div></td>
          <td class='amount float blur'><div>{{trx.amount}}</div></td>
          <td class='approved bool selectall'><div>X</div></td>
          <td class='comment editable'><div>{{trx.comment}}</div></td>
        </tr>
      </tbody>
    </table>
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
