<template>
  <div id='budgettransactions'>
    <PageWrap>
      <div v-if='items' v-hotkey='keymap'>
        <h1>
          {{account ? account.name : 'All'}} Transactions
          <div class='subtext'>Showing {{this.items.length | intcomma}} of {{this.total | intcomma}} transactions</div>
        </h1>
        <div id='searchwrap'>
          <b-loading class='is-small' :active='loading' :is-full-page='false'/>
          <b-icon v-if='search' @click.native.prevent='search = ""' icon='close-circle-outline'/>
          <input v-model.lazy='search' ref='search' class='input' icon='magnify'
            placeholder='Search Transactions' autocomplete='off' spellcheck='false' rounded/>
          <div class='quicklinks'>
            <a v-if='uncategorized' @click='appendSearch("category:none")'>{{uncategorized | intcomma}} uncategorized</a>
            <a v-if='unapproved' @click='appendSearch("approved=false")'>{{unapproved | intcomma}} unapproved</a>
            <div v-if='!uncategorized && !unapproved' class='uptodate'>✓ You're all caught up!</div>
          </div>
        </div>
        <div style='clear:both'/>
        <div class='clickout-detector' v-click-outside='cancelAll'>
          <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
            <template slot-scope='props'>
              <b-table-column v-for='cell in props.row' :key='cell.label' :label='cell.col.label' :width='cell.col.width' :numeric='cell.col.numeric' :class='cell.col.cls'>
                <TableCell v-bind='cell' :ref='`c${cell.tabindex}`' :key='cell.row.id' @click.native='click($event, cell.tabindex)' @madeChoice='enter'/>
              </b-table-column>
            </template>
            <template slot='empty'>No items to display.</template>
          </b-table>
        </div>
      </div>
      <div v-else id='budgettransactions'>
        <h1>{{account ? account.name : 'All'}}  Transactions<div class='subtext'>Loading transactions..</div></h1>
        <b-loading active :is-full-page='false'/>
      </div>
    </PageWrap>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import {TYPES} from '@/components/TableMixin';
  import PageWrap from '@/components/site/PageWrap';
  import TableMixin from '@/components/TableMixin';
  import trim from 'lodash/trim';

  export default {
    name: 'BudgetTransactions',
    mixins: [TableMixin],
    components: {PageWrap},
    data: () => ({
      cancelsearch: null,   // Cancel search token
      loading: false,       // True to show loading indicator
      transactions: null,   // Displayed transactions
      total: 0,             // Total transactions in current view
      unapproved: 0,        // Total unapproved transactions in current view
      uncategorized: 0,     // Total uncategorized transactions in current view
    }),
    computed: {
      account: pathify.get('budget/account'),
      categories: pathify.get('budget/categories'),
      search: pathify.sync('budget/search'),
      items: function() { return this.transactions; },
      keymap: function() { return this.tableMixinKeymap(); },
      columns: function() { return [
        {label:'Name', field:'account.name', width:68},
        {type:TYPES.editable, label:'Date', field:'date', width:100, reset:true, format:utils.formatDate},
        {type:TYPES.editable, label:'Category', field:'category.name', width:150, select:true, choices:this.categories},
        {type:TYPES.editable, label:'Payee', field:'payee', reset:true, width:250},
        {type:TYPES.editable, label:'Amount', field:'amount', format:utils.usd, opts:{color:true}, select:true, numeric:true, reset:true, width:90, cls:'blur'},
        {type:TYPES.toggle, label:'X', field:'approved', width:26},
        {type:TYPES.editable, label:'Comment', field:'comment', width:180},
      ];},
    },
    watch: {
      account: function() { this.reset(this.search); },
      search: function() { this.refresh(true); },
    },
    mounted: function() {
      var search = trim(this.search || this.$route.query.search || '');
      this.reset(search);
    },
    methods: {
      // Append Search
      // Add the specified text to the search input
      appendSearch: function(text) {
        if (this.search.toLowerCase().includes(text.toLowerCase())) { return; }
        this.search = trim(`${this.search} ${text}`);
      },

      // Save
      // Save the current cell value
      save: async function(id, field, newvalue, cell=null, refresh=false) {
        try {
          var change = utils.rset({}, field.replace('.','_'), newvalue);
          if ('category_name' in change) { change.approved = true; }
          var {data} = await api.Budget.patchTransaction(id, change);
          this.updateItem(id, data);
          if (cell) { cell.setStatus('success', 1000); }
          if (refresh) { await this.refresh(); }
          // Specially track unapproved and uncategorized
          if (field == 'approved' && cell.value && !newvalue) { this.unapproved += 1; }
          if (field == 'approved' && !cell.value && newvalue) { this.unapproved -= 1; }
          if (field == 'category.name' && cell.value && !newvalue) { this.uncategorized += 1; }
          if (field == 'category.name' && !cell.value && newvalue) { this.uncategorized -= 1; }
          return data;
        } catch(err) {
          if (cell) { cell.setStatus('error'); }
          utils.snackbar(`Error saving transaction.`);
          console.log(err);
        }
      },

      // Refresh
      // Refresh the list of transactions displayed
      refresh: async function(showLoading=false) {
        this.loading = showLoading;
        this.cancelsearch = api.cancel(this.cancelsearch);
        var token = this.cancelsearch.token;
        try {
          var params = {search: this.search};
          if (this.account) { params.search += ` bank:"${this.account.name}"`; }
          var {data} = await api.Budget.getTransactions(params, token);
          utils.updateHistory(this.$router, {search:this.search});
          this.total = data.count;
          this.unapproved = data.unapproved;
          this.uncategorized = data.uncategorized;
          this.transactions = data.results;
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        } finally {
          setTimeout(() => this.loading = false, 300);
        }
      },

      // Reset
      // Reset the page view when switching tabs
      reset: function(search='') {
        var accountname = this.account ? this.account.name : 'All';
        document.title =`PK - ${accountname} Transactions`;
        this.getCell().editing = false;
        this.transactions = null;
        this.search = search;
        this.focus = null;
        this.refresh();
      },

    }
  };
</script>

<style lang='scss'>
  #budgettransactions {
    animation-duration: .6s;
    min-height: calc(70vh - 50px);
    position: relative;
    h1 { margin-bottom:0px; }
    #searchwrap {
      position: relative;
      width: 450px;
      float: right;
      margin-bottom: 10px;
      padding-left: 30px;
      .input {
        border-radius: 20px;
        color: $lightbg-fg3;
        font-weight: bold;
        padding: 4px 35px 4px 15px;
      }
      .loading-overlay {
        width: 20px;
        height: 35px;
      }
      .icon {
        color: $lightbg-fg1;
        position: absolute;
        opacity: 0.3;
        top: 6px;
        right: 0px;
        z-index: 10;
        padding-right: 12px;
        cursor: pointer;
        &:hover { opacity:0.5; }
      }
    }
    .quicklinks {
      color:$lightbg-fg4;
      font-size: 12px;
      font-weight: 400;
      padding-right: 10px;
      padding-top: 2px;
      text-align: right;
      a::after { content: ', '; color:$lightbg-fg1; }
      a:last-child:after { content: ''; }
    }
  }
</style>
