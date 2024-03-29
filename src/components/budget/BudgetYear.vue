<template>
  <div id='budgetyear'>
    <PageWrap>
      <div v-if='items' v-hotkey='keymap'>
        <h1>Past Year Spending
          <div class='subtext'>Global view of past years {{count | intcomma}} transactions</div>
        </h1>
        <div id='searchwrap'>
          <b-loading class='is-small' :active='loading' :is-full-page='false'/>
          <b-icon v-if='search' @click.native.prevent='search = ""' icon='close-circle-outline'/>
          <input v-model.lazy='search' ref='search' class='input' icon='magnify'
            placeholder='Filter Transactions' autocomplete='off' spellcheck='false' rounded/>
        </div>
        <div style='clear:both'/>
        <div class='clickout-detector' v-click-outside='cancelAll'>
          <b-table :data='tabledata' narrowed ref='table' tabindex='-1'>
            <template slot-scope='props'>
              <b-table-column v-for='cell in props.row' :key='cell.col.label' :label='cell.col.label' :width='cell.col.width' :numeric='cell.col.numeric' :class='cell.col.cls'>
                <TableCell v-bind='cell' :ref='`c${cell.tabindex}`' @click.native='click($event, cell.tabindex)'/>
              </b-table-column>
            </template>
            <template slot='empty'>No items to display.</template>
          </b-table>
        </div>
      </div>
      <div v-else id='#budgetyear'>
        <h1>Past Year Spending<div class='subtext'>Loading transactions..</div></h1>
        <b-loading active :is-full-page='false'/>
      </div>
    </PageWrap>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as dayjs from 'dayjs';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import {TYPES} from '@/components/TableMixin';
  import BudgetPopover from '@/components/budget/BudgetPopover';
  import PageWrap from '@/components/site/PageWrap';
  import TableMixin from '@/components/TableMixin';
  import trim from 'lodash/trim';
  var TOTAL = {name:'Total', budget:0, meta:{type:TYPES.readonly, cls:'totalrow'}};
  var UNCATEGORIZED = {name:'Uncategorized', budget:0};

  export default {
    name: 'BudgetYear',
    mixins: [TableMixin],
    components: {PageWrap},
    data: () => ({
      cancelsearch: null,   // Cancel search token
      count: 0,             // Total transactions in view
      loading: false,       // True to show loading indicator
      start: null,          // Starting month
      tablerows: null,      // Row items to display
    }),
    computed: {
      categories: pathify.sync('budget/categories'),
      search: pathify.sync('budget/search'),
      view: pathify.sync('budget/view'),
      columns: function() { return this.initColumns(); },
      items: function() { return this.tablerows; },
      keymap: function() { return this.tableMixinKeymap(); },
      months: function() { return this.initMonths(); },
    },
    watch: {
      search: function() {
        this.refresh(true);
      },
    },
    mounted: function() {
      document.title = `PK - Past Year Spending`;
      this.start = dayjs().startOf('month');
      this.search = trim(this.search || this.$route.query.search || '');
      this.refresh();
    },
    methods: {
      // Get Transactions
      // Search for and update the list of displayed transactions
      getTransactions: async function() {
        this.cancelsearch = api.cancel(this.cancelsearch);
        var token = this.cancelsearch.token;
        var mindatestr = this.start.clone().subtract(12, 'months').format('YYYY-MM-DD');
        var params = {search:`${this.search} date>=${mindatestr}`, limit:9999};
        var {data} = await api.Budget.getTransactions(params, token);
        return data.results;
      },

      // Init Columns
      // Initialize table columns
      initColumns: function() {
        var columns = [];
        var opts = {color:true, symbol:'$'};
        columns.push({type:TYPES.readonly, label:'Category', field:'name', width:148});
        for (var i in this.months) {
          var monthstr = this.months[i].format('YYYY-MM');
          var label = i == 0 ? ` ${this.months[i].format('MMM')}` : this.months[i].format('MMM');
          var cls = i == 0 ? 'current' : 'pastmonth';
          columns.push({type:TYPES.popover, label:label, field:`${monthstr}.total`, numeric:true, format:utils.usdint,
            opts:opts, width:64, cls:`${cls} blur`, monthstr:monthstr, popoverComponent:BudgetPopover});
        }
        columns.push({label:'Average', field:'average', numeric:true, format:utils.usdint, opts:opts, width:70, cls:'average blur'});
        columns.push({label:'Total', field:'total', numeric:true, format:utils.usdint, opts:opts, width:70, cls:'totalcol blur'});
        return columns;
      },

      // Init Table Rows
      // Initialize an empty group collection
      initTablerows: function() {
        var tablerows = {};
        var categories = this.categories.slice();  // clone array
        categories.push(UNCATEGORIZED);
        categories.push(TOTAL);
        for (var cat of categories) {
          if (cat.exclude_budget == true) { continue; }
          tablerows[cat.name] = {};
          tablerows[cat.name].name = cat.name;
          tablerows[cat.name].budget = cat.budget;
          tablerows[cat.name].total = 0;
          tablerows[cat.name].average = 0;
          tablerows[cat.name].count = 0;
          if (cat.meta) { tablerows[cat.name].meta = cat.meta; }
          for (var month of this.months) {
            var monthstr = month.format('YYYY-MM');
            tablerows[cat.name][monthstr] = {};
            tablerows[cat.name][monthstr].total = 0;
            tablerows[cat.name][monthstr].items = [];
          }
        }
        return tablerows;
      },

      initMonths: function() {
        var months = [];
        var month = this.start.clone();
        for (var i=0; i<=12; i++) {
          months.push(month.clone());
          month = month.subtract(1, 'month');
        }
        return months;
      },

      // Update Items
      // Update the items to be displayed in the table
      refresh: async function(showLoading=false) {
        this.loading = showLoading;
        try {
          var count = 0;
          var transactions = await this.getTransactions();
          var tablerows = this.initTablerows();
          var categories = Object.keys(tablerows);
          var startstr = this.start.format('YYYY-MM');
          // Pass 1: Add up all the transactions per category and month
          for (var trx of transactions) {
            var month = dayjs(trx.date).startOf('month');
            var monthstr = month.format('YYYY-MM');
            var amount = parseFloat(trx.amount);
            var cat = trx.category || UNCATEGORIZED;
            if (categories.indexOf(cat.name) == -1) { continue; }
            count += 1;
            tablerows[cat.name].count += 1;
            tablerows[cat.name][monthstr].items.push(trx);
            tablerows[cat.name][monthstr].total += amount;
            tablerows[TOTAL.name][monthstr].total += amount;
            if (monthstr != startstr) {
              tablerows[cat.name].total += amount;
              tablerows[TOTAL.name].total += amount;
            }
          }
          // Pass 2: Remove empty rows or calculate the average
          for (var key of Object.keys(tablerows)) {
            if (tablerows[key].total == 0) { delete tablerows[key]; }
            else { tablerows[key].average = tablerows[key].total / 12; }
          }
          this.tablerows = tablerows;
          this.count = count;
          utils.updateHistory(this.$router, {search:this.search});
        } catch(err) {
          if (!api.isCancel(err)) { throw(err); }
        } finally {
          setTimeout(() => this.loading = false, 300);
        }
      },
    }
  };
</script>

<style lang='scss'>
  #budgetyear {
    animation-duration: .6s;
    min-height: calc(70vh - 50px);
    position: relative;
    h1 { margin-bottom:0px; }

    th.current { border-right:1px solid darken($lightbg-bg3, 5%); }
    td.current { border-right:1px solid $lightbg-bg3; }
    th.average { border-left:1px solid darken($lightbg-bg3, 5%); }
    td.average { border-left:1px solid $lightbg-bg3; }
    td.totalrow { font-weight:600; background-color:$lightbg-bg1; }

    #page { max-width:1220px !important; min-width:1220px !important; }
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
  }
</style>
