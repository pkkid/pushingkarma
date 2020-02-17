<template>
  <div id='budgettransactions' v-hotkey='keymap'>
    <div id='searchwrap'>
      <input id='search' type='text' v-model='search' @keyup.enter.prevent='updateTransactions'/>
    </div>
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
      search: '',           // Current search string
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
      account: {immediate:true, handler:function() {
        this.resetPage();
        this.updateTransactions();
        
      }},

    },
    mounted: function() {
      this.resetPage();
    },
    
    methods: {
      // Cell: Helper function to calculate cell number
      cell: function(r, c) { return (r * EDITCOLUMNS) + c; },

      // Move Cursor
      // Move the cursor cell in the specified direction
      moveCursor: function(event, amount=0, save=false) {
        if (this.cursor == null) { return null; }
        if (this.editing) {
          if (save == false) { return null; }
          else { this.$refs[this.cursor][0].save(); }
        }
        event.preventDefault();
        // Move the cursor to the next position
        var cursor = this.cursor + amount;
        if ((cursor > 0) && (cursor <= this.transactions.length * EDITCOLUMNS)) {
          this.cursor = cursor;
          if (this.editing) {
            this.$refs[this.cursor][0].edit();
          }
        }
      },

      // Remove Cursor
      // Remove the cursor from the screen (unselect)
      removeCursor: function(event) {
        if (this.cursor == null) { return null; }
        event.preventDefault();
        if (this.editing) { this.$refs[this.cursor][0].cancel(); }
        else { this.cursor = null; }
      },

      // Reset Page
      // Reset editing variable when page loads
      resetPage: function() {
        this.cursor = null;
        this.editing = false;
        this.search = '';
      },

      // Toggle Edit
      // Edit or save the value at the current cursor position
      toggleEdit: function(event) {
        if (this.cursor == null) { return null; }
        event.preventDefault();
        if (this.editing) { this.moveCursor(event, EDITCOLUMNS, true); }
        else { this.$refs[this.cursor][0].edit(); }
      },

      // Update Transactions
      // Search for and update the list of displayed transactions
      updateTransactions: async function() {
        this.cancelSearch = api.cancel(this.cancelSearch);
        var token = this.cancelSearch.token;
        try {
          var params = {search: this.search};
          if (this.account) { params.search += ` bank:"${this.account.name}"`; }
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
    th, td {
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
    #searchwrap {
      float: right;
      width: 500px;
      margin-top: 10px;
      input {
        background-color: #eee;
        border-radius: 20px;
        border-color: #ccc;
        font-size: 1.4rem;
        font-weight: 500;
        height: 34px;
        line-height: 34px;
        padding: 0px 40px 0px 15px;
      }
    }
  }
</style>
