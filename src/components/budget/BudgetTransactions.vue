<template>
    <div id='budgettransactions' v-if='items' v-hotkey='keymap'>
      <h1>
        Budget Transactions
        <div class='subtext'>{{account ? account.name : 'All transactions'}}, Showing {{this.items.length}} of ??</div>
      </h1>
      <input v-model.lazy='search' ref='search' class='input search' icon='magnify'
        placeholder='Search Transactions' autocomplete='off' rounded/>
      <div v-click-outside='cancelAll'>
        <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
          <template slot-scope='props'>
            <b-table-column v-for='c in props.row' :key='c.name' :label='c.name' :width='c.width'
              :numeric='c.numeric' :header-class='c.cls' :cell-class='c.cls'>
              <TableCell :data='c' :ref='`c${c.tabindex}`' @click.native='clickSetFocus($event, c.tabindex)'/>
            </b-table-column>
          </template>
          <template slot='empty'>No items to display.</template>
        </b-table>
      </div>
    </div>
    <div v-else id='#budgettransactions'>
      <h1>Budget Transactions<div class='subtext'>Loading transactions..</div></h1>
      <b-loading active :is-full-page='false'/>
    </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import TableMixin from '@/components/TableMixin';
  import Vue from 'vue';

  export default {
    name: 'BudgetTransactions',
    mixins: [TableMixin],
    data: function() {
      return {
        cancelsearch: null,   // Cancel search token
        search: '',           // Current search string
        transactions: null,     // Displayed transactions
        columns: [
          {name:'Name', field:'account.name'},
          {name:'Date', field:'date', width:'100px', editable:true},
          {name:'Category', field:'category.name', width:'160px', editable:true},
          {name:'Payee', field:'payee', editable:true},
          {name:'Amount', field:'amount', display:utils.usd, select:true, numeric:true, editable:true, width:'100px', cls:'blur'},
          {name:'X', field:'approved', cls:'check', width:'26px', editable:true},
          {name:'Comment', field:'comment', width:'200px', editable:true},
        ],
      };
    },
    computed: {
      account: pathify.get('budget/account'),
      categories: pathify.get('budget/categories'),
      items: function() { return this.transactions; },
      keymap: function() { return this.tablemixin_keymap(); },
    },
    watch: {
      account: function() { this.reset(); },
      search: function() { this.refresh(); },
    },
    mounted: function() { this.reset(); },
    methods: {
      // Save
      // Save the current cell value
      save: async function(cell, id, row, field, newvalue, refresh=false) {
        try {
          var change = utils.rset({}, field.replace('.','_'), newvalue);
          var {data} = await api.Budget.patchTransaction(id, change);
          Vue.set(this.items, row, data);
          if (cell) { cell.setStatus('success', 1000); }
          if (refresh) { await this.refresh(); }
          return data;
        } catch(err) {
          if (cell) { cell.setStatus('error'); }
          utils.snackbar(`Error saving transaction.`);
          console.log(err);
        }
      },

      // Refresh
      // Refresh the list of categories displayed
      refresh: async function() {
        this.cancelsearch = api.cancel(this.cancelsearch);
        var token = this.cancelsearch.token;
        try {
          var params = {search: this.search};
          if (this.account) { params.search += ` bank:"${this.account.name}"`; }
          var {data} = await api.Budget.getTransactions(params, token);
          this.transactions = data.results;
          //this.transactions = null;
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        }
      },

      // Reset
      // Reset the page view when switching tabs
      reset: function() {
        this.search = '';
        this.editing = false;
        this.focus = null;
        this.refresh();
      },

    }
  };
</script>

<style lang='scss'>
  #budgettransactions,
  #budgettransactions-loading {
    animation-duration: .6s;
    min-height: calc(70vh - 50px);
    position: relative;
    h1 { margin-bottom:0px; }
    .search {
      width: 400px;
      position: absolute;
      font-weight: bold;
      color: $lightbg-fg3;
      right: 0px;
      border-radius: 20px;
      padding-left: 15px;
    }
    .table-wrapper { margin-top:45px; }

  }
</style>
