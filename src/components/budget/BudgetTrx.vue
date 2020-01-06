<template>
  <div id='budgettransactions'>
    <h3>Budget Transactions {{account ? account.name : 'ALL'}}</h3>
    <div class='tablewrap'>
      <table cellpadding='0' cellspacing='0'>
        <thead><tr>
          <th class='account'><div>Bank</div></th>
          <th class='date'><div>Date</div></th>
          <th class='payee'><div>Payee</div></th>
          <th class='category'><div>Category</div></th>
          <th class='amount usdint'><div>Amount</div></th>
          <th class='approved bool'><div>X</div></th>
          <th class='comment'><div>Comment</div></th>
        </tr></thead>
        <tbody>
          <tr v-for='trx in transactions' :key='trx.id'>
            <BudgetTrxCell :item='trx' :name='"account.name"'/>
            <BudgetTrxCell :item='trx' :name='"date"' editable/>
            <BudgetTrxCell :item='trx' :name='"payee"' editable/>
            <BudgetTrxCell :item='trx' :name='"category.name"' editable selectall/>
            <BudgetTrxCell :item='trx' :name='"amount"' :display='"usdint"'/>
            <BudgetTrxCell :item='trx' :name='"approved"' :display='"bool"' editable selectall />
            <BudgetTrxCell :item='trx' :name='"comment"' editable/>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import BudgetTrxCell from './BudgetTrxCell';

  export default {
    name: 'BudgetTransactions',
    components: {BudgetTrxCell},
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
  #budgettransactions {
    padding: 10px 20px;

    .tablewrap {
      background-color: white;
      border: 1px solid darken($lightbg-color, 20%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 10px;
      min-width: 1000px;
    }
    table {
      width: 100%;
      color: #666;
      th {
        background-color: rgba(0,0,0,0.05);
        border-top-left-radius: 2px;
        border-top-right-radius: 2px;
        font-size: 0.7em;
        color: #222;
        font-weight: 600;
      }
    }
    th, td {
      border-bottom: 1px solid rgba(0,0,0,0.05);
      cursor: default;
      font-family: arial;
      font-size: 1.3rem;
      padding: 1px 5px;
      text-align: left;
      div, input {
        border-radius: 2px;
        border-width: 0px;
        line-height: 1.3em;
        margin: 0px;
        overflow-x: hidden;
        padding: 5px 5px;
        transition: background-color 1s ease;
        white-space: nowrap;
        width: 100%;
      }
      input {
        background-color: rgba(0,0,0,0.1);
      }
      // Column types
      &.bool, &.bool input { text-align: center; }
      &.usdint, &.usdint input { text-align: right; }
      // Specific column widths
      &.account_name { width:8%; }
      &.date { width:10%; }
      &.payee { width:28%; }
      &.category_name { width:22%; }
      &.amount { width:10%; }
      &.approved { width:2%; }
      &.comment { width:22%; }
    }

  }
</style>
