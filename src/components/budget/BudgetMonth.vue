<template>
  <div id='budgetmonth'>
    <PageWrap>
      <h1>{{month.format('MMMM YYYY')}} Budget
        <div style='float:right'>
          <i class='mdi mdi-chevron-left' @click.prevent='incrementMonth(-1)'/>
          <i class='mdi mdi-chevron-right' @click.prevent='incrementMonth(1)'/>
        </div>
        <div class='subtext'>View {{month.format('MMMM')}} transactions</div>
      </h1>
      <div style='clear:both'/>
      <div class='tablewrap'>
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
    </PageWrap>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as dayjs from 'dayjs';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import * as butils from '@/components/budget/BudgetUtils';
  import {TYPES} from '@/components/TableMixin';
  import BudgetPopover from '@/components/budget/BudgetPopover';
  import PageWrap from '@/components/site/PageWrap';
  import TableMixin from '@/components/TableMixin';

  export default {
    name: 'BudgetMonth',
    mixins: [TableMixin],
    components: {PageWrap},
    data: () => ({
      cancelsearch: null,   // Cancel search token
      count: 0,             // Total transactions in view
      loading: false,       // True to show loading indicator
      month: dayjs(),       // Current month displayed (dayjs object)
      tablerows: null,      // Row items to display
    }),
    computed: {
      categories: pathify.sync('budget/categories'),
      columns: function() { return this.initColumns(); },
      items: function() { return this.tablerows; },
      keymap: function() { return this.tableMixinKeymap(); },
    },
    mounted: function() {
      this.month = dayjs(dayjs().format('YYYY-MM'));
      document.title = `PK - ${this.month.format('MMMM')} Budget`;
      this.refresh();
    },
    methods: {
      // Get Transactions
      // Search for and update the list of displayed transactions
      getTransactions: async function() {
        this.cancelsearch = api.cancel(this.cancelsearch);
        var token = this.cancelsearch.token;
        var datestr = this.month.format('MMM YYYY');
        var params = {search:`date="${datestr}"`, limit:9999};
        var {data} = await api.Budget.getTransactions(params, token);
        return data.results;
      },

      // Increment Month
      // Go to previous or next month
      incrementMonth: function(inc) {
        this.month = this.month.add(inc, 'month');
        this.refresh();
      },

      // Init Columns
      // Initialize table columns
      initColumns: function() {
        var columns = [];
        var opts = {color:true, symbol:'$'};
        columns.push({type:TYPES.readonly, label:'Category', field:'name', width:200});
        columns.push({type:TYPES.readonly, label:'Budget', field:'budget', width:100, opts:opts, numeric:true, format:utils.usdint, cls:'blur'});
        columns.push({type:TYPES.popover, label:'Spent', field:'total', width:100, opts:opts, numeric:true, format:utils.usdint, cls:'blur', popoverComponent:BudgetPopover});
        //columns.push({type:TYPES.readonly, label:'Difference', field:'name', width:148});
        return columns;
      },

      // Init Table Rows
      // Initialize an empty group collection
      initTablerows: function() {
        var tablerows = {};
        var categories = this.categories.slice();  // clone array
        categories.push(butils.UNCATEGORIZED);
        categories.push(butils.TOTAL);
        for (var cat of categories) {
          if (cat.exclude_budget == true) { continue; }
          tablerows[cat.name] = {};
          tablerows[cat.name].name = cat.name;
          tablerows[cat.name].budget = cat.budget;
          tablerows[cat.name].total = 0;
          tablerows[cat.name].average = 0;
          tablerows[cat.name].count = 0;
          tablerows[cat.name].items = [];
          if (cat.meta) { tablerows[cat.name].meta = cat.meta; }
        }
        return tablerows;
      },

      // Refresh
      // Refresh the list of transactions displayed
      refresh: async function(showLoading=false) {
        this.loading = showLoading;
        try {
          var count = 0;
          var transactions = await this.getTransactions();
          var tablerows = this.initTablerows();
          var categories = Object.keys(tablerows);
          // Organize the transactions into their categories
          for (var trx of transactions) {
            var amount = parseFloat(trx.amount);
            var cat = trx.category || butils.UNCATEGORIZED;
            if (categories.indexOf(cat.name) == -1) { continue; }
            count += 1;
            tablerows[cat.name].count += 1;
            tablerows[cat.name].items.push(trx);
            tablerows[cat.name].total += amount;
            tablerows[butils.TOTAL.name].total += amount;
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
  #budgetmonth {
    .tablewrap {
      width: 410px;
    }

    H1 .mdi:hover {
      cursor: pointer;
      background-color: rgba(0,0,0,0.05);
      border-radius: 3px;
    }

  }
</style>
