<template>
  <div id='budgettransactions' v-hotkey='keymap' tabindex='-1'>
    <h1>Budget Transactions
      <div class='subtext'>
        {{account ? account.name : 'All transactions'}}, Showing {{this.transactions.length}} of ??
      </div>
    </h1>
    <div v-click-outside='cancelAll'>
      <b-table :data='tabledata' narrowed>
        <template slot-scope='props'>
          <b-table-column v-for='c in props.row' :key='c.name' :label='c.name' :width='c.width'
            :numeric='c.numeric' :header-class='c.cls' :cell-class='c.cls'>
            <TableCell v-bind='{data:c, focus, editing}' :ref='`c${c.tabindex}`'
              @click.native='clickSetFocus($event, c.tabindex)'/>
          </b-table-column>
        </template>
        <template slot='empty'>No items to display.</template>
      </b-table>
    </div>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import TableMixin from '@/components/TableMixin';

  export default {
    name: 'BudgetTransactions',
    mixins: [TableMixin],
    data: function() {
      return {
        cancelsearch: null,   // Cancel search token
        search: '',           // Current search string
        transactions: {},     // Displayed transactions
        columns: [
          {name:'Name', field:'account.name'},
          {name:'Date', field:'date', width:'100px', editable:true},
          {name:'Payee', field:'payee', editable:true},
          {name:'Category', field:'category.name', width:'200px', editable:true},
          {name:'Amount', field:'amount', display:utils.usd, select:true, numeric:true, editable:true, width:'150px', class:'blur'},
          {name:'X', field:'approved', cls:'check', editable:true},
          {name:'Comment', field:'comment', editable:true},
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
      // account: {immediate:true, handler:function() {
      //   this.resetPage();
      //   this.updateTransactions();
      // }},
    },
    mounted: function() {
      this.refresh();
    },
    methods: {
      // Save
      // Save the current cell value
      // save: async function(cell, id, row, field, newvalue, refresh=false) {
      //   try {
      //     var change = utils.rset({}, field, newvalue);
      //     var {data} = await api.Budget.patchTransaction(id, change);
      //     Vue.set(this.items, row, data);
      //     if (cell) { cell.setStatus('success', 1000); }
      //     if (refresh) { await this.refresh(); }
      //     return data;
      //   } catch(err) {
      //     if (cell) { cell.setStatus('error'); }
      //     utils.snackbar(`Error saving transaction.`);
      //     console.log(err);
      //   }
      // },

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
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        }
      },
    }
  };
</script>
