<template>
  <div id='budgettransactions'>
    <h3>Budget Transactions {{account ? account.name : 'ALL'}}</h3>
    <table cellpadding='0' cellspacing='0'>
      <thead><tr>
        <th class='account'><div>Bank</div></th>
        <th class='date'><div>Date</div></th>
        <th class='payee'><div>Payee</div></th>
        <th class='category'><div>Category</div></th>
        <th class='amount'><div>Amount</div></th>
        <th class='approved'><div>X</div></th>
        <th class='comment'><div>Comment</div></th>
      </tr></thead>
      <tbody>
        <tr v-for='trx in transactions' :key='trx.id'>
          <BudgetTableCell :cls='"account"' :init='trx.account.name' />
          <BudgetTableCell :cls='"date"' :init='trx.date' :editable='true' />
          <BudgetTableCell :cls='"payee"' :init='trx.payee' :editable='true' :selectall='true'/>
          <BudgetTableCell :cls='"category"' :init='trx.category ? trx.category.name : ""' :editable='true' :selectall='true' :type='"select"'/>
          <BudgetTableCell :cls='"amount blur"' :init='trx.amount' :editable='true' :type='"float"'/>
          <BudgetTableCell :cls='"approved"' :init='trx.approved' :editable='true' :type='"bool"' :selectall='true'/>
          <BudgetTableCell :cls='"comment"' :init='trx.comment' :editable='true' />
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import * as api from '@/api';
  import BudgetTableCell from './BudgetTableCell';

  export default {
    name: 'BudgetTransactions',
    components: {
      BudgetTableCell,
    },
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
    table {
      width: 100%;
      background-color: white;
    }
    th, td {
      border-bottom: 1px solid rgba(0,0,0,0.05);
      cursor: default;
      font-family: arial;
      font-size: 1.3rem;
      padding: 1px;
      text-align: left;
      div,input {
        border-radius: 2px;
        border-width: 0px;
        line-height: 1.3em;
        margin: 0px;
        overflow-x: hidden;
        padding: 5px 5px;
        transition: background-color 0.2s ease;
        white-space: nowrap;
      }
      input {
        background-color: rgba(255,255,255,0.3);
      }
    }
  }
</style>
