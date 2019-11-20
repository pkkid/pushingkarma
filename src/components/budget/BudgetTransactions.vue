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
          <BudgetTableCell :item='trx' :name='"account.name"'/>
          <BudgetTableCell :item='trx' :name='"date"' :flags='"editable"' @changed='saveTransaction'/>
          <BudgetTableCell :item='trx' :name='"payee"' :flags='"editable selectall"' @changed='saveTransaction'/>
          <BudgetTableCell :item='trx' :name='"category.name"' :flags='"editable selectall"' @changed='saveTransaction'/>
          <BudgetTableCell :item='trx' :name='"amount"' :flags='"usd"'/>
          <BudgetTableCell :item='trx' :name='"approved"' :flags='"bool editable selectall"' @changed='saveTransaction'/>
          <BudgetTableCell :item='trx' :name='"comment"' :flags='"editable"' @changed='saveTransaction'/>
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
    components: {BudgetTableCell},
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
    methods: {
      saveTransaction: function(event) {
        console.log(event);

        // await api.Budget.saveTransaction(this.item.id, {
        //   title: this.note.title,
        //   tags: this.note.tags,
        //   body: this.editor.getHTML()
        // });

        // data[name] = input.val();
        // data = self.clean_data(data);
        // var url = row.data('url');
        // var xhr = self.request(item, url, method, data, {
        //   done: function(data, textStatus, jqXHR) {
        //     if (display) { self.item_display(item, data[name]); }
        //     if (callback) { callback(); }
        //   },
        //   fail: function(jqXHR, textStatus, errorThrown) {
        //     if (display) { self.item_display(item, data[name]); }
        //   }
        // });

      },
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
      padding: 1px 5px;
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
        width: 100%;
      }
      input {
        background-color: rgba(0,0,0,0.1);
      }
      &.account_name { width:8%; }
      &.date { width:10%; }
      &.payee { width:28%; }
      &.category_name { width:22%; }
      &.amount { width:10%; text-align:right; }
      &.approved { width:2%; text-align:center; }
      &.comment { width:22%; }
    }
  }
</style>
