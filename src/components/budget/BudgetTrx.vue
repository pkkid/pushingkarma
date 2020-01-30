<template>
  <div id='budgettransactions' v-hotkey='keymap'>
    <h3>Budget Transactions {{account ? account.name : 'ALL'}}</h3>
    <div class='tablewrap'>
      <table cellpadding='0' cellspacing='0'>
        <thead><tr>
          <th class='account'><div>Bank</div></th>
          <th class='date'><div>Date</div></th>
          <th class='payee'><div>Payee</div></th>
          <th class='category_name'><div>Category</div></th>
          <th class='amount usdint'><div>Amount</div></th>
          <th class='approved bool'><div>X</div></th>
          <th class='comment'><div>Comment</div></th>
        </tr></thead>
        <tbody>
          <tr v-for='(trx,i) in transactions' :key='trx.id'>
            <BudgetTrxCell :item='trx' :name='"account.name"'/>
            <BudgetTrxCell @updated='updatetrx' :item='trx' :cell='cell(i,1)' :ref='cell(i,1)' :name='"date"' editable/>
            <BudgetTrxCell @updated='updatetrx' :item='trx' :cell='cell(i,2)' :ref='cell(i,2)' :name='"payee"' editable/>
            <BudgetTrxCell @updated='updatetrx' :item='trx' :cell='cell(i,3)' :ref='cell(i,3)' :name='"category.name"' :choices='categories' editable selectall/>
            <BudgetTrxCell :item='trx' :name='"amount"' :display='"usdint"'/>
            <BudgetTrxCell @updated='updatetrx' :item='trx' :cell='cell(i,4)' :ref='cell(i,4)' :name='"approved"' :display='"bool"' editable selectall />
            <BudgetTrxCell @updated='updatetrx' :item='trx' :cell='cell(i,5)' :ref='cell(i,5)' :name='"comment"' editable/>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import * as _ from 'lodash';
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import BudgetTrxCell from './BudgetTrxCell';
  import Vue from 'vue';
  var EDITCOLUMNS = 5;

  export default {
    name: 'BudgetTransactions',
    components: {BudgetTrxCell},
    data: () => ({
      cancelSearch: null,   // Cancel search token
      transactions: {},     // Displayed transactions
    }),
    computed: {
      cursor: pathify.sync('budget/cursor'),
      selected: pathify.sync('budget/selected'),
      editing: pathify.sync('budget/editing'),
      account: pathify.get('budget/account'),
      categories: pathify.get('budget/categories'),
      // key bindings
      keymap: function() { return {
        'esc': (event) => this.removeCursor(event),
        'tab': (event) => this.moveCursor(event, 1, true),
        'shift+tab': (event) => this.moveCursor(event, -1, true),
        'up': (event) => this.moveCursor(event, -EDITCOLUMNS),
        'left': (event) => this.moveCursor(event, -1),
        'down': (event) => this.moveCursor(event, EDITCOLUMNS),
        'right': (event) => this.moveCursor(event, 1),
        'enter': (event) => this.toggleEdit(event),
      };},
    },
    watch: {
      account: {immediate:true, handler:function() { this.updateTransactions(); }},
    },
    
    methods: {
      // Cell: Helper function to calculate cell number
      cell: function(r, c) { return (r * EDITCOLUMNS) + c; },

      // Move Cursor
      // Move the cursor cell in the specified direction
      moveCursor: function(event, amount=0, save=false) {
        if (this.cursor == null) { return null; }
        if ((this.editing) && (save == false)) { return null; }
        event.preventDefault();
        this.editing = false;
        var cursor = this.cursor + amount;
        if ((cursor > 0) && (cursor <= this.transactions.length * EDITCOLUMNS)) {
          this.cursor = cursor;
        }
      },

      // Remove Cursor
      // Remove the cursor from the screen (unselect)
      removeCursor: function(event) {
        if (this.cursor == null) { return null; }
        event.preventDefault();
        if (this.editing) { this.editing = false; }
        else { this.cursor = null; }
      },

      // Toggle Edit
      // Edit or save the value at the current cursor position
      toggleEdit: function(event) {
        if (this.cursor == null) { return null; }
        event.preventDefault();
        if (this.editing) { this.$refs[this.cursor][0].save(); }
        else { this.$refs[this.cursor][0].edit(); }
      },

      // Update Transactions
      // Search for and update the list of displayed transactions
      updateTransactions: async function() {
        this.cancelSearch = api.cancel(this.cancelSearch);
        var token = this.cancelSearch.token;
        try {
          var params = this.account ? {search:`bank:"${this.account.name}"`} : null;
          var {data} = await api.Budget.getTransactions(params, token);
          this.transactions = data.results;
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        }
      },
      
      // Update Transaction
      // Callback called when a single transaction has been updated
      updatetrx: function(trx) {
        var i = _.findIndex(this.transactions, {id:trx.id});
        Vue.set(this.transactions, i, trx);
      },
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
        border: 1px solid transparent;
        line-height: 1.3em;
        min-height: 26px;
        margin: 0px;
        overflow-x: hidden;
        padding: 5px 5px;
        white-space: nowrap;
        width: 100%;
      }
      &.cursor div,
      &.cursor input {
        border-radius: 3px;
        background-color: #eee;
      }
      input {
        border-radius: 3px;
        box-shadow: 0 2px 6px 2px rgba(60,64,67,.15);
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
      
      // Saving and Errors
      &.saving div { background-color: rgba(0,0,255,0.1); }
      &.error div { background-color:rgba(150,0,0,0.1); }
    }

  }
</style>
